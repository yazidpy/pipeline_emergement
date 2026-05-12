"""
Phase 5 - AGGREGATE (PySpark) : Calculs agrégés depuis silver.emargement_clean vers tables gold.
Input : silver.emargement_clean (données nettoyées)
Output : gold.presence_par_cours, gold.presence_par_etudiant, gold.absences_repetees
"""
from __future__ import annotations

import os
import argparse
import sys
from datetime import date, datetime, timedelta
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
    col, lit, count, sum, when, avg, round, max, min,
    row_number, dense_rank, lag, lead, coalesce, desc, asc, dayofweek
)
from pyspark.sql.window import Window
from pyspark.sql.types import (
    IntegerType, DecimalType, DateType, TimestampType
)

from utils.db import connect_postgres
from utils.logger import get_logger
from utils.spark_utils import get_spark_session

logger = get_logger(__name__)

# Configuration Spark déplacée dans utils/spark_utils.py
SPARK_APP_NAME = "emargement_aggregate"

# Seuils pour les alertes
ABSENCE_THRESHOLD = 3  # Nombre d'absences consécutives pour alerte


def create_spark_session() -> SparkSession:
    """Crée une session Spark via l'utilitaire centralisé"""
    return get_spark_session(SPARK_APP_NAME)


def aggregate_presence_par_cours(df_silver):
    """Calcule les statistiques de présence par cours"""
    
    # Agrégation par cours, date, session
    df_cours_stats = (df_silver
        .groupBy("cours_id", "date_jour", "session")
        .agg(
            count("*").alias("nb_inscrits"),
            sum(when(col("present") == True, 1).otherwise(0)).alias("nb_presents")
        )
        .withColumn("taux_presence", 
                   round(col("nb_presents") * 100.0 / col("nb_inscrits"), 2))
        .withColumn("computed_at", lit(datetime.now()))
    )
    
    return df_cours_stats


def aggregate_presence_par_etudiant(df_silver):
    """Calcule les statistiques de présence par étudiant"""
    
    # Sélection des colonnes pertinentes pour gold.presence_par_etudiant
    df_etudiant_stats = df_silver.select(
        "numero_et", "date_jour", "session", "cours_id", "present", 
        "filiere", "niveau"
    ).withColumn("computed_at", lit(datetime.now()))
    
    return df_etudiant_stats


def detect_absences_repetees(df_silver, threshold: int = ABSENCE_THRESHOLD):
    """Détecte les absences répétées par étudiant (simplifié: nb absences recentes)"""
    
    # Filtrer les absences seulement
    df_absences = df_silver.filter(col("present") == False)
    
    # Agrégation simple: compter les absences par étudiant sur la période
    df_absences_count = (df_absences
        .groupBy("numero_et", "date_jour")
        .agg(count("*").alias("nb_abs_cours"))
    )
    
    # Window pour cumuler les absences sur les 7 derniers jours glissants
    window_etudiant = Window.partitionBy("numero_et").orderBy("date_jour").rowsBetween(-6, 0)
    
    df_cumul = (df_absences_count
        .withColumn("nb_absences_consecutives", sum("nb_abs_cours").over(window_etudiant))
        .filter(col("nb_absences_consecutives") >= threshold)
        .select(
            "numero_et", "date_jour", "nb_absences_consecutives",
            lit(threshold).alias("seuil"),
            lit(datetime.now()).alias("flagged_at")
        )
        .distinct()
    )
    
    return df_cumul


def aggregate_to_gold(
    session: str,
    date_jour: date
) -> int:
    """Agrège les données silver vers les tables gold"""
    
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
        
        # Chargement des données silver pour la date/session
        logger.info(f"Chargement données silver pour {date_jour} {session}")
        
        df_silver = (spark.read
            .jdbc(url=postgres_url, table="silver.emargement_clean", properties=postgres_properties)
            .filter((col("date_jour") == lit(date_jour)) & 
                   (col("session") == lit(session))))
        
        silver_count = df_silver.count()
        if silver_count == 0:
            logger.warning(f"Aucune donnée silver trouvée pour {date_jour} {session}")
            return 0
        
        logger.info(f"Chargement de {silver_count} lignes silver")
        
        # Pour les absences répétées, on a besoin des données historiques
        # On charge les 30 derniers jours pour détecter les séquences
        start_date = date_jour - timedelta(days=30)
        df_historique = (spark.read
            .jdbc(url=postgres_url, table="silver.emargement_clean", properties=postgres_properties)
            .filter(col("date_jour") >= lit(start_date)))
        
        # 1. Agrégation présence par cours
        logger.info("Calcul présence par cours...")
        df_cours_stats = aggregate_presence_par_cours(df_silver)
        
        # 2. Agrégation présence par étudiant
        logger.info("Calcul présence par étudiant...")
        df_etudiant_stats = aggregate_presence_par_etudiant(df_silver)
        
        # 3. Détection absences répétées
        logger.info("Détection absences répétées...")
        df_absences_alertes = detect_absences_repetees(df_historique)
        
        # Écriture vers les tables gold via Upsert (PSQL Cleanup + Spark Append)
        logger.info(f"Nettoyage des tables Gold pour {date_jour} {session}")
        with connect_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM gold.presence_par_cours WHERE date_jour = %s AND session = %s", (date_jour, session))
                cur.execute("DELETE FROM gold.presence_par_etudiant WHERE date_jour = %s AND session = %s", (date_jour, session))
                cur.execute("DELETE FROM gold.absences_repetees WHERE date_jour = %s", (date_jour,))
            conn.commit()

        total_written = 0
        
        # gold.presence_par_cours
        if df_cours_stats.count() > 0:
            logger.info(f"Écriture de {df_cours_stats.count()} lignes vers gold.presence_par_cours")
            df_cours_stats.write.jdbc(url=postgres_url, table="gold.presence_par_cours", mode="append", properties=postgres_properties)
            total_written += df_cours_stats.count()
        
        # gold.presence_par_etudiant
        if df_etudiant_stats.count() > 0:
            logger.info(f"Écriture de {df_etudiant_stats.count()} lignes vers gold.presence_par_etudiant")
            df_etudiant_stats.write.jdbc(url=postgres_url, table="gold.presence_par_etudiant", mode="append", properties=postgres_properties)
            total_written += df_etudiant_stats.count()
        
        # gold.absences_repetees
        if df_absences_alertes.count() > 0:
            logger.info(f"Écriture de {df_absences_alertes.count()} alertes vers gold.absences_repetees")
            df_absences_alertes.write.jdbc(url=postgres_url, table="gold.absences_repetees", mode="append", properties=postgres_properties)
            total_written += df_absences_alertes.count()
        
        logger.info(f"AGGREGATE terminé: {total_written} lignes écrites dans les tables gold")
        return total_written
        
    except Exception as e:
        logger.error(f"Erreur lors de l'agrégation: {e}")
        return 0



def parse_date(s: str | None) -> date:
    if not s:
        return date.today()
    return datetime.strptime(s, "%Y-%m-%d").date()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Phase 5 - Aggregate: silver vers tables gold")
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
        n_records = aggregate_to_gold(args.session, date_jour)
        return 0 if n_records > 0 else 1
    except Exception:
        logger.exception("Échec AGGREGATE")
        return 1


if __name__ == "__main__":
    sys.exit(main())