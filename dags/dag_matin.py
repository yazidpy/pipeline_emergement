from __future__ import annotations
# pyrefly: ignore [missing-import]
import pendulum
from datetime import timedelta
# pyrefly: ignore [missing-import]
from airflow.models.dag import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
import sys
from pathlib import Path

# Add dags folder to path for imports
DAGS_DIR = Path(__file__).resolve().parent
if str(DAGS_DIR) not in sys.path:
    sys.path.insert(0, str(DAGS_DIR))

from dag_utils import (
    execute_generate, execute_collect, execute_extract,
    execute_transform, execute_aggregate, execute_ia_scoring
)

default_args = {
    "owner": "emargement_team",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="emargement_matin",
    default_args=default_args,
    schedule_interval="0 7 * * 1-5",  # 07h00 Lun-Ven
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["emargement", "morning"],
    params={"session": "matin"},
    description="Pipeline Émargement - Session Matin"
) as dag:

    task_generate = PythonOperator(
        task_id="generate_matin",
        python_callable=execute_generate,
    )

    task_collect = PythonOperator(
        task_id="collect_matin",
        python_callable=execute_collect,
    )

    task_extract = PythonOperator(
        task_id="extract_matin",
        python_callable=execute_extract,
    )

    task_transform = PythonOperator(
        task_id="transform_matin",
        python_callable=execute_transform,
    )

    task_aggregate = PythonOperator(
        task_id="aggregate_matin",
        python_callable=execute_aggregate,
    )

    task_scoring = PythonOperator(
        task_id="ia_scoring_matin",
        python_callable=execute_ia_scoring,
    )

    task_generate >> task_collect >> task_extract >> task_transform >> task_aggregate
    task_aggregate >> task_scoring
