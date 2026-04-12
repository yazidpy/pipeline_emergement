import os
from typing import Any, Dict

import psycopg2
from psycopg2.extensions import connection as PgConnection


def get_postgres_dsn() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "emargement")
    user = os.getenv("POSTGRES_USER", "emargement")
    password = os.getenv("POSTGRES_PASSWORD", "emargement")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_postgres_connect_kwargs() -> Dict[str, Any]:
    # Host "postgres" = service Docker ; depuis l’hôte Windows : 127.0.0.1 + port publié (ex. 5433).
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "emargement"),
        "user": os.getenv("POSTGRES_USER", "emargement"),
        "password": os.getenv("POSTGRES_PASSWORD", "emargement"),
    }


def connect_postgres() -> PgConnection:
    return psycopg2.connect(**get_postgres_connect_kwargs())


def get_airflow_sqlalchemy_conn() -> str:
    # Airflow reads this from env as well; helper for consistency.
    return os.getenv("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN", "")
