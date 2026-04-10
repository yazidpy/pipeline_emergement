import os


def get_postgres_dsn() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "emargement")
    user = os.getenv("POSTGRES_USER", "emargement")
    password = os.getenv("POSTGRES_PASSWORD", "emargement")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_airflow_sqlalchemy_conn() -> str:
    # Airflow reads this from env as well; helper for consistency.
    return os.getenv("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN", "")
