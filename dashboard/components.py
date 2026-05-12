import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import Optional

def render_filters(conn, key_prefix: str, show_formation: bool = False, formation_only: bool = False):
    today = date.today()
    default_start = today - timedelta(days=365)
    
    st.markdown('<div class="filters-bar">', unsafe_allow_html=True)
    
    if formation_only:
        cols = st.columns([4, 1])
        with cols[0]:
            from dashboard.crud_backend import get_formations
            df_f = get_formations()
            form_options = {"Toutes les formations / Niveaux": None}
            for _, r in df_f.iterrows():
                form_options[f"{r['intitule']} ({r['niveau']})"] = r['id']
            
            sel_form = st.selectbox("Formation & Niveau", list(form_options.keys()), label_visibility='collapsed', key=f"{key_prefix}_form_only")
            formation_id = form_options[sel_form]
            d_debut, d_fin = default_start, today
        with cols[1]:
            if st.button("↻ Rafraîchir", width="stretch", key=f"{key_prefix}_refresh_only"):
                st.rerun()
    else:
        if show_formation:
            cols = st.columns([1, 1, 1.5, 1.5, 1])
        else:
            cols = st.columns([1, 1, 2, 1])
            
        with cols[0]:
            d_debut = st.date_input("Début", value=today - timedelta(days=30), max_value=today, label_visibility='collapsed', key=f"{key_prefix}_start")
        with cols[1]:
            d_fin = st.date_input("Fin", value=today, min_value=d_debut, max_value=today, label_visibility='collapsed', key=f"{key_prefix}_end")
        
        formation_id = None
        if show_formation:
            with cols[2]:
                from dashboard.crud_backend import get_formations
                df_f = get_formations()
                form_options = {"Toutes les formations": None}
                for _, r in df_f.iterrows():
                    form_options[f"{r['intitule']} ({r['niveau']})"] = r['id']
                sel_form = st.selectbox("Formation", list(form_options.keys()), label_visibility='collapsed', key=f"{key_prefix}_form")
                formation_id = form_options[sel_form]
            col_label_idx, col_btn_idx = 3, 4
        else:
            col_label_idx, col_btn_idx = 2, 3

        with cols[col_label_idx]:
            st.markdown(f"<span class='filter-label'>Période : {d_debut} → {d_fin}</span>", unsafe_allow_html=True)
        with cols[col_btn_idx]:
            if st.button("↻ Rafraîchir", width="stretch", key=f"{key_prefix}_refresh"):
                st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
    return d_debut, d_fin, formation_id

def display_kpi_metrics(df_presence: pd.DataFrame, df_retour: pd.DataFrame, total_real_students: int):
    total_cours = len(df_presence)
    taux_moyen = df_presence['taux_presence'].mean() if not df_presence.empty else 0
    retour_moyen = df_retour['taux_retour'].mean() if not df_retour.empty else 0
    
    kpi_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-header"><span class="kpi-label">Total Cours</span><div class="kpi-icon blue"><i class="fas fa-graduation-cap"></i></div></div><div class="kpi-value">{total_cours}</div><div class="kpi-delta">Sessions programmées</div></div>
        <div class="kpi-card"><div class="kpi-header"><span class="kpi-label">Taux Présence</span><div class="kpi-icon green"><i class="fas fa-user-check"></i></div></div><div class="kpi-value">{taux_moyen:.1f}%</div><div class="kpi-delta">Moyenne sur la période</div></div>
        <div class="kpi-card"><div class="kpi-header"><span class="kpi-label">Retour Feuilles</span><div class="kpi-icon amber"><i class="fas fa-file-signature"></i></div></div><div class="kpi-value">{retour_moyen:.1f}%</div><div class="kpi-delta">Taux de collecte</div></div>
        <div class="kpi-card"><div class="kpi-header"><span class="kpi-label">Effectif Étudiants</span><div class="kpi-icon purple"><i class="fas fa-users"></i></div></div><div class="kpi-value">{total_real_students}</div><div class="kpi-delta">Étudiants uniques inscrits</div></div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
