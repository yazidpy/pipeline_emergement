import streamlit as st
import pandas as pd
from dashboard.charts import display_etudiant_top_chart
from utils.pdf_generator import generate_student_report_pdf

def display_absences_alertes(df_absences: pd.DataFrame):
    if df_absences.empty:
        st.markdown('<div style="text-align:center; padding:1.5rem; color:#64748b;"><i class="fas fa-check-circle" style="font-size:1.5rem; color:#22c55e;"></i><br>Aucune alerte</div>', unsafe_allow_html=True)
        return
    for _, row in df_absences.iterrows():
        is_crit = row['nb_absences_consecutives'] >= 5
        st.markdown(f"""
        <div class="alert-card {'critical' if is_crit else ''}">
            <div class="alert-icon {'critical' if is_crit else ''}"><i class="fas fa-{'exclamation-triangle' if is_crit else 'bell'}"></i></div>
            <div class="alert-content">
                <div class="alert-title">{row['prenom']} {row['nom']} - {row['nb_absences_consecutives']} absences</div>
                <div class="alert-meta">{row['filiere']} • Depuis le {row['date_jour']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_student_fiche(conn, numero_et):
    """Vue détaillée 'Fiche Étudiant'"""
    try:
        # 1. Infos de base
        q_info = "SELECT e.*, f.intitule as formation_nom FROM ref.etudiant e JOIN ref.formation f ON e.formation_id = f.id WHERE numero_et = %s"
        df_info = pd.read_sql(q_info, conn, params=(numero_et,))
        if df_info.empty: return st.error("Étudiant introuvable")
        student = df_info.iloc[0]
        
        # 2. Score & Badge
        q_score = "SELECT * FROM gold.scoring_etudiants WHERE numero_et = %s"
        df_score = pd.read_sql(q_score, conn, params=(numero_et,))
        score = df_score.iloc[0]['score_serieux'] if not df_score.empty else "N/A"
        badge = df_score.iloc[0]['badge'] if not df_score.empty else "SANS BADGE"
        
        # 3. Paiements
        q_pay = "SELECT * FROM ref.paiement WHERE id_etudiant = %s"
        df_pay = pd.read_sql(q_pay, conn, params=(numero_et,))
        total_pay = df_pay['paiement'].sum() if not df_pay.empty else 0
        reste = df_pay['reste_a_payer'].iloc[0] if not df_pay.empty else "N/A"

        st.markdown(f"### <i class='fas fa-address-card'></i> {student['prenom']} {student['nom'].upper()}", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Formation", student['formation_nom'], student['niveau'])
        c2.metric("Score Sérieux", f"{score}/100", badge)
        c3.metric("Solde Restant", f"{reste} €", f"Payé: {total_pay} €", delta_color="inverse")
        
        # 4. Historique de présence
        st.markdown("#### <i class='fas fa-calendar-alt'></i> Historique des Présences", unsafe_allow_html=True)
        q_hist = """
            SELECT date_jour, session, present 
            FROM gold.presence_par_etudiant 
            WHERE numero_et = %s 
            ORDER BY date_jour DESC
        """
        df_hist = pd.read_sql(q_hist, conn, params=(numero_et,))
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            
            # --- BOUTON DE TÉLÉCHARGEMENT ---
            st.markdown("---")
            try:
                # --- CALCUL DES MÉTRIQUES POUR LE CERTIFICAT ---
                nb_pres = df_hist[df_hist['present'] == True].shape[0] if not df_hist.empty else 0
                nb_abs = df_hist[df_hist['present'] == False].shape[0] if not df_hist.empty else 0
                total_sess = df_hist.shape[0]
                taux_p = round((nb_pres / total_sess * 100), 1) if total_sess > 0 else 0
                
                metrics = {
                    'nb_presences': nb_pres,
                    'nb_absences': nb_abs,
                    'taux': taux_p,
                    'total_heures': total_sess * 4, # On estime 4h par session (Matin/Après-midi)
                    'date_debut': df_hist['date_jour'].min().strftime('%d/%m/%Y') if not df_hist.empty else "N/A",
                    'date_fin': df_hist['date_jour'].max().strftime('%d/%m/%Y') if not df_hist.empty else "N/A"
                }

                logo_p = "assets/logo.png"
                pdf_data = generate_student_report_pdf(student, df_hist, metrics, logo_path=logo_p)
                
                st.download_button(
                    label="📄 Télécharger la Fiche d'Assiduité (PDF)",
                    data=pdf_data,
                    file_name=f"Fiche_Assiduite_{student['nom']}_{student['numero_et']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as pdf_err:
                st.warning(f"Impossible de générer le PDF : {pdf_err}")
        else:
            st.info("Aucun historique de présence.")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement de la fiche : {e}")

def render_tab_etudiants(conn, df_etudiants, df_absences):
    st.markdown('<div class="section-title">Gestion & Analyses Étudiants</div>', unsafe_allow_html=True)
    
    m_tab1, m_tab2 = st.tabs(["📊 Statistiques & Alertes", "🔍 Fiche Étudiant"])
    
    with m_tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown('<div class="section-title">Alertes Absences</div>', unsafe_allow_html=True)
            display_absences_alertes(df_absences)
        with col2:
            st.markdown('<div class="section-title">Top 10 Assiduité</div>', unsafe_allow_html=True)
            if not df_etudiants.empty:
                df_top = df_etudiants.sort_values('taux_presence_etudiant', ascending=False).head(10).copy()
                df_top['nom_complet'] = df_top['prenom'] + " " + df_top['nom']
                display_etudiant_top_chart(df_top)
    
    with m_tab2:
        st.markdown('<div class="section-title">Consultation Dossier Individuel</div>', unsafe_allow_html=True)
        all_ids = df_etudiants['numero_et'].tolist() if not df_etudiants.empty else []
        if all_ids:
            sel_id = st.selectbox("Choisir un étudiant", all_ids, format_func=lambda x: f"{x} - {df_etudiants[df_etudiants['numero_et']==x].iloc[0]['nom']} {df_etudiants[df_etudiants['numero_et']==x].iloc[0]['prenom']}")
            if sel_id:
                render_student_fiche(conn, sel_id)
        else:
            st.warning("Aucun étudiant disponible dans cette sélection.")
