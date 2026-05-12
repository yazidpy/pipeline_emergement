import streamlit as st
import pandas as pd
from datetime import date, time
from dashboard import crud_backend as backend
from utils.pdf_generator import generate_daily_planning_pdf

def safe_index(lst, val):
    try:
        if val in lst:
            return lst.index(val)
    except:
        pass
    return 0

# --- FORMATIONS ---
def manage_formations():
    st.markdown('<div class="section-title"><i class="fas fa-graduation-cap"></i> Catalogue des Formations</div>', unsafe_allow_html=True)
    df = backend.get_formations()
    
    with st.expander("Créer une nouvelle formation", expanded=False):
        with st.form("form_add_formation"):
            col1, col2 = st.columns(2)
            intitule = col1.text_input("Intitulé (ex: Data Science)")
            niveau = col2.selectbox("Niveau", ["Bac+1", "Bac+2", "Bac+3", "Master 1", "Master 2"])
            section = col1.text_input("Section (ex: Section A)")
            sess = col2.selectbox("Session", ["Septembre", "Février"])
            cout = st.number_input("Coût de l'inscription (€)", min_value=0, value=5000)
            
            if st.form_submit_button("Enregistrer la formation"):
                if intitule:
                    success, msg = backend.add_formation(intitule, niveau, section, sess, cout)
                    if success: st.success("Formation créée !"); st.rerun()
                    else: st.error(msg)

    st.dataframe(df, width='stretch', hide_index=True)
    
    if not df.empty:
        with st.expander("Modifier une formation", expanded=False):
            sel_id = st.selectbox("Sélectionner", df['id'].tolist())
            row = df[df['id'] == sel_id].iloc[0]
            with st.form("form_edit_formation"):
                col1, col2 = st.columns(2)
                int_e = col1.text_input("Intitulé", value=row['intitule'])
                niv_e = col2.selectbox("Niveau", ["Bac+1", "Bac+2", "Bac+3", "Master 1", "Master 2"], index=safe_index(["Bac+1", "Bac+2", "Bac+3", "Master 1", "Master 2"], row['niveau']))
                sec_e = col1.text_input("Section", value=row['section'])
                ses_e = col2.selectbox("Session", ["Septembre", "Février"], index=safe_index(["Septembre", "Février"], row['session']))
                cout_e = st.number_input("Coût", value=float(row['cout']))
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("Mettre à jour"):
                    backend.update_formation(sel_id, int_e, niv_e, sec_e, ses_e, cout_e)
                    st.success("Modifié !"); st.rerun()
                if c2.form_submit_button("Supprimer", type="secondary"):
                    success, msg = backend.delete_formation(sel_id)
                    if success: st.success("Supprimé !"); st.rerun()
                    else: st.error(f"Action impossible : {msg}")

# --- ÉTUDIANTS ---
def manage_etudiants():
    st.markdown('<div class="section-title"><i class="fas fa-user-graduate"></i> Gestion des Étudiants</div>', unsafe_allow_html=True)
    df = backend.get_etudiants()
    df_form = backend.get_formations()
    form_map = {f"{r['intitule']} ({r['niveau']})": r['id'] for _, r in df_form.iterrows()}
    
    with st.expander("Ajouter un étudiant", expanded=False):
        with st.form("form_add_etudiant"):
            c1, c2 = st.columns(2)
            numero_et = c1.text_input("Numéro Étudiant")
            nom = c2.text_input("Nom")
            prenom = c1.text_input("Prénom")
            date_n = c2.date_input("Date de naissance", value=date(2000, 1, 1))
            nat = c1.text_input("Nationalité", value="Marocaine")
            form_name = c2.selectbox("Formation", list(form_map.keys()))
            
            if st.form_submit_button("Enregistrer l'étudiant"):
                if numero_et and nom:
                    success, msg = backend.add_etudiant(numero_et, nom, prenom, date_n, nat, form_map[form_name])
                    if success: st.success("Étudiant ajouté !"); st.rerun()
                    else: st.error(msg)

    st.dataframe(df, width='stretch', hide_index=True)
    
    if not df.empty:
        with st.expander("Modifier un profil", expanded=False):
            sel_id = st.selectbox("Sélectionner par Numéro", df['numero_et'].tolist())
            row = df[df['numero_et'] == sel_id].iloc[0]
            with st.form("form_edit_etudiant"):
                c1, c2 = st.columns(2)
                nom_e = c1.text_input("Nom", value=row['nom'])
                prenom_e = c2.text_input("Prénom", value=row['prenom'])
                date_e = c1.date_input("Date de naissance", value=row['date_naissance'] if row['date_naissance'] else date(2000, 1, 1))
                nat_e = c2.text_input("Nationalité", value=row['nationalite'] if row['nationalite'] else "Marocaine")
                
                form_list = list(form_map.keys())
                curr_form_name = next((k for k,v in form_map.items() if v == row['formation_id']), form_list[0] if form_list else None)
                form_e = st.selectbox("Formation", form_list, index=safe_index(form_list, curr_form_name))
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("Mettre à jour"):
                    backend.update_etudiant(sel_id, nom_e, prenom_e, date_e, nat_e, form_map[form_e])
                    st.success("Profil mis à jour !"); st.rerun()
                if b2.form_submit_button("Supprimer", type="secondary"):
                    backend.delete_etudiant(sel_id)
                    st.success("Profil supprimé !"); st.rerun()

