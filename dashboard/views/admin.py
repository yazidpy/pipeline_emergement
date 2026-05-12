import streamlit as st
from dashboard import crud_ui

def render_tab_admin(conn, logo_path):
    st.markdown('<div class="section-title">Centre de Gestion Administrative</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .admin-card {
        background: white; padding: 1rem; border-radius: 10px; border-left: 5px solid #1e3a5f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1rem;
    }
    .admin-icon { font-size: 1.5rem; margin-right: 0.5rem; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

    sub_tabs = st.tabs(["Formations", "Paiements", "Étudiants", "Enseignants", "Cours", "Planning", "Inscriptions"])
    
    with sub_tabs[0]: crud_ui.manage_formations()
    with sub_tabs[1]: crud_ui.manage_paiements()
    with sub_tabs[2]: crud_ui.manage_etudiants()
    with sub_tabs[3]: crud_ui.manage_enseignants()
    with sub_tabs[4]: crud_ui.manage_cours()
    with sub_tabs[5]: crud_ui.manage_planning(conn, logo_path)
    with sub_tabs[6]: crud_ui.manage_inscriptions()
