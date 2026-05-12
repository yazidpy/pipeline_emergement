"""
Phase 3 - EXTRACT (PySpark) : Lecture des feuilles Excel collectées vers bronze.emargement_raw.
Input : data/collected/YYYY-MM-DD/<session>/*.xlsx (validés par collect.py)
Output : bronze.emargement_raw (une ligne par étudiant par cours)
"""
from __future__ import annotations
import os
import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Tuple

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
from pyspark.sql.functions import col, lit, input_file_name
from pyspark.sql.types import (
    StringType, DateType, BooleanType, TimestampType,
    StructType, StructField, IntegerType
)

from psycopg2.extras import execute_values

from utils.db import connect_postgres
from utils.logger import get_logger
from utils.spark_utils import get_spark_session

logger = get_logger(__name__)

# Configuration Spark déplacée dans utils/spark_utils.py
SPARK_APP_NAME = "emargement_extract"
# Schéma de la table bronze.emargement_raw
BRONZE_SCHEMA = StructType([
    StructField("date_jour", DateType(), False),
    StructField("session", StringType(), False),
    StructField("cours_id", IntegerType(), False),  # Extracted from filename
    StructField("etudiant_nom", StringType(), True),
    StructField("etudiant_prenom", StringType(), True),
    StructField("present", StringType(), True),
    StructField("remarque", StringType(), True),
    StructField("fichier_source", StringType(), True),
    StructField("ingested_at", TimestampType(), False),
])


