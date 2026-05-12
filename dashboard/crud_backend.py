import pandas as pd
from typing import List, Dict, Any, Optional
import psycopg2
from utils.db import connect_postgres

class CRUDBase:
    def __init__(self):
        self.conn = connect_postgres()

    def refresh_conn(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
        except:
            self.conn = connect_postgres()

    def fetch_all(self, table: str, order_by: str = "id", schema: str = "ref") -> pd.DataFrame:
        self.refresh_conn()
        return pd.read_sql(f"SELECT * FROM {schema}.{table} ORDER BY {order_by}", self.conn)

    def fetch_unique(self, table: str, column: str) -> List[str]:
        self.refresh_conn()
        df = pd.read_sql(f"SELECT DISTINCT {column} FROM ref.{table} ORDER BY {column}", self.conn)
        return df[column].dropna().tolist()

    def execute_query(self, query: str, params: tuple) -> tuple:
        self.refresh_conn()
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
            return True, "Succès"
        except psycopg2.Error as e:
            self.conn.rollback()
            return False, str(e)

# --- Formations ---
def get_formations():
    return CRUDBase().fetch_all("formation", "id")

def add_formation(intitule, niveau, section, session, cout):
    query = "INSERT INTO ref.formation (intitule, niveau, section, session, cout) VALUES (%s, %s, %s, %s, %s)"
    return CRUDBase().execute_query(query, (intitule, niveau, section, session, cout))

def update_formation(form_id, intitule, niveau, section, session, cout):
    query = "UPDATE ref.formation SET intitule=%s, niveau=%s, section=%s, session=%s, cout=%s WHERE id=%s"
    return CRUDBase().execute_query(query, (intitule, niveau, section, session, cout, form_id))

def delete_formation(form_id):
    query = "DELETE FROM ref.formation WHERE id=%s"
    return CRUDBase().execute_query(query, (form_id,))

# --- Étudiants ---
def get_etudiants():
    query = """
        SELECT e.*, f.intitule as formation_nom 
        FROM ref.etudiant e
        LEFT JOIN ref.formation f ON e.formation_id = f.id
        ORDER BY e.numero_et
    """
    return pd.read_sql(query, connect_postgres())

def add_etudiant(numero_et, nom, prenom, date_n, nat, formation_id):
    query = "INSERT INTO ref.etudiant (numero_et, nom, prenom, date_naissance, nationalite, formation_id) VALUES (%s, %s, %s, %s, %s, %s)"
    return CRUDBase().execute_query(query, (numero_et, nom, prenom, date_n, nat, formation_id))

def update_etudiant(numero_et, nom, prenom, date_n, nat, formation_id):
    query = "UPDATE ref.etudiant SET nom=%s, prenom=%s, date_naissance=%s, nationalite=%s, formation_id=%s WHERE numero_et=%s"
    return CRUDBase().execute_query(query, (nom, prenom, date_n, nat, formation_id, numero_et))

def delete_etudiant(numero_et):
    query = "DELETE FROM ref.etudiant WHERE numero_et=%s"
    return CRUDBase().execute_query(query, (numero_et,))

# --- Enseignants ---
def get_enseignants():
    return CRUDBase().fetch_all("enseignant", "numero_ens")

def add_enseignant(numero_ens, nom, prenom, date_n, nat):
    query = "INSERT INTO ref.enseignant (numero_ens, nom, prenom, date_naissance, nationalite) VALUES (%s, %s, %s, %s, %s)"
    return CRUDBase().execute_query(query, (numero_ens, nom, prenom, date_n, nat))

def update_enseignant(numero_ens, nom, prenom, date_n, nat):
    query = "UPDATE ref.enseignant SET nom=%s, prenom=%s, date_naissance=%s, nationalite=%s WHERE numero_ens=%s"
    return CRUDBase().execute_query(query, (nom, prenom, date_n, nat, numero_ens))

def delete_enseignant(numero_ens):
    query = "DELETE FROM ref.enseignant WHERE numero_ens=%s"
    return CRUDBase().execute_query(query, (numero_ens,))

# --- Cours ---
def get_cours():
    query = """
        SELECT c.*, f.intitule as formation_nom, e.nom as ens_nom 
        FROM ref.cours c
        LEFT JOIN ref.formation f ON c.formation_id = f.id
        LEFT JOIN ref.enseignant e ON c.enseignant_id = e.numero_ens
        ORDER BY c.id
    """
    return pd.read_sql(query, connect_postgres())

def add_cours(intitule, session, formation_id, enseignant_id):
    query = "INSERT INTO ref.cours (intitule, session, formation_id, enseignant_id) VALUES (%s, %s, %s, %s)"
    return CRUDBase().execute_query(query, (intitule, session, formation_id, enseignant_id))

def update_cours(cours_id, intitule, session, formation_id, enseignant_id):
    query = "UPDATE ref.cours SET intitule=%s, session=%s, formation_id=%s, enseignant_id=%s WHERE id=%s"
    return CRUDBase().execute_query(query, (intitule, session, formation_id, enseignant_id, cours_id))

def delete_cours(cours_id):
    query = "DELETE FROM ref.cours WHERE id=%s"
    return CRUDBase().execute_query(query, (cours_id,))

# --- Planning ---
def get_planning(conn=None):
    query = """
        SELECT p.*, c.intitule as cours_nom 
        FROM ref.planning p 
        JOIN ref.cours c ON p.cours_id = c.id 
        ORDER BY p.jour_semaine, p.heure_debut
    """
    if conn is None:
        conn = connect_postgres()
    return pd.read_sql(query, conn)

def add_planning(cours_id, jour_semaine, heure_debut, heure_fin, salle):
    query = "INSERT INTO ref.planning (cours_id, jour_semaine, heure_debut, heure_fin, salle) VALUES (%s, %s, %s, %s, %s)"
    return CRUDBase().execute_query(query, (cours_id, jour_semaine, heure_debut, heure_fin, salle))

def update_planning(plan_id, cours_id, jour_semaine, heure_debut, heure_fin, salle):
    query = "UPDATE ref.planning SET cours_id=%s, jour_semaine=%s, heure_debut=%s, heure_fin=%s, salle=%s WHERE id=%s"
    return CRUDBase().execute_query(query, (cours_id, jour_semaine, heure_debut, heure_fin, salle, plan_id))

def delete_planning(plan_id):
    query = "DELETE FROM ref.planning WHERE id=%s"
    return CRUDBase().execute_query(query, (plan_id,))

# --- Inscriptions ---
def get_inscriptions():
    query = """
        SELECT i.*, e.nom as et_nom, e.prenom as et_prenom, f.intitule as formation_nom, f.session as formation_session
        FROM ref.inscription i
        JOIN ref.etudiant e ON i.id_etudiant = e.numero_et
        JOIN ref.formation f ON i.id_formation = f.id
    """
    return pd.read_sql(query, connect_postgres())

def add_inscription(id_etudiant, id_formation, date_inscription):
    # Enforce session constraint: one formation per session per student
    conn = connect_postgres()
    try:
        with conn.cursor() as cur:
            # Get session of the new formation
            cur.execute("SELECT session FROM ref.formation WHERE id = %s", (id_formation,))
            res = cur.fetchone()
            if not res: return False, "Formation introuvable"
            new_session = res[0]
            
            # Check if student already has a formation in this session
            cur.execute("""
                SELECT f.intitule 
                FROM ref.inscription i 
                JOIN ref.formation f ON i.id_formation = f.id 
                WHERE i.id_etudiant = %s AND f.session = %s
            """, (id_etudiant, new_session))
            existing = cur.fetchone()
            if existing:
                return False, f"L'étudiant est déjà inscrit à la formation '{existing[0]}' pour la session {new_session}."
            
            # Perform insertion
            cur.execute(
                "INSERT INTO ref.inscription (id_etudiant, id_formation, date_inscription) VALUES (%s, %s, %s)",
                (id_etudiant, id_formation, date_inscription)
            )
        conn.commit()
        return True, "Inscription effectuée"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_inscription(id_etudiant, id_formation):
    query = "DELETE FROM ref.inscription WHERE id_etudiant=%s AND id_formation=%s"
    return CRUDBase().execute_query(query, (id_etudiant, id_formation))

# --- Paiements ---
def get_paiements():
    query = """
        SELECT p.*, e.nom as et_nom, e.prenom as et_prenom, f.intitule as formation_nom
        FROM ref.paiement p
        JOIN ref.etudiant e ON p.id_etudiant = e.numero_et
        JOIN ref.formation f ON p.id_formation = f.id
    """
    return pd.read_sql(query, connect_postgres())

def add_paiement(id_etudiant, id_formation, montant):
    query = "INSERT INTO ref.paiement (id_etudiant, id_formation, paiement) VALUES (%s, %s, %s)"
    return CRUDBase().execute_query(query, (id_etudiant, id_formation, montant))

def update_paiement(id_etudiant, id_formation, montant):
    query = "UPDATE ref.paiement SET paiement=%s WHERE id_etudiant=%s AND id_formation=%s"
    return CRUDBase().execute_query(query, (montant, id_etudiant, id_formation))

def delete_paiement(id_etudiant, id_formation):
    query = "DELETE FROM ref.paiement WHERE id_etudiant=%s AND id_formation=%s"
    return CRUDBase().execute_query(query, (id_etudiant, id_formation))