# --- ENSEIGNANTS ---
def manage_enseignants():
    st.markdown('<div class="section-title"><i class="fas fa-chalkboard-teacher"></i> Corps Enseignant</div>', unsafe_allow_html=True)
    df = backend.get_enseignants()
    
    with st.expander("Ajouter un enseignant", expanded=False):
        with st.form("form_add_prof"):
            c1, c2 = st.columns(2)
            num_ens = c1.text_input("Identifiant (ex: ENS001)")
            nom = c2.text_input("Nom")
            prenom = c1.text_input("Prénom")
            date_n = c2.date_input("Date de naissance", value=date(1980, 1, 1))
            nat = st.text_input("Nationalité", value="Marocaine")
            
            if st.form_submit_button("Enregistrer"):
                if num_ens and nom:
                    success, msg = backend.add_enseignant(num_ens, nom, prenom, date_n, nat)
                    if success: st.success("Enseignant ajouté !"); st.rerun()
                    else: st.error(msg)

    st.dataframe(df, width='stretch', hide_index=True)
    
    if not df.empty:
        with st.expander("Modifier un enseignant", expanded=False):
            sel_id = st.selectbox("Sélectionner un ID", df['numero_ens'].tolist())
            row = df[df['numero_ens'] == sel_id].iloc[0]
            with st.form("form_edit_prof"):
                c1, c2 = st.columns(2)
                nom_e = c1.text_input("Nom", value=row['nom'])
                prenom_e = c2.text_input("Prénom", value=row['prenom'])
                date_e = c1.date_input("Date de naissance", value=row['date_naissance'] if row['date_naissance'] else date(1980,1,1))
                nat_e = c2.text_input("Nationalité", value=row['nationalite'] if row['nationalite'] else "Marocaine")
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("Mettre à jour"):
                    backend.update_enseignant(sel_id, nom_e, prenom_e, date_e, nat_e)
                    st.success("Mis à jour !"); st.rerun()
                if b2.form_submit_button("Supprimer", type="secondary"):
                    backend.delete_enseignant(sel_id)
                    st.success("Supprimé !"); st.rerun()

# --- COURS ---
def manage_cours():
    st.markdown('<div class="section-title"><i class="fas fa-book-open"></i> Catalogue des Cours</div>', unsafe_allow_html=True)
    df = backend.get_cours()
    df_form = backend.get_formations()
    df_prof = backend.get_enseignants()
    
    form_map = {f"{r['intitule']} ({r['niveau']})": r['id'] for _, r in df_form.iterrows()}
    prof_map = {f"{r['prenom']} {r['nom']}": r['numero_ens'] for _, r in df_prof.iterrows()}
    
    with st.expander("Ajouter un cours", expanded=False):
        with st.form("form_add_cours"):
            intitule = st.text_input("Intitulé du cours")
            c1, c2 = st.columns(2)
            sess = c1.selectbox("Session temporelle", ["Matin", "Après-midi"])
            form_name = c2.selectbox("Rattaché à la Formation", list(form_map.keys()))
            prof_name = st.selectbox("Enseignant responsable", list(prof_map.keys()))
            
            if st.form_submit_button("Créer le cours"):
                success, msg = backend.add_cours(intitule, sess, form_map[form_name], prof_map[prof_name])
                if success: st.success("Cours ajouté !"); st.rerun()

    st.dataframe(df, width='stretch', hide_index=True)
    
    if not df.empty:
        with st.expander("Modifier un cours", expanded=False):
            sel_id = st.selectbox("ID Cours", df['id'].tolist())
            row = df[df['id'] == sel_id].iloc[0]
            with st.form("form_edit_cours"):
                int_e = st.text_input("Intitulé", value=row['intitule'])
                c1, c2 = st.columns(2)
                ses_e = c1.selectbox("Session", ["Matin", "Après-midi"], index=safe_index(["Matin", "Après-midi"], row['session']))
                
                form_list = list(form_map.keys())
                curr_f = next((k for k,v in form_map.items() if v == row['formation_id']), form_list[0] if form_list else None)
                form_e = c2.selectbox("Formation", form_list, index=safe_index(form_list, curr_f))
                
                prof_list = list(prof_map.keys())
                curr_p = next((k for k,v in prof_map.items() if v == row['enseignant_id']), prof_list[0] if prof_list else None)
                prof_e = st.selectbox("Enseignant", prof_list, index=safe_index(prof_list, curr_p))
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("Mettre à jour"):
                    backend.update_cours(sel_id, int_e, ses_e, form_map[form_e], prof_map[prof_e])
                    st.success("Cours mis à jour !"); st.rerun()
                if b2.form_submit_button("Supprimer", type="secondary"):
                    backend.delete_cours(sel_id)
                    st.success("Cours retiré !"); st.rerun()

