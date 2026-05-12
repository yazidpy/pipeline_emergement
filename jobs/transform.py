"""
Phase 4 - TRANSFORM (PySpark) : Nettoyage et enrichissement bronze.emargement_raw vers silver.emargement_clean.
Input : bronze.emargement_raw (données brutes des fichiers Excel)
Output : silver.emargement_clean (données validées, enrichies avec ref.*)
"""
from __future__ import annotations

import os
import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Racine projet (parent de jobs/)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if (ROOT / ".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lit, when, trim, upper, lower, concat, regexp_extract,
    to_date, coalesce, broadcast
)
from pyspark.sql.types import (
    StringType, DateType, BooleanType, TimestampType,
    StructType, StructField
)

from utils.db import connect_postgres
from utils.logger import get_logger
from utils.spark_utils import get_spark_session

logger = get_logger(__name__)

# Configuration Spark déplacée dans utils/spark_utils.py
SPARK_APP_NAME = "emargement_transform"

# Mapping des valeurs de présence vers booléen
PRESENCE_MAPPING = {
    "O": True, "OUI": True, "YES": True, "1": True, "X": True,
    "N": False, "NON": False, "NO": False, "0": False, "": None, None: None
}


def create_spark_session() -> SparkSession:
    """Crée une session Spark via l'utilitaire centralisé"""
    return get_spark_session(SPARK_APP_NAME)


def load_reference_data(spark: SparkSession) -> dict:
    """Charge les tables de référence depuis PostgreSQL"""
    import os
    
    postgres_url = f"jdbc:postgresql://{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'emargement')}"
    postgres_properties = {
        "user": os.getenv('POSTGRES_USER', 'emargement'),
        "password": os.getenv('POSTGRES_PASSWORD', 'emargement'),
        "driver": "org.postgresql.Driver"
    }
    
    reference_data = {}
    
    try:
        # Chargement des formations
        df_formations = spark.read.jdbc(
            url=postgres_url, table="ref.formation", properties=postgres_properties
        )
        
        # Chargement des étudiants + Jointure avec formation
        df_et_raw = spark.read.jdbc(
            url=postgres_url, table="ref.etudiant", properties=postgres_properties
        )
        
        reference_data['etudiants'] = (df_et_raw.join(
                broadcast(df_formations),
                df_et_raw["formation_id"] == df_formations["id"],
                "left"
            )
            .select(
                df_et_raw["*"],
                df_formations["intitule"].alias("filiere"),
                df_formations["niveau"].alias("niveau_form")
            )
            .withColumn("nom_upper", upper(col("nom")))
            .withColumn("prenom_upper", upper(col("prenom"))))
        
        # Chargement des cours
        reference_data['cours'] = spark.read.jdbc(
            url=postgres_url, table="ref.cours", properties=postgres_properties
        )
        
        logger.info("Tables de référence chargées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur chargement tables de référence: {e}")
        raise
    
    return reference_data


def normalize_presence_value(present_col):
    """Normalise les valeurs de présence vers booléen"""
    # Nettoyage et mise en majuscule
    cleaned = upper(trim(col(present_col)))
    
    # Mapping vers booléen
    result = when(cleaned.isin("O", "OUI", "YES", "1", "X"), lit(True)) \
             .when(cleaned.isin("N", "NON", "NO", "0"), lit(False)) \
             .otherwise(lit(None))
    
    return result


def match_student_with_reference(df_bronze, df_etudiants):
    """Fait le matching entre les données bronze et la table étudiante"""
    
    # Normalisation des noms pour le matching
    df_bronze_clean = df_bronze.withColumn("nom_upper", upper(trim(col("etudiant_nom")))) \
                               .withColumn("prenom_upper", upper(trim(col("etudiant_prenom"))))
    
    # Jointure par nom et prénom (broadcast pour optimisation)
    df_matched = df_bronze_clean.join(
        broadcast(df_etudiants),
        (df_bronze_clean["nom_upper"] == df_etudiants["nom_upper"]) &
        (df_bronze_clean["prenom_upper"] == df_etudiants["prenom_upper"]),
        "left"
    )
    
    # Sélection et renommage des colonnes
    df_result = df_matched.select(
        col("date_jour"),
        col("session"),
        col("cours_id").cast("int"),
        col("numero_et"),
        concat(col("etudiant_nom"), lit(" "), col("etudiant_prenom")).alias("nom_complet"),
        col("filiere"),
        col("niveau_form").alias("niveau"),
        normalize_presence_value("present").alias("present"),
        col("present").alias("present_raw"),  # Conserver la valeur originale
        col("remarque"),
        col("fichier_source"),
        lit(datetime.now()).alias("cleaned_at")
    )
    
    return df_result


