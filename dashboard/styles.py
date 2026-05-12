import streamlit as st

def apply_styles():
    st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* Reset Streamlit defaults */
    .main > div { padding: 0.5rem 1rem; }
    .block-container { padding: 0.5rem 1rem; max-width: 100%; }
    
    /* Header professionnel */
    .app-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Navigation horizontale */
    .nav-container {
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        display: flex;
        gap: 0.25rem;
    }

    /* Bouton Export PDF - Style SaaS Vert */
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px rgba(40, 167, 69, 0.2) !important;
    }
    
    /* Filtres compact */
    .filters-bar {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Cards KPI modernes */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    
    .kpi-icon { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; }
    .kpi-icon.blue { background: #dbeafe; color: #1e40af; }
    .kpi-icon.green { background: #d1fae5; color: #065f46; }
    .kpi-icon.amber { background: #fef3c7; color: #92400e; }
    .kpi-icon.purple { background: #e0e7ff; color: #3730a3; }
    
    .kpi-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0; }
    .kpi-delta { font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }
    
    /* Sections */
    .section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e3a5f;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Alertes redesign */
    .alert-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .alert-card.critical { background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-color: #dc2626; }
    .alert-icon.critical { color: #dc2626; }
    .alert-content { flex: 1; }
    .alert-title { font-size: 0.8125rem; font-weight: 600; color: #1f2937; margin: 0; }
    .alert-meta { font-size: 0.75rem; color: #6b7280; margin-top: 0.125rem; }
    
    /* Hide default Streamlit elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
