"""
Portail Enseignant - GoldenCollar Émargement
Version : Génération à la demande (On-demand)
"""
import os
import sys
import re
import io
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

# Configuration Racine
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils.db import connect_postgres

# --- IMPORTS PIPELINE & GENERATION ---
from jobs.collect import collecter_feuilles
from jobs.extract import extract_to_bronze_pandas
from jobs.transform import transform_to_silver
from jobs.aggregate import aggregate_to_gold
# pyrefly: ignore [missing-import]
from jobs.business.scoring import run_scoring
from jobs.generate import (
    fetch_inscrits, 
    build_workbook, 
    nom_fichier_xlsx, 
    CoursPlanifie,
    JOURS_FR
)

# Configuration Page
st.set_page_config(
    page_title="Portail Enseignant - SmartAcademy",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PROFESSIONNEL (Parité Admin) ---
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #f8fafc; }
    .stApp { background-color: #f8fafc; }
    
    /* Header professionnel */
    .app-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title { margin: 0; font-size: 1.25rem; font-weight: 700; }
    .header-subtitle { margin: 0; opacity: 0.8; font-size: 0.8rem; }

    /* Login Card */
    .login-container {
        max-width: 450px;
        margin: 80px auto;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    /* Session Cards */
    .session-card {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .session-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Badges Pro */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        gap: 0.5rem;
    }
    /* État 1 : À générer (Rouge) */
    .badge-generate { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; }
    /* État 2 : À remplir (Jaune/Orange) */
    .badge-fill { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    /* État 3 : Traité (Vert) */
    .badge-done { background: #dcfce7; color: #16a34a; border: 1px solid #bcf0da; }
    /* État 4 : Non traité (Rouge vif pour historique) */
    .badge-error { background: #fee2e2; color: #b91c1c; border: 1px solid #f87171; }
    
    /* Boutons personnalisés */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Bouton Download spécial (Vert) */
    div.stDownloadButton > button {
        background-color: #22c55e !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #16a34a !important;
        transform: translateY(-1px);
    }

    /* Nettoyage File Uploader (Éliminer le double texte) */
    [data-testid="stFileUploader"] {
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        background-color: transparent !important;
    }
    [data-testid="stFileUploader"] label {
        display: none !important; /* Supprime le label dupliqué */
    }
    [data-testid="stFileUploadDropzone"] {
        border: 1px dashed #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        background: #f8fafc !important;
    }
    [data-testid="stFileUploadDropzone"] div div span {
        font-size: 0.8rem !important;
        color: #64748b !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px;
        background-color: #f1f5f9;
        padding: 0.5rem;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        border: none;
        padding: 8px 20px !important;
        color: #64748b !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1e3a5f !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Tableaux */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }

    /* Scrollable History Table Container */
    .history-table-container {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background: white;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

import subprocess

def trigger_pipeline(date_jour: date, session: str):
    """Déclenche le DAG Airflow correspondant au lieu d'exécuter localement."""
    dag_id = "emargement_matin" if session == "matin" else "emargement_apresmidi"
    
    with st.status(f"🚀 Déclenchement du pipeline Airflow ({dag_id})...", expanded=True) as status:
        try:
            # Commande Airflow pour déclencher le DAG pour une date spécifique
            # -e ou --exec-date permet de simuler la date d'exécution (context['ds'])
            cmd = [
                "airflow", "dags", "trigger",
                "--exec-date", date_jour.isoformat(),
                dag_id
            ]
            
            st.write(f"📡 Appel de l'orchestrateur Airflow...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            st.write("✅ Signal de déclenchement envoyé avec succès.")
            st.info(f"Consultez l'interface Airflow (port 8080) pour suivre l'avancement du DAG `{dag_id}`.")
            
            status.update(label="✅ Pipeline Airflow déclenché !", state="complete", expanded=False)
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Erreur lors du déclenchement Airflow : {e.stderr}")
            status.update(label="⚠️ Échec du déclenchement", state="error", expanded=True)
        except Exception as e:
            st.error(f"❌ Une erreur inattendue est survenue : {e}")
            status.update(label="⚠️ Erreur critique", state="error", expanded=True)

def get_teacher_info(numero_ens: str):
    try:
        with connect_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nom, prenom FROM ref.enseignant WHERE numero_ens = %s", (numero_ens,))
                return cur.fetchone()
    except Exception as e:
        st.error(f"Erreur de connexion base : {e}")
        return None

def check_if_processed(cours_id: int, date_jour: date, session_name: str):
    """Vérifie si la séance est déjà dans Gold."""
    try:
        with connect_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM gold.presence_par_cours WHERE cours_id = %s AND date_jour = %s AND session = %s",
                    (cours_id, date_jour, session_name)
                )
                return cur.fetchone() is not None
    except:
        return False

def get_sessions_from_schedule(numero_ens: str, start_date: date, end_date: date):
    """Calcule les sessions réelles à partir du planning en base."""
    sql = """
        SELECT 
            c.id as cours_id,
            c.intitule,
            c.section,
            c.horaire,
            c.session,
            p.jour_semaine,
            p.heure_debut,
            p.heure_fin,
            e.nom as ens_nom,
            e.prenom as ens_prenom,
            p.salle,
            f.intitule as formation_nom,
            f.niveau as niveau_nom
        FROM ref.cours c
        JOIN ref.planning p ON c.id = p.cours_id
        JOIN ref.enseignant e ON c.enseignant_id = e.numero_ens
        JOIN ref.formation f ON c.formation_id = f.id
        WHERE e.numero_ens = %s
    """
    sessions = []
    with connect_postgres() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (numero_ens,))
            rows = cur.fetchall()
            
            for row in rows:
                c_id, intitule, section, horaire, session_type, jour_label, h_deb, h_fin, e_nom, e_prenom, salle, f_nom, n_nom = row
                
                try:
                    target_weekday = JOURS_FR.index(jour_label.capitalize())
                except ValueError:
                    continue
                
                curr = start_date
                while curr <= end_date:
                    if curr.weekday() == target_weekday:
                        cp = CoursPlanifie(
                            cours_id=c_id,
                            enseignant_id=numero_ens,
                            intitule=intitule,
                            section=section,
                            horaire=horaire,
                            session=session_type,
                            heure_debut=h_deb,
                            heure_fin=h_fin,
                            ens_nom=e_nom,
                            ens_prenom=e_prenom,
                            salle=salle or "Salle 101",
                            formation_nom=f_nom or "N/A",
                            niveau_nom=n_nom or "N/A"
                        )
                        
                        # --- LOGIQUE DE STATUT ROBUSTE ( get_file_status ) ---
                        fname = nom_fichier_xlsx(cp)
                        gen_path = ROOT / "data" / "generated" / curr.isoformat() / session_type / fname
                        coll_path = ROOT / "data" / "collected" / curr.isoformat() / session_type / fname
                        
                        is_generated = gen_path.exists()
                        is_collected = coll_path.exists()
                        is_processed = check_if_processed(c_id, curr, session_type)
                        
                        today = date.today()
                        
                        if curr < today:
                            # Logique HISTORIQUE (Passé)
                            if is_processed or is_collected:
                                status_label = "Traité"
                                status_class = "badge-done"
                                status_icon = "fa-circle-check"
                            else:
                                status_label = "Non traité"
                                status_class = "badge-error"
                                status_icon = "fa-circle-xmark"
                        else:
                            # Logique À VENIR (Présent/Futur)
                            if is_processed or is_collected:
                                status_label = "Traité"
                                status_class = "badge-done"
                                status_icon = "fa-circle-check"
                            elif is_generated:
                                status_label = "À remplir"
                                status_class = "badge-fill"
                                status_icon = "fa-file-signature"
                            else:
                                status_label = "À générer"
                                status_class = "badge-generate"
                                status_icon = "fa-file-circle-plus"

                        sessions.append({
                            "date": curr,
                            "session": session_type,
                            "intitule": intitule,
                            "formation": f_nom,
                            "niveau": n_nom,
                            "horaire": horaire,
                            "filename": fname,
                            "cours_id": c_id,
                            "cours_planifie": cp,
                            "is_generated": is_generated,
                            "is_collected": is_collected,
                            "is_processed": is_processed,
                            "generated_path": gen_path,
                            "collected_path": coll_path,
                            "status_label": status_label,
                            "status_class": status_class,
                            "status_icon": status_icon,
                            "salle": salle or "N/A"
                        })
                    curr += timedelta(days=1)
                    
    return sorted(sessions, key=lambda x: x['date'], reverse=True)

# --- APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.teacher_id = None
    st.session_state.teacher_name = ""

def login_form():
    st.markdown("""
        <div class="login-container">
            <div style="font-size: 3rem; color: #1e3a5f; margin-bottom: 1rem;"><i class="fas fa-user-circle"></i></div>
            <h2 style="color: #1e3a5f; margin-bottom: 0.5rem;">Espace Enseignant</h2>
            <p style="color: #64748b; margin-bottom: 2rem;">Veuillez vous identifier pour accéder à vos cours</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 2, 1])
    with col:
        tid = st.text_input("Numéro Enseignant", placeholder="ENS001...", label_visibility="collapsed")
        if st.button("Se connecter", use_container_width=True, type="primary"):
            if tid:
                info = get_teacher_info(tid)
                if info:
                    st.session_state.logged_in = True
                    st.session_state.teacher_id = tid
                    st.session_state.teacher_name = f"{info[1]} {info[0]}"
                    st.success(f"Bienvenue, {st.session_state.teacher_name}")
                    st.rerun()
                else:
                    st.error("Identifiant inconnu. Veuillez vérifier votre numéro ENS.")
            else:
                st.warning("Veuillez saisir votre identifiant.")

def dashboard_prof():
    # Header professionnel
    st.markdown(f"""
    <div class="app-header">
        <div>
            <h2 class="header-title">Bonjour, {st.session_state.teacher_name}</h2>
            <p class="header-subtitle"><i class="fas fa-graduation-cap"></i> Portail Enseignant | SmartAcademy Émargement</p>
        </div>
        <div>
            <span style="font-size: 0.8rem; background: rgba(255,255,255,0.1); padding: 0.4rem 0.8rem; border-radius: 6px; margin-right: 10px;">
                <i class="fas fa-id-card"></i> {st.session_state.teacher_id}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Filtres
    with st.sidebar:
        st.markdown("### <i class='fas fa-magnifying-glass'></i> Filtres")
        today = date.today()
        period = st.date_input("Période d'affichage", [today - timedelta(days=7), today + timedelta(days=14)])
        
        if len(period) == 2:
            start_d, end_d = period
        else:
            start_d = end_d = period[0]

        # Récupération sessions
        sessions = get_sessions_from_schedule(st.session_state.teacher_id, start_d, end_d)
        
        # Filtre par cours
        all_courses = sorted(list(set([s['intitule'] for s in sessions])))
        sel_course = st.selectbox("Filtrer par cours", ["Tous les cours"] + all_courses)
        
        st.divider()
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.teacher_id = None
            st.rerun()

    if sel_course != "Tous les cours":
        sessions = [s for s in sessions if s['intitule'] == sel_course]

    # LOGIQUE DE RÉPARTITION : État-Dépendant (Traité vs À faire)
    # À venir : Aujourd'hui ou futur, NON traité
    upcoming = [s for s in sessions if s['date'] >= today and not s['is_processed']]
    # Historique : Tout ce qui est déjà traité OU ce qui est passé (même non traité)
    past = [s for s in sessions if s['is_processed'] or s['date'] < today]

    tab_futur, tab_passe = st.tabs([
        f"📅 Séances à venir ({len(upcoming)})", 
        f"📖 Historique ({len(past)})"
    ])

    # --- ONGLET : SÉANCES À VENIR ---
    with tab_futur:
        if not upcoming:
            st.info("Aucune séance à venir prévue sur cette période.")
        else:
            for s in upcoming:
                with st.container():
                    st.markdown(f"""
                    <div class="session-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 2;">
                                <div style="margin-bottom: 0.5rem;">
                                    <span class="badge {s['status_class']}">
                                        <i class="fa-solid {s['status_icon']}"></i> {s['status_label']}
                                    </span>
                                </div>
                                <h3 style="margin: 0; color: #1e3a5f; font-size: 1.1rem; font-weight: 700;">{s['intitule']}</h3>
                                <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                                    <i class="fa-regular fa-calendar-days"></i> {s['date'].strftime('%d %B %Y')} &nbsp;|&nbsp; 
                                    <i class="fa-regular fa-clock"></i> {s['session'].capitalize()} &nbsp;|&nbsp; 
                                    <i class="fa-solid fa-location-dot"></i> {s['salle']}
                                </p>
                            </div>
                            <div style="flex: 1; text-align: right;">
                                <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                    Section: {s['cours_planifie'].section}
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #f1f5f9;">
                    """, unsafe_allow_html=True)
                    
                    cols = st.columns([1, 1, 1], vertical_alignment="center")
                    
                    # 1. Génération / Téléchargement
                    with cols[0]:
                        file_key = f"file_data_{s['filename']}_{s['date']}"
                        if not s['is_generated']:
                            if st.button("🪄 Générer Excel", key=f"btn_gen_{s['filename']}_{s['date']}", use_container_width=True):
                                with st.spinner("Génération..."):
                                    inscrits = fetch_inscrits(s['cours_planifie'].cours_id)
                                    if not inscrits:
                                        st.error("Aucun inscrit.")
                                    else:
                                        wb = build_workbook(s['cours_planifie'], s['date'], inscrits)
                                        s['generated_path'].parent.mkdir(parents=True, exist_ok=True)
                                        wb.save(str(s['generated_path']))
                                        output = io.BytesIO()
                                        wb.save(output)
                                        st.session_state[file_key] = output.getvalue()
                                        st.toast("✅ Fichier généré !")
                                        st.rerun()
                        
                        if s['is_generated'] or file_key in st.session_state:
                            if file_key not in st.session_state and s['is_generated']:
                                if s['generated_path'].exists():
                                    with open(s['generated_path'], "rb") as f:
                                        st.session_state[file_key] = f.read()

                            if file_key in st.session_state:
                                st.download_button(
                                    label="📥 Télécharger",
                                    data=st.session_state[file_key],
                                    file_name=s['filename'],
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"dl_btn_{s['filename']}_{s['date']}",
                                    use_container_width=True
                                )
                    
                    # 2. Upload (Dépôt)
                    with cols[1]:
                        if s['is_generated']:
                            up_key_base = f"up_{s['filename']}_{s['date']}"
                            if f"v_{up_key_base}" not in st.session_state:
                                st.session_state[f"v_{up_key_base}"] = 0
                            current_up_key = f"{up_key_base}_{st.session_state[f'v_{up_key_base}']}"

                            uploaded_file = st.file_uploader("", type=["xlsx"], key=current_up_key)
                            if uploaded_file:
                                if f"_cours{s['cours_id']}.xlsx" not in uploaded_file.name:
                                    st.error("❌ Fichier invalide.")
                                else:
                                    try:
                                        df_val = pd.read_excel(uploaded_file, header=6)
                                        df_val.columns = ['Numéro Ét.', 'Nom', 'Prénom', 'Présent', 'Remarque']
                                        invalid = df_val[~df_val['Présent'].astype(str).str.strip().str.upper().isin(['O', 'N'])]
                                        if not invalid.empty:
                                            st.error(f"❌ {len(invalid)} lignes invalides.")
                                        else:
                                            s['collected_path'].parent.mkdir(parents=True, exist_ok=True)
                                            with open(s['collected_path'], "wb") as bf:
                                                bf.write(uploaded_file.getbuffer())
                                            trigger_pipeline(s['date'], s['session'])
                                            st.session_state[f"v_{up_key_base}"] += 1
                                            st.success("✅ Déposé !")
                                            st.rerun()
                                    except Exception as ve:
                                        st.error(f"❌ Erreur : {ve}")
                        else:
                            st.markdown("<div style='text-align:center; color:#94a3b8; font-size:0.8rem; font-style:italic;'>Générez d'abord le fichier</div>", unsafe_allow_html=True)

                    # 3. Visualisation
                    with cols[2]:
                        if s['is_collected']:
                            view_state_key = f"show_list_{s['filename']}_{s['date']}"
                            if view_state_key not in st.session_state:
                                st.session_state[view_state_key] = False
                            
                            if not st.session_state[view_state_key]:
                                if st.button("🔍 Voir la liste", key=f"btn_open_{s['filename']}_{s['date']}", use_container_width=True):
                                    st.session_state[view_state_key] = True
                                    st.rerun()
                            else:
                                if st.button("✖️ Fermer", key=f"btn_close_{s['filename']}_{s['date']}", use_container_width=True):
                                    st.session_state[view_state_key] = False
                                    st.rerun()
                                    
                            if st.session_state[view_state_key]:
                                try:
                                    st.markdown("---")
                                    st.markdown(f"#### <i class='fas fa-users'></i> Inscrits - {s['intitule']}", unsafe_allow_html=True)
                                    df_preview = pd.read_excel(str(s['collected_path']), header=6)
                                    df_preview.columns = ['ID', 'Nom', 'Prénom', 'Présent', 'Remarque']
                                    st.dataframe(df_preview, use_container_width=True, height=300, hide_index=True)
                                    st.markdown("---")
                                except Exception as e:
                                    st.error(f"Erreur de lecture : {e}")
                        elif s['is_generated']:
                            st.markdown("<div style='text-align:center; color:#94a3b8; font-size:0.8rem;'>En attente de dépôt...</div>", unsafe_allow_html=True)

                    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- ONGLET : HISTORIQUE ---
    with tab_passe:
        if not past:
            st.markdown("""
                <div style="text-align:center; padding: 3rem;">
                    <i class="fas fa-clock-rotate-left" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 1rem;"></i>
                    <p style="color: #64748b;">Aucune séance passée enregistrée.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            h_traite = len([s for s in past if s['status_label'] == "Traité"])
            h_non_traite = len(past) - h_traite
            
            p_cols = st.columns(4)
            p_cols[0].metric("Total Passé", len(past))
            p_cols[1].metric("Traités", h_traite)
            p_cols[2].metric("Non Traités", h_non_traite, delta=-h_non_traite, delta_color="inverse")
            
            st.divider()

            st.markdown("#### <i class='fas fa-filter'></i> Filtres & Recherche", unsafe_allow_html=True)
            h_fcols = st.columns([2, 1, 1, 1])
            with h_fcols[0]:
                h_search = st.text_input("Rechercher", placeholder="Cours, formation...", key="h_search", label_visibility="collapsed")
            with h_fcols[1]:
                h_status = st.selectbox("Statut", ["Tous les statuts", "Traité", "Non traité"], key="h_status", label_visibility="collapsed")
            with h_fcols[2]:
                months = sorted(list(set([s['date'].strftime('%B %Y') for s in past])), reverse=True)
                h_month = st.selectbox("Période", ["Toute la période"] + months, key="h_month", label_visibility="collapsed")
            with h_fcols[3]:
                h_sort = st.selectbox("Tri", ["Plus récent", "Plus ancien"], key="h_sort", label_visibility="collapsed")

            # Filtrage
            filtered_past = past.copy()
            if h_search:
                filtered_past = [s for s in filtered_past if h_search.lower() in s['intitule'].lower() or h_search.lower() in (s.get('formation','') or '').lower()]
            if h_status != "Tous les statuts":
                filtered_past = [s for s in filtered_past if s['status_label'] == h_status]
            if h_month != "Toute la période":
                filtered_past = [s for s in filtered_past if s['date'].strftime('%B %Y') == h_month]
            
            filtered_past.sort(key=lambda x: x['date'], reverse=(h_sort == "Plus récent"))

            if not filtered_past:
                st.warning("Aucun résultat ne correspond.")
            else:
                past_data = []
                for s in filtered_past:
                    past_data.append({
                        "Date": s['date'],
                        "Cours": s['intitule'],
                        "Formation": s['formation'],
                        "Niveau": s['niveau'],
                        "Horaire": s['horaire'],
                        "Salle": s['salle'],
                        "Statut": s['status_label']
                    })
                
                df_past = pd.DataFrame(past_data)
                st.markdown('<div class="history-table-container">', unsafe_allow_html=True)
                st.dataframe(
                    df_past, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.DateColumn("📅 Date", format="DD/MM/YYYY"),
                        "Statut": st.column_config.TextColumn("🎯 État"),
                    }
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown(f"<div style='text-align:right; font-size:0.75rem; color:#64748b; margin-top:0.5rem;'><i class='fas fa-list'></i> {len(filtered_past)} séance(s) archivée(s)</div>", unsafe_allow_html=True)

            st.markdown("""
                <div style="background-color: #fffbeb; border: 1px solid #fef3c7; padding: 1rem; border-radius: 8px; margin-top: 2rem;">
                    <p style="color: #92400e; margin: 0; font-size: 0.85rem;">
                        <i class="fas fa-circle-info"></i> <strong>Note :</strong> L'historique est en lecture seule. Pour toute modification, contactez l'administration.
                    </p>
                </div>
            """, unsafe_allow_html=True)

# --- MAIN ---
if not st.session_state.logged_in:
    login_form()
else:
    dashboard_prof()
