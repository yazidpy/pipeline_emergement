import streamlit as st
import pandas as pd
from dashboard.data_loader import get_total_unique_students
from dashboard.components import display_kpi_metrics
from dashboard.charts import display_presence_chart, display_section_stats, display_retour_chart

def render_tab_presence(conn, df_presence, df_retour):
    total_real = get_total_unique_students(conn)
    display_kpi_metrics(df_presence, df_retour, total_real)
    
    c_gran, _ = st.columns([1, 3])
    with c_gran:
        granularity = st.select_slider("Vue temporelle", options=["Semaine", "Mois"], value="Semaine", label_visibility="collapsed")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="section-title">Évolution - Taux de Présence ({granularity})</div>', unsafe_allow_html=True)
        display_presence_chart(df_presence, granularity)
    with col2:
        st.markdown('<div class="section-title">Répartition par Section</div>', unsafe_allow_html=True)
        display_section_stats(df_presence)
    
    if not df_retour.empty:
        st.markdown(f'<div class="section-title">Performance Retour des Feuilles ({granularity})</div>', unsafe_allow_html=True)
        df_retour['nom_complet'] = df_retour['enseignant_prenom'] + " " + df_retour['enseignant_nom']
        enseignants = ["Tous les enseignants"] + sorted(df_retour['nom_complet'].unique().tolist())
        
        c1, c2 = st.columns([1, 2])
        with c1: choix_ens = st.selectbox("Sélection Enseignant", enseignants, label_visibility='collapsed')
        
        df_filtered = df_retour.copy()
        if choix_ens != "Tous les enseignants":
            df_filtered = df_filtered[df_filtered['nom_complet'] == choix_ens]
        display_retour_chart(df_filtered, granularity)
