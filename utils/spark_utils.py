import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark import SparkContext
from utils.logger import get_logger

logger = get_logger(__name__)

# Racine projet
ROOT = Path(__file__).resolve().parent.parent

# Configuration par défaut
SPARK_APP_NAME = "emargement_spark_app"
SPARK_MASTER = os.getenv("SPARK_MASTER_URL", "local[*]")
SPARK_JDBC_PACKAGES = os.getenv("SPARK_JDBC_PACKAGES", "org.postgresql:postgresql:42.7.3")
SPARK_WAREHOUSE_DIR = os.getenv(
    "SPARK_WAREHOUSE_DIR",
    str((ROOT / "spark-warehouse").resolve()),
)

def _force_cleanup_spark():
    """Nettoyage brutal des singletons Spark en mémoire Python."""
    logger.warning("🧹 Nettoyage forcé des singletons Spark...")
    try:
        if SparkContext._active_spark_context is not None:
            try:
                SparkContext._active_spark_context.stop()
            except:
                pass
        # Suppression des références globales
        SparkContext._active_spark_context = None
        SparkSession._instantiatedSession = None
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage forcé : {e}")

def get_spark_session(app_name: str = SPARK_APP_NAME) -> SparkSession:
    """
    Récupère ou crée une session Spark avec une tolérance aux pannes (contexte arrêté).
    """
    
    # Tentative 1 : Normal
    try:
        builder = (SparkSession.builder
                   .appName(app_name)
                   .master(SPARK_MASTER)
                   .config("spark.sql.warehouse.dir", SPARK_WAREHOUSE_DIR)
                   .config("spark.hadoop.fs.defaultFS", "file:///")
                   .config("spark.sql.adaptive.enabled", "true")
                   .config("spark.sql.adaptive.coalescePartitions.enabled", "true"))

        if SPARK_JDBC_PACKAGES:
            builder = builder.config("spark.jars.packages", SPARK_JDBC_PACKAGES)

        # Si un contexte existe déjà mais qu'il est arrêté, getOrCreate() risque de planter
        if SparkContext._active_spark_context is not None:
            if SparkContext._active_spark_context._jsc is None or SparkContext._active_spark_context._jsc.sc().isStopped():
                _force_cleanup_spark()

        return builder.getOrCreate()

    except Exception as e:
        error_msg = str(e)
        if "stopped SparkContext" in error_msg or "IllegalStateException" in error_msg:
            logger.error("🚨 SparkContext arrêté détecté lors de la création. Tentative de réinitialisation complète...")
            _force_cleanup_spark()
            # Tentative 2 : Après nettoyage
            return builder.getOrCreate()
        else:
            logger.error(f"❌ Erreur critique lors de la création de la session Spark : {e}")
            raise
