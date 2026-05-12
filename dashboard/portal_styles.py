import streamlit as st

def apply_portal_styles():
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

    /* Session Cards */
    .session-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .card-top { display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; }
    .card-meta { display: flex; gap: 15px; color: #64748b; font-size: 0.85rem; }
    .card-title { margin: 0.5rem 0; color: #0f172a; font-size: 1.25rem; font-weight: 700; }
    .card-subtitle { color: #64748b; font-size: 0.9rem; margin: 0; }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        gap: 6px;
    }
    .badge-generate { background: #fee2e2; color: #dc2626; }
    .badge-fill { background: #fef3c7; color: #92400e; }
    .badge-done { background: #dcfce7; color: #15803d; }
    .badge-error { background: #fee2e2; color: #b91c1c; }

    /* Boutons */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