# --- PLANNING ---
def manage_planning(conn, logo_path):
    st.markdown('<div class="section-title"><i class="fas fa-calendar-check"></i> Organisation du Planning</div>', unsafe_allow_html=True)
    df = backend.get_planning(conn)
    df_cours = backend.get_cours()
    cours_map = {r['intitule']: r['id'] for _, r in df_cours.iterrows()}
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    # Export Planning en PDF
    c1, c2 = st.columns([2, 1])
    export_date = c1.date_input("Date pour l'impression du planning", value=date.today())
    
    jour_tr = {0:'lundi', 1:'mardi', 2:'mercredi', 3:'jeudi', 4:'vendredi', 5:'samedi', 6:'dimanche'}
    target_day = jour_tr[export_date.weekday()]
    
    query_pdf = """
        SELECT 
            p.heure_debut, p.heure_fin, 
            c.intitule as cours_nom, p.salle, 
            e.nom as ens_nom, e.prenom as ens_prenom,
            f.intitule as formation_nom, f.niveau
        FROM ref.planning p
        JOIN ref.cours c ON p.cours_id = c.id
        JOIN ref.enseignant e ON c.enseignant_id = e.numero_ens
        JOIN ref.formation f ON c.formation_id = f.id
        WHERE p.jour_semaine = %s
    """
    try:
        df_pdf_data = pd.read_sql(query_pdf, conn, params=(target_day,))
        pdf_bytes = generate_daily_planning_pdf(df_pdf_data, export_date, logo_path)
        st.download_button(label="GÉNÉRER LE PLANNING DU JOUR", data=pdf_bytes, file_name=f"planning_{export_date}.pdf", mime="application/pdf")
        if not df_pdf_data.empty: st.toast("Planning prêt !", icon="✅")
    except Exception as e: st.error(f"PDF Error: {e}")

    with st.expander("Ajouter une séance", expanded=False):
        with st.form("form_add_plan"):
            cours_name = st.selectbox("Cours", list(cours_map.keys()))
            jour = st.selectbox("Jour", jours)
            salle = st.text_input("Salle", value="Salle 101")
            h_deb = st.time_input("Début", value=time(8, 0))
            h_fin = st.time_input("Fin", value=time(10, 0))
            if st.form_submit_button("Ajouter"):
                backend.add_planning(cours_map[cours_name], jour.lower(), h_deb.strftime("%H:%M"), h_fin.strftime("%H:%M"), salle)
                st.success("Ajouté !"); st.rerun()

    st.dataframe(df, width='stretch', hide_index=True)
    
    if not df.empty:
        with st.expander("Gérer les séances", expanded=False):
            sel_id = st.selectbox("Sélectionner séance", df['id'].tolist())
            row = df[df['id'] == sel_id].iloc[0]
            with st.form("form_edit_plan"):
                c_list = list(cours_map.keys())
                curr_c = next((k for k,v in cours_map.items() if v == row['cours_id']), c_list[0] if c_list else None)
                c_e = st.selectbox("Cours", c_list, index=safe_index(c_list, curr_c))
                j_e = st.selectbox("Jour", jours, index=safe_index(jours, row['jour_semaine'].capitalize()))
                salle_e = st.text_input("Salle", value=row['salle'])
                h_d_e = st.time_input("Début", value=pd.to_datetime(str(row['heure_debut'])).time())
                h_f_e = st.time_input("Fin", value=pd.to_datetime(str(row['heure_fin'])).time())
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("Modifier"):
                    backend.update_planning(sel_id, cours_map[c_e], j_e.lower(), h_d_e.strftime("%H:%M"), h_f_e.strftime("%H:%M"), salle_e)
                    st.success("Mis à jour !"); st.rerun()
                if b2.form_submit_button("Retirer", type="secondary"):
                    backend.delete_planning(sel_id)
                    st.success("Retiré !"); st.rerun()

