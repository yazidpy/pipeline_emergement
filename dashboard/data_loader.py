import pandas as pd
from typing import Optional
from datetime import date
from utils.db import connect_postgres

def get_total_unique_students(conn) -> int:
    query = "SELECT COUNT(*) FROM ref.etudiant"
    res = pd.read_sql(query, conn)
    return int(res.iloc[0, 0]) if not res.empty else 0

def load_presence_stats(conn, date_debut: date, date_fin: date) -> pd.DataFrame:
    query = """
        SELECT gpc.date_jour, gpc.session, c.intitule,
               e.nom as enseignant_nom, e.prenom as enseignant_prenom,
               gpc.nb_inscrits, gpc.nb_presents, gpc.taux_presence, c.section
        FROM gold.presence_par_cours gpc
        JOIN ref.cours c ON gpc.cours_id = c.id
        JOIN ref.enseignant e ON c.enseignant_id = e.numero_ens
        WHERE gpc.date_jour BETWEEN %s AND %s
        ORDER BY gpc.date_jour DESC, gpc.session, c.intitule
    """
    return pd.read_sql(query, conn, params=(date_debut, date_fin))

def load_etudiant_stats(conn, date_debut: date, date_fin: date, formation_id: Optional[int] = None) -> pd.DataFrame:
    params = [date_debut, date_fin]
    filter_sql = ""
    if formation_id is not None:
        filter_sql = "AND et.formation_id = %s"
        params.append(formation_id)

    query = f"""
        SELECT gpe.numero_et, et.nom, et.prenom, et.filiere, et.niveau,
               COUNT(*) as nb_cours_total,
               SUM(CASE WHEN gpe.present = True THEN 1 ELSE 0 END) as nb_presences,
               ROUND(SUM(CASE WHEN gpe.present = True THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_presence_etudiant
        FROM gold.presence_par_etudiant gpe
        JOIN ref.etudiant et ON gpe.numero_et = et.numero_et
        WHERE gpe.date_jour BETWEEN %s AND %s {filter_sql}
        GROUP BY gpe.numero_et, et.nom, et.prenom, et.filiere, et.niveau
        ORDER BY taux_presence_etudiant ASC
    """
    return pd.read_sql(query, conn, params=tuple(params))

def load_absences_alertes(conn, date_debut: date, date_fin: date, formation_id: Optional[int] = None) -> pd.DataFrame:
    params = [date_debut, date_fin]
    filter_sql = ""
    if formation_id is not None:
        filter_sql = "AND et.formation_id = %s"
        params.append(formation_id)

    query = f"""
        SELECT gar.numero_et, et.nom, et.prenom, et.filiere, gar.date_jour,
               gar.nb_absences_consecutives, gar.seuil
        FROM gold.absences_repetees gar
        JOIN ref.etudiant et ON gar.numero_et = et.numero_et
        WHERE gar.date_jour BETWEEN %s AND %s {filter_sql}
        ORDER BY gar.date_jour DESC, gar.nb_absences_consecutives DESC
    """
    return pd.read_sql(query, conn, params=tuple(params))

def load_retour_feuilles(conn, date_debut: date, date_fin: date) -> pd.DataFrame:
    query = """
        SELECT grf.date_jour, grf.session, e.nom as enseignant_nom, e.prenom as enseignant_prenom,
               grf.nb_attendus, grf.nb_recus, grf.taux_retour
        FROM gold.retour_feuilles grf
        JOIN ref.enseignant e ON grf.enseignant_id = e.numero_ens
        WHERE grf.date_jour BETWEEN %s AND %s
        ORDER BY grf.date_jour DESC, grf.session
    """
    return pd.read_sql(query, conn, params=(date_debut, date_fin))

def load_ia_scoring(conn) -> pd.DataFrame:
    query = """
        SELECT se.numero_et, et.nom, et.prenom, f.intitule as formation_nom, f.niveau,
               se.score_serieux, se.badge
        FROM gold.scoring_etudiants se
        JOIN ref.etudiant et ON se.numero_et = et.numero_et
        JOIN ref.formation f ON et.formation_id = f.id
        ORDER BY se.score_serieux DESC
    """
    return pd.read_sql(query, conn)
