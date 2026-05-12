import streamlit as st
import pandas as pd
import plotly.express as px

def display_presence_chart(df_presence: pd.DataFrame, granularity: str = "Semaine"):
    if df_presence.empty:
        st.markdown('<div class="empty-state"><i class="fas fa-chart-line"></i><br>Aucune donnée</div>', unsafe_allow_html=True)
        return
    
    df_chart = df_presence.copy()
    df_chart['date_jour'] = pd.to_datetime(df_chart['date_jour'])
    
    if granularity == "Semaine":
        df_chart['periode'] = df_chart['date_jour'].dt.strftime('S%U (%b %Y)')
    else:
        df_chart['periode'] = df_chart['date_jour'].dt.strftime('%B %Y')
    
    df_agg = df_chart.groupby(['periode', 'session']).agg({'nb_inscrits': 'sum', 'nb_presents': 'sum'}).reset_index()
    df_agg['taux_presence'] = (df_agg['nb_presents'] / df_agg['nb_inscrits'] * 100).round(1)
    df_agg = df_agg.sort_values(['periode', 'session'])
    
    fig = px.bar(
        df_agg, x='periode', y='taux_presence', color='session',
        barmode='group', text='taux_presence',
        labels={'periode': '', 'taux_presence': 'Présence (%)', 'session': 'Session'},
        color_discrete_map={'matin': '#22c55e', 'apres-midi': '#3b82f6'}
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside', marker_line_width=0)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=320,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(showgrid=False), yaxis=dict(range=[0, 115], ticksuffix='%'),
        plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter, sans-serif', size=11)
    )
    st.plotly_chart(fig, width="stretch")

def display_section_stats(df_presence: pd.DataFrame):
    if df_presence.empty: return
    df_section = df_presence.groupby('section').agg({'nb_inscrits': 'sum', 'nb_presents': 'sum', 'taux_presence': 'mean'}).reset_index()
    df_section['taux_presence'] = df_section['taux_presence'].round(1)
    
    fig = px.pie(df_section, names='section', values='taux_presence', hole=0.4, color_discrete_sequence=['#1e3a5f', '#3b82f6', '#64748b'])
    fig.update_traces(textinfo='percent+label', pull=[0.05, 0])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=240, showlegend=False)
    st.plotly_chart(fig, width="stretch")

def display_retour_chart(df_retour: pd.DataFrame, granularity: str = "Semaine"):
    if df_retour.empty: return
    df_chart = df_retour.copy()
    df_chart['date_jour'] = pd.to_datetime(df_chart['date_jour'])
    if granularity == "Semaine":
        df_chart['periode'] = df_chart['date_jour'].dt.strftime('S%U (%b %Y)')
    else:
        df_chart['periode'] = df_chart['date_jour'].dt.strftime('%B %Y')
        
    df_agg = df_chart.groupby(['periode']).agg({'nb_attendus': 'sum', 'nb_recus': 'sum'}).reset_index()
    df_agg['taux_retour'] = (df_agg['nb_recus'] / df_agg['nb_attendus'] * 100).round(1)
    df_agg = df_agg.sort_values('periode')
    
    fig = px.area(df_agg, x='periode', y='taux_retour', labels={'periode': '', 'taux_retour': 'Retour (%)'}, color_discrete_sequence=['#f59e0b'])
    fig.update_traces(mode='lines+markers+text', text=df_agg['taux_retour'], textposition='top center', fillcolor='rgba(245, 158, 11, 0.2)', line=dict(width=3))
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=260, yaxis=dict(range=[0, 120], ticksuffix='%'), plot_bgcolor='white')
    st.plotly_chart(fig, width="stretch")

def display_etudiant_top_chart(df_top: pd.DataFrame):
    fig = px.bar(
        df_top, x='taux_presence_etudiant', y='nom_complet', orientation='h',
        text='taux_presence_etudiant', color='taux_presence_etudiant',
        color_continuous_scale='Greens', labels={'taux_presence_etudiant': 'Présence (%)', 'nom_complet': ''}
    )
    fig.update_traces(texttemplate='%{text}%', textposition='inside', marker_line_width=0)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=380, showlegend=False,
        coloraxis_showscale=False, xaxis=dict(range=[0, 110], ticksuffix='%'),
        yaxis=dict(autorange="reversed", showgrid=False), plot_bgcolor='white'
    )
    st.plotly_chart(fig, width="stretch")