# --- PAIEMENTS ---
def manage_paiements():
    st.markdown('<div class="section-title"><i class="fas fa-wallet"></i> Suivi des Paiements et Soldes</div>', unsafe_allow_html=True)
    df = backend.get_paiements()
    df_et = backend.get_etudiants()
    df_form = backend.get_formations()
    
    et_map = {f"{r['prenom']} {r['nom']} ({r['numero_et']})": r['numero_et'] for _, r in df_et.iterrows()}
    form_map = {f"{r['intitule']} ({r['niveau']})": r['id'] for _, r in df_form.iterrows()}
    
    with st.expander("Enregistrer un nouveau paiement", expanded=False):
        with st.form("form_add_paiement"):
            et_name = st.selectbox("Étudiant", list(et_map.keys()))
            form_name = st.selectbox("Formation Concernée", list(form_map.keys()))
            montant = st.number_input("Montant Versé (€)", min_value=0, value=0)
            if st.form_submit_button("Valider le paiement"):
                success, msg = backend.add_paiement(et_map[et_name], form_map[form_name], montant)
                if success: st.success("Paiement enregistré !"); st.rerun()
                else: st.error(msg)

    # Style pour mettre en évidence les impayés
    if not df.empty:
        st.dataframe(df, width='stretch', hide_index=True)
        
        with st.expander("Mettre à jour un versement", expanded=False):
            df['label'] = df['et_prenom'] + " " + df['et_nom'] + " (" + df['formation_nom'] + ")"
            sel_label = st.selectbox("Rechercher un paiement", df['label'].tolist())
            if sel_label:
                row = df[df['label'] == sel_label].iloc[0]
                with st.form("form_edit_paiement"):
                    st.info(f"Reste initial : {row['reste_a_payer']} €")
                    new_montant = st.number_input("Nouveau montant total versé", value=float(row['paiement']))
                    if st.form_submit_button("Actualiser le solde"):
                        backend.update_paiement(row['id_etudiant'], row['id_formation'], new_montant)
                        st.success("Solde actualisé !"); st.rerun()

# --- INSCRIPTIONS ---
def manage_inscriptions():
    st.markdown('<div class="section-title"><i class="fas fa-id-card"></i> Inscriptions aux Formations</div>', unsafe_allow_html=True)
    df = backend.get_inscriptions()
    df_et = backend.get_etudiants()
    df_form = backend.get_formations()
    
    et_map = {f"{r['prenom']} {r['nom']} ({r['numero_et']})": r['numero_et'] for _, r in df_et.iterrows()}
    form_map = {f"{r['intitule']} ({r['niveau']} - {r['session']})": r['id'] for _, r in df_form.iterrows()}
    
    with st.expander("Nouvelle inscription à une formation", expanded=False):
        with st.form("form_add_ins"):
            et_name = st.selectbox("Étudiant", list(et_map.keys()))
            form_name = st.selectbox("Formation", list(form_map.keys()))
            d_ins = st.date_input("Date", value=date.today())
            if st.form_submit_button("Inscrire l'étudiant"):
                success, msg = backend.add_inscription(et_map[et_name], form_map[form_name], d_ins)
                if success: st.success("Inscription effectuée !"); st.rerun()
                else: st.error(msg)

    if not df.empty:
        # Display simplified columns
        display_df = df[['id_etudiant', 'et_nom', 'et_prenom', 'formation_nom', 'formation_session', 'date_inscription']]
        st.dataframe(display_df, width='stretch', hide_index=True)
        
        with st.expander("Se désinscrire d'une formation", expanded=False):
            df['label'] = df['et_prenom'] + " " + df['et_nom'] + " -> " + df['formation_nom'] + " (" + df['formation_session'] + ")"
            del_label = st.selectbox("Sélectionner l'inscription à retirer", df['label'].tolist())
            if del_label:
                row = df[df['label'] == del_label].iloc[0]
                if st.button("❌ Confirmer le retrait", type="secondary"):
                    success, msg = backend.delete_inscription(row['id_etudiant'], row['id_formation'])
                    if success: st.success("Désinscription effectuée !"); st.rerun()
                    else: st.error(msg)
