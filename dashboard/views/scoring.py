import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.data_loader import load_ia_scoring

def render_tab_scoring(engine):
    st.markdown('<div class="section-title">Scoring & Badges Étudiants</div>', unsafe_allow_html=True)
    df_scores = load_ia_scoring(engine)
    
    if df_scores.empty:
        st.markdown('<div class="empty-state"><i class="fas fa-medal"></i><br>Scoring non calculé</div>', unsafe_allow_html=True)
        return
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Score moyen", f"{df_scores['score_serieux'].mean():.1f}")
    col2.metric("Badges OR", len(df_scores[df_scores['badge'] == 'OR']), "Top 10%")
    col3.metric("Badges Argent", len(df_scores[df_scores['badge'] == 'ARGENT']), "Top 25%")
    col4.metric("À risque", len(df_scores[df_scores['score_serieux'] < 50]), "Score < 50")
    
    df_agg = df_scores.groupby(['formation_nom', 'niveau']).agg({'score_serieux': 'mean'}).reset_index()
    df_agg['label'] = df_agg['formation_nom'] + " (" + df_agg['niveau'] + ")"
    df_agg = df_agg.sort_values('score_serieux', ascending=False)
    
    fig = px.line(df_agg, x='label', y='score_serieux', markers=True, text=df_agg['score_serieux'].round(1), labels={'label': 'Formation', 'score_serieux': 'Score Moyen'}, color_discrete_sequence=['#1e3a5f'])
    fig.update_traces(textposition='top center', line=dict(width=3), marker=dict(size=10, line=dict(width=2, color='white')))
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=320, plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter, sans-serif', size=11))
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_scores.head(20), use_container_width=True, hide_index=True, column_config={'score_serieux': st.column_config.ProgressColumn(min_value=0, max_value=100, format='%d/100')})