def validate_and_filter_data(df_silver):
    """Validation et filtrage des données transformées"""
    
    # Filtrage des lignes sans étudiant matché
    df_valid = df_silver.filter(col("numero_et").isNotNull())
    
    # Validation de l'intégrité référentielle (cours_id doit exister)
    # Note: Cette validation se fera via jointure avec ref.cours
    
    logger.info(f"Filtrage: {df_silver.count()} -> {df_valid.count()} lignes valides")
    
    return df_valid


def transform_to_silver(
    session: str,
    date_jour: date
) -> int:
    """Transforme les données bronze vers silver.emargement_clean"""
    
    # Création session Spark
    spark = create_spark_session()
    
    try:
        import os
        
        # Configuration PostgreSQL JDBC
        postgres_url = f"jdbc:postgresql://{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'emargement')}"
        postgres_properties = {
            "user": os.getenv('POSTGRES_USER', 'emargement'),
            "password": os.getenv('POSTGRES_PASSWORD', 'emargement'),
            "driver": "org.postgresql.Driver"
        }
        
        # Chargement des données bronze pour la date/session
        logger.info(f"Chargement données bronze pour {date_jour} {session}")
        
        df_bronze = (spark.read
            .jdbc(url=postgres_url, table="bronze.emargement_raw", properties=postgres_properties)
            .filter((col("date_jour") == lit(date_jour)) & 
                   (col("session") == lit(session))))
        
        # Déduplication (Spécification PDF section 4.5.3)
        df_bronze = df_bronze.dropDuplicates([
            "date_jour", "session", "cours_id", "etudiant_nom", "etudiant_prenom"
        ])
        
        bronze_count = df_bronze.count()
        if bronze_count == 0:
            logger.warning(f"Aucune donnée bronze trouvée pour {date_jour} {session}")
            return 0
        
        logger.info(f"Chargement de {bronze_count} lignes bronze")
        
        # Chargement des données de référence
        reference_data = load_reference_data(spark)
        
        # Transformation: matching avec les étudiants
        df_transformed = match_student_with_reference(df_bronze, reference_data['etudiants'])
        
        # Validation et filtrage
        df_valid = validate_and_filter_data(df_transformed)
        
        # Jointure avec ref.cours pour valider cours_id
        df_final = df_valid.join(
            broadcast(reference_data['cours']),
            df_valid["cours_id"] == reference_data['cours']["id"],
            "inner"
        ).select(df_valid["*"])  # Garde seulement les colonnes de silver
        
        valid_count = df_final.count()
        if valid_count == 0:
            logger.warning("Aucune donnée valide après transformation")
            return 0
        
        # Écriture vers silver.emargement_clean
        logger.info(f"Écriture de {valid_count} lignes vers silver.emargement_clean")
        
        # Suppression des données existantes pour cette date/session (upsert) via psycopg2
        logger.info(f"Nettoyage des anciennes données silver pour {date_jour} {session}")
        with connect_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM silver.emargement_clean WHERE date_jour = %s AND session = %s",
                    (date_jour, session)
                )
            conn.commit()
        
        # Insertion des nouvelles données
        df_final.write.jdbc(
            url=postgres_url,
            table="silver.emargement_clean",
            mode="append",
            properties=postgres_properties
        )
        
        logger.info(f"TRANSFORM terminé: {valid_count}/{bronze_count} lignes valides")
        return valid_count
        
    except Exception as e:
        logger.error(f"Erreur lors de la transformation: {e}")
        return 0



def parse_date(s: str | None) -> date:
    if not s:
        return date.today()
    return datetime.strptime(s, "%Y-%m-%d").date()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Phase 4 - Transform: bronze vers silver.emargement_clean")
    p.add_argument(
        "--session",
        required=True,
        choices=["matin", "apres-midi"],
        help="matin ou apres-midi"
    )
    p.add_argument(
        "--date",
        default=None,
        help="Date au format YYYY-MM-DD (défaut : jour courant)"
    )
    args = p.parse_args(argv)
    
    date_jour = parse_date(args.date)
    
    try:
        n_records = transform_to_silver(args.session, date_jour)
        return 0 if n_records > 0 else 1
    except Exception:
        logger.exception("Échec TRANSFORM")
        return 1


if __name__ == "__main__":
    sys.exit(main())