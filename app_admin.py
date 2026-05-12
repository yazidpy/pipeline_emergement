"""
GoldenCollar Dashboard Admin - Version Modulaire
"""
import sys
from pathlib import Path
from datetime import date
import streamlit as st
from sqlalchemy import create_engine

# Configuration Racine
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils.db import connect_postgres, get_postgres_dsn
from utils.auth import verify_password
from dashboard.styles import apply_styles
from dashboard.components import render_filters
from dashboard.data_loader import load_presence_stats, load_etudiant_stats, load_absences_alertes, load_retour_feuilles
from dashboard.views.presence import render_tab_presence
from dashboard.views.etudiants import render_tab_etudiants
from dashboard.views.scoring import render_tab_scoring
from dashboard.views.admin import render_tab_admin

# --- CONFIGURATION STREAMLIT ---
st.set_page_config(
    page_title="SmartAcademy Émargement",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LOGO_PATH = "assets/logo.png"

def get_sqlalchemy_engine():
    """Crée un engine SQLAlchemy pour pandas"""
    return create_engine(get_postgres_dsn())

def login_screen():
    """Écran de connexion administrateur"""
    st.markdown("""
        <div style="max-width: 400px; margin: 50px auto; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; color: #1e3a5f; margin-bottom: 1rem;"><i class="fas fa-shield-halved"></i></div>
                <h2 style="color: #1e3a5f; margin: 0;">Administration</h2>
                <p style="color: #64748b; font-size: 0.875rem;">Accès restreint aux administrateurs</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 1, 1])
    with col:
        user = st.text_input("Utilisateur", key="admin_user")
        pwd = st.text_input("Mot de passe", type="password", key="admin_pwd")
        if st.button("Se connecter", use_container_width=True, type="primary"):
            try:
                with connect_postgres() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT password_hash FROM ref.credentials WHERE login = %s AND role = 'admin'", (user,))
                        res = cur.fetchone()
                        if res and verify_password(pwd, res[0]):
                            st.session_state.admin_logged_in = True
                            st.rerun()
                        else: st.error("Identifiants incorrects.")
            except Exception as e: st.error(f"Erreur : {e}")

def main():
    apply_styles()
    
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
        
    if not st.session_state.admin_logged_in:
        login_screen()
        return

    # Header
    st.markdown(f"""
    <div class="app-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: white; font-size: 1.5rem; font-weight: 700;">SmartAcademy Dashboard</div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">Système d'Émargement Intelligent • {date.today().strftime('%d %B %Y')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()

    # Tabs
    tabs = st.tabs(["Présence", "Étudiants", "Scoring", "Administration"])
    
    try:
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            with tabs[0]:
                d1, d2, _ = render_filters(conn, "presence")
                df_p = load_presence_stats(conn, d1, d2)
                df_r = load_retour_feuilles(conn, d1, d2)
                render_tab_presence(conn, df_p, df_r)
            
            with tabs[1]:
                d1, d2, f_id = render_filters(conn, "etudiants", formation_only=True)
                df_e = load_etudiant_stats(conn, d1, d2, formation_id=f_id)
                df_a = load_absences_alertes(conn, d1, d2, formation_id=f_id)
                render_tab_etudiants(conn, df_e, df_a)
            
            with tabs[2]:
                render_tab_scoring(conn)
                
            with tabs[3]:
                render_tab_admin(conn, LOGO_PATH)
        
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.info("Vérifiez la connexion PostgreSQL.")

if __name__ == "__main__":
    main()