"""
Phase 7.3 — SCORING : Calcul du score de sérieux des étudiants.
Source : gold.presence_par_etudiant, gold.absences_repetees
Target : gold.scoring_etudiants
"""
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# Racine projet
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from utils.db import get_postgres_dsn, connect_postgres
from utils.logger import get_logger

logger = get_logger(__name__)

def run_scoring():
    conn = connect_postgres()
    try:
        # 1. Calcul du taux de présence global par étudiant
        query_presence = """
            SELECT 
                numero_et,
                COUNT(*) as nb_sessions,
                SUM(CASE WHEN present = True THEN 1 ELSE 0 END) as nb_presents
            FROM gold.presence_par_etudiant
            GROUP BY numero_et
        """
        df_presence = pd.read_sql(query_presence, conn)
        
        # 2. Récupération des pénalités (absences répétées)
        query_absences = """
            SELECT numero_et, COUNT(*) as nb_alertes
            FROM gold.absences_repetees
            GROUP BY numero_et
        """
        df_absences = pd.read_sql(query_absences, conn)

        if df_presence.empty:
            logger.info("Aucune donnée de présence pour le scoring.")
            return

        # Merge
        df_score = pd.merge(df_presence, df_absences, on='numero_et', how='left').fillna(0)
        
        # Formule équilibrée : 70% taux de présence + 30% régularité
        # Chaque alerte d'absence répétée retire 10 points sur la part régularité
        taux_presence = (df_score['nb_presents'] / df_score['nb_sessions']) * 100
        regularite = (30 - (df_score['nb_alertes'] * 10)).clip(0, 30)
        
        df_score['score_serieux'] = (taux_presence * 0.7 + regularite).clip(0, 100)
        
        def get_badge(score):
            if score >= 90: return 'OR'
            if score >= 70: return 'ARGENT'
            if score >= 50: return 'BRONZE'
            return 'SANS BADGE'
        
        df_score['badge'] = df_score['score_serieux'].apply(get_badge)
        
        # Sauvegarde via psycopg2
        results = []
        for _, row in df_score.iterrows():
            results.append((row['numero_et'], float(row['score_serieux']), row['badge']))

        with conn.cursor() as cur:
            cur.execute("TRUNCATE gold.scoring_etudiants")
            query = """
                INSERT INTO gold.scoring_etudiants (numero_et, score_serieux, badge)
                VALUES (%s, %s, %s)
            """
            cur.executemany(query, results)
        conn.commit()
        logger.info(f"Scoring terminé pour {len(results)} étudiants.")

    finally:
        conn.close()

if __name__ == "__main__":
    run_scoring()