def extract_cours_id_from_filename(filename: str) -> Optional[int]:
    """Extrait l'ID du cours depuis le nom de fichier format: *_cours<id>.xlsx"""
    try:
        # Cherche le pattern "_cours<number>.xlsx"
        import re
        match = re.search(r'_cours(\d+)\.xlsx$', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def create_spark_session() -> SparkSession:
    """Crée une session Spark via l'utilitaire centralisé"""
    return get_spark_session(SPARK_APP_NAME)


def read_excel_file(spark: SparkSession, file_path: Path, date_jour: date, session: str):
    """Lit un fichier Excel et retourne un DataFrame Spark"""
    try:
        # Utilise pandas pour lire Excel puis convertit en Spark DataFrame
        import pandas as pd
        
        # Lecture du fichier Excel avec pandas
        df_pandas = pd.read_excel(str(file_path), header=6)  # Ligne 7 = header (index 6)
        
        # Nettoyage des colonnes
        df_pandas.columns = [
            'numero_et', 'nom', 'prenom', 'present', 'remarque'
        ]
        
        # Suppression des lignes vides
        df_pandas = df_pandas.dropna(subset=['nom', 'prenom'])
        
        # Validation stricte (Sécurité Backend)
        invalid_mask = ~df_pandas['present'].astype(str).str.strip().str.upper().isin(['O', 'N'])
        if invalid_mask.any():
            logger.error(f"❌ FICHIER REJETÉ (Backend) : {file_path.name} contient des valeurs de présence invalides.")
            return None
        
        # Création du Spark DataFrame
        df_spark = spark.createDataFrame(df_pandas)
        
        # Ajout des métadonnées
        cours_id = extract_cours_id_from_filename(file_path.name)
        if cours_id is None:
            logger.warning(f"Impossible d'extraire cours_id du fichier: {file_path.name}")
            return None
            
        df_spark = (df_spark
                   .withColumn("date_jour", lit(date_jour))
                   .withColumn("session", lit(session))
                   .withColumn("cours_id", lit(cours_id).cast(IntegerType()))
                   .withColumn("fichier_source", lit(str(file_path.name)))
                   .withColumn("ingested_at", lit(datetime.now())))
        
        # Sélection des colonnes selon le schéma bronze
        df_spark = df_spark.select([
            "date_jour", "session", "cours_id",
            "nom", "prenom", "present", "remarque",
            "fichier_source", "ingested_at"
        ]).withColumnRenamed("nom", "etudiant_nom") \
         .withColumnRenamed("prenom", "etudiant_prenom")
         
         
        return df_spark
        
    except Exception as e:
        logger.error(f"Erreur lecture fichier {file_path}: {e}")
        return None


def extract_to_bronze(
    session: str,
    date_jour: date,
    base_collected: Optional[Path] = None
) -> int:
    """Extrait les données Excel vers la table bronze.emargement_raw"""
    
    # Chemin des fichiers collectés
    base = base_collected or (ROOT / "data" / "collected")
    collected_dir = base / date_jour.isoformat() / session
    
    if not collected_dir.exists():
        logger.warning(f"Dossier collected inexistant: {collected_dir}")
        return 0
    
    # Fichiers Excel à traiter
    excel_files = list(collected_dir.glob("*.xlsx"))
    if not excel_files:
        logger.warning(f"Aucun fichier Excel trouvé dans: {collected_dir}")
        return 0
    
    logger.info(f"Traitement de {len(excel_files)} fichiers Excel")
    
    # Création session Spark
    spark = create_spark_session()
    
    try:
        all_dataframes = []
        
        # Traitement de chaque fichier
        for file_path in excel_files:
            logger.info(f"Lecture fichier: {file_path.name}")
            df = read_excel_file(spark, file_path, date_jour, session)
            if df is not None and df.count() > 0:
                all_dataframes.append(df)
                logger.info(f"  -> {df.count()} lignes extraites")
        
        if not all_dataframes:
            logger.warning("Aucune donnée extraite des fichiers")
            return 0
        
        # Union de tous les DataFrames
        df_final = all_dataframes[0]
        for df in all_dataframes[1:]:
            df_final = df_final.union(df)
        
        # Écriture vers PostgreSQL (bronze.emargement_raw)
        logger.info(f"Écriture de {df_final.count()} lignes vers bronze.emargement_raw")
        
        # Configuration PostgreSQL JDBC
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_db = os.getenv("POSTGRES_DB", "emargement")

        postgres_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"
        postgres_properties = {
            "user": os.getenv("POSTGRES_USER", "emargement"),
            "password": os.getenv("POSTGRES_PASSWORD", "emargement"),
            "driver": "org.postgresql.Driver"
        }
            
        # Écriture en mode append (pour conserver l'historique)
        df_final.write.jdbc(
            url=postgres_url,
            table="bronze.emargement_raw",
            mode="append",
            properties=postgres_properties
        )
        
        logger.info(f"EXTRACT terminé: {len(all_dataframes)} fichiers traités")
        return len(all_dataframes)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction: {e}")
        return 0


def extract_to_bronze_pandas(
    session: str,
    date_jour: date,
    base_collected: Optional[Path] = None
) -> int:
    """Fallback sans Spark : pandas -> PostgreSQL (bronze.emargement_raw)."""
    import pandas as pd

    base = base_collected or (ROOT / "data" / "collected")
    collected_dir = base / date_jour.isoformat() / session

    if not collected_dir.exists():
        logger.warning(f"Dossier collected inexistant: {collected_dir}")
        return 0

    excel_files = list(collected_dir.glob("*.xlsx"))
    if not excel_files:
        logger.warning(f"Aucun fichier Excel trouvé dans: {collected_dir}")
        return 0

    rows: List[Tuple] = []
    for file_path in excel_files:
        logger.info(f"Lecture fichier (pandas): {file_path.name}")
        try:
            df = pd.read_excel(str(file_path), header=6)
        except Exception as e:
            logger.error(f"Erreur lecture fichier {file_path}: {e}")
            continue

        df.columns = [
            "numero_et", "nom", "prenom", "present", "remarque"
        ]
        df = df.dropna(subset=["nom", "prenom"])

        # Validation stricte (Sécurité Backend / fallback pandas)
        invalid_mask = ~df['present'].astype(str).str.strip().str.upper().isin(['O', 'N'])
        if invalid_mask.any():
            logger.error(f"❌ FICHIER REJETÉ (Pandas Backend) : {file_path.name} contient des valeurs invalides.")
            continue

        cours_id = extract_cours_id_from_filename(file_path.name)
        if cours_id is None:
            logger.warning(f"Impossible d'extraire cours_id du fichier: {file_path.name}")
            continue

        for _, r in df.iterrows():
            rows.append((
                date_jour,
                session,
                int(cours_id),
                str(r.get("nom") or ""),
                str(r.get("prenom") or ""),
                None if pd.isna(r.get("present")) else str(r.get("present")),
                None if pd.isna(r.get("remarque")) else str(r.get("remarque")),
                file_path.name,
            ))

    if not rows:
        logger.warning("Aucune ligne valide à insérer (pandas)")
        return 0

    insert_sql = """
        INSERT INTO bronze.emargement_raw (
            date_jour, session, cours_id,
            etudiant_nom, etudiant_prenom, present,
            remarque, fichier_source
        )
        VALUES %s
    """

    with connect_postgres() as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, rows)
        conn.commit()

    logger.info(f"EXTRACT (pandas) terminé: {len(excel_files)} fichiers, {len(rows)} lignes")
    return len(excel_files)


def parse_date(s: str | None) -> date:
    if not s:
        return date.today()
    return datetime.strptime(s, "%Y-%m-%d").date()


def main(argv: List[str] | None = None) -> int:
    import os
    
    p = argparse.ArgumentParser(description="Phase 3 - Extract: Excel vers bronze.emargement_raw")
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
    p.add_argument(
        "--engine",
        default="spark",
        choices=["spark", "pandas"],
        help="Moteur d'extraction: spark (défaut) ou pandas (fallback)",
    )
    args = p.parse_args(argv)
    
    date_jour = parse_date(args.date)
    
    try:
        if args.engine == "pandas":
            n_files = extract_to_bronze_pandas(args.session, date_jour)
        else:
            n_files = extract_to_bronze(args.session, date_jour)
        return 0 if n_files > 0 else 1
    except Exception:
        logger.exception("Échec EXTRACT")
        return 1


if __name__ == "__main__":
    sys.exit(main())
