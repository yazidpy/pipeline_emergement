import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.db import connect_postgres
from jobs.collect import collecter_feuilles
from jobs.extract import extract_to_bronze_pandas
from jobs.transform import transform_to_silver
from jobs.aggregate import aggregate_to_gold
from jobs.business.scoring import run_scoring
from jobs.generate import JOURS_FR, CoursPlanifie, nom_fichier_xlsx

def get_teacher_info(numero_ens):
    try:
        with connect_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nom, prenom FROM ref.enseignant WHERE numero_ens = %s", (numero_ens,))
                return cur.fetchone()
    except: return None

def check_if_processed(cours_id, date_jour, session_name):
    try:
        with connect_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM gold.presence_par_cours WHERE cours_id = %s AND date_jour = %s AND session = %s",
                    (cours_id, date_jour, session_name)
                )
                return cur.fetchone() is not None
    except: return False

def trigger_pipeline(date_jour, session):
    with st.status(f"🔄 Traitement des données...", expanded=False) as status:
        collecter_feuilles(session, date_jour)
        extract_to_bronze_pandas(session, date_jour)
        transform_to_silver(session, date_jour)
        aggregate_to_gold(session, date_jour)
        run_scoring()
        status.update(label="✅ Traitement terminé !", state="complete")

def get_sessions_from_schedule(numero_ens, start_date, end_date):
    sql = """
        SELECT c.id, c.intitule, c.section, c.horaire, c.session, p.jour_semaine, 
               p.heure_debut, p.heure_fin, e.nom, e.prenom, p.salle, f.intitule, f.niveau
        FROM ref.cours c
        JOIN ref.planning p ON c.id = p.cours_id
        JOIN ref.enseignant e ON c.enseignant_id = e.numero_ens
        JOIN ref.formation f ON c.formation_id = f.id
        WHERE e.numero_ens = %s
    """
    sessions = []
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent
    
    with connect_postgres() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (numero_ens,))
            rows = cur.fetchall()
            for r in rows:
                target_weekday = JOURS_FR.index(r[5].capitalize())
                curr = start_date
                while curr <= end_date:
                    if curr.weekday() == target_weekday:
                        cp = CoursPlanifie(r[0], numero_ens, r[1], r[2], r[3], r[4], r[6], r[7], r[8], r[9], r[10], r[11], r[12])
                        fname = nom_fichier_xlsx(cp)
                        gen_path = ROOT / "data" / "generated" / curr.isoformat() / r[4] / fname
                        coll_path = ROOT / "data" / "collected" / curr.isoformat() / r[4] / fname
                        
                        is_generated = gen_path.exists()
                        is_collected = coll_path.exists()
                        is_processed = check_if_processed(r[0], curr, r[4])
                        
                        status_label = "À générer"
                        status_class = "badge-generate"
                        status_icon = "fa-file-circle-plus"
                        
                        if is_processed or is_collected:
                            status_label, status_class, status_icon = "Traité", "badge-done", "fa-circle-check"
                        elif is_generated:
                            status_label, status_class, status_icon = "À remplir", "badge-fill", "fa-file-signature"
                        elif curr < date.today():
                            status_label, status_class, status_icon = "Non traité", "badge-error", "fa-circle-xmark"

                        sessions.append({
                            "date": curr, "session": r[4], "intitule": r[1], "formation": r[11], "niveau": r[12],
                            "filename": fname, "cours_id": r[0], "is_generated": is_generated,
                            "generated_path": gen_path, "collected_path": coll_path,
                            "status_label": status_label, "status_class": status_class, "status_icon": status_icon,
                            "salle": r[10] or "N/A"
                        })
                    curr += timedelta(days=1)
    return sessions