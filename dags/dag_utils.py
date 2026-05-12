"""
Shared utilities for Airflow DAGs.
"""
from __future__ import annotations
from datetime import date, timedelta
import sys
from pathlib import Path

# Roots
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jobs.generate import generer_fichiers
from jobs.collect import collecter_feuilles
from jobs.extract import extract_to_bronze
from jobs.transform import transform_to_silver
from jobs.aggregate import aggregate_to_gold
from jobs.business.scoring import run_scoring

def execute_generate(**context):
    execution_date = context["ds"]
    session = context["params"]["session"]
    date_jour = date.fromisoformat(execution_date)
    n_files = generer_fichiers(session, date_jour)
    if n_files == 0:
        print(f"INFO: Aucun fichier généré pour {session} le {execution_date}")
    return f"Génération: {n_files} fichiers"

def execute_collect(**context):
    execution_date = context["ds"]
    session = context["params"]["session"]
    date_jour = date.fromisoformat(execution_date)
    chemins_ok, stats = collecter_feuilles(session, date_jour)
    return f"Collecte: {len(chemins_ok)} fichiers valides"

def execute_extract(**context):
    execution_date = context["ds"]
    session = context["params"]["session"]
    date_jour = date.fromisoformat(execution_date)
    n_files = extract_to_bronze(session, date_jour)
    return f"Extraction: {n_files} fichiers traités"

def execute_transform(**context):
    execution_date = context["ds"]
    session = context["params"]["session"]
    date_jour = date.fromisoformat(execution_date)
    n_records = transform_to_silver(session, date_jour)
    return f"Transformation: {n_records} enregistrements"

def execute_aggregate(**context):
    execution_date = context["ds"]
    session = context["params"]["session"]
    date_jour = date.fromisoformat(execution_date)
    n_records = aggregate_to_gold(session, date_jour)
    return f"Agrégation: {n_records} enregistrements"

def execute_ia_scoring(**context):
    run_scoring()
    return "Scoring mis à jour"
