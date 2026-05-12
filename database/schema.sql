-- SCHEMA DEFINITIONS (AUTO-GENERATED FROM ACTUAL DB STATE)
CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- =========
-- ref.*
-- =========
CREATE TABLE IF NOT EXISTS ref.cours (
  id INTEGER NOT NULL DEFAULT nextval('ref.cours_id_seq'::regclass),
  intitule TEXT NOT NULL,
  section TEXT NOT NULL,
  horaire TEXT NOT NULL,
  session TEXT NOT NULL,
  enseignant_id TEXT NOT NULL,
  formation_id INTEGER
);

CREATE TABLE IF NOT EXISTS ref.enseignant (
  id INTEGER NOT NULL DEFAULT nextval('ref.enseignant_id_seq'::regclass),
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  numero_ens TEXT,
  date_naissance DATE,
  nationalite TEXT
);

CREATE TABLE IF NOT EXISTS ref.etudiant (
  numero_et TEXT NOT NULL,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  filiere TEXT NOT NULL,
  niveau TEXT NOT NULL,
  date_naissance DATE,
  nationalite TEXT,
  formation_id INTEGER
);

CREATE TABLE IF NOT EXISTS ref.formation (
  id INTEGER NOT NULL DEFAULT nextval('ref.formation_id_seq'::regclass),
  intitule TEXT NOT NULL,
  niveau TEXT,
  section TEXT,
  session TEXT,
  cout NUMERIC DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ref.inscription (
  id_etudiant TEXT NOT NULL,
  id_formation INTEGER NOT NULL,
  date_inscription DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS ref.paiement (
  id_etudiant TEXT NOT NULL,
  id_formation INTEGER NOT NULL,
  paiement NUMERIC DEFAULT 0,
  reste_a_payer NUMERIC DEFAULT 0,
  PRIMARY KEY (id_etudiant, id_formation)
);

CREATE TABLE IF NOT EXISTS ref.pipeline_logs (
  id BIGINT NOT NULL DEFAULT nextval('ref.pipeline_logs_id_seq'::regclass),
  ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  dag_id TEXT,
  task_id TEXT,
  run_id TEXT,
  session TEXT,
  date_jour DATE,
  status TEXT,
  message TEXT
);

CREATE TABLE IF NOT EXISTS ref.planning (
  id INTEGER NOT NULL DEFAULT nextval('ref.planning_id_seq'::regclass),
  cours_id INTEGER NOT NULL,
  jour_semaine TEXT NOT NULL,
  heure_debut TIME WITHOUT TIME ZONE NOT NULL,
  heure_fin TIME WITHOUT TIME ZONE NOT NULL,
  salle CHARACTER VARYING DEFAULT 'Salle 101'::character varying
);

-- =========
-- bronze.*
-- =========
CREATE TABLE IF NOT EXISTS bronze.emargement_raw (
  id BIGINT NOT NULL DEFAULT nextval('bronze.emargement_raw_id_seq'::regclass),
  date_jour DATE NOT NULL,
  session TEXT NOT NULL,
  cours_id INTEGER NOT NULL,
  etudiant_nom TEXT,
  etudiant_prenom TEXT,
  present TEXT,
  remarque TEXT,
  fichier_source TEXT,
  ingested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- =========
-- silver.*
-- =========
CREATE TABLE IF NOT EXISTS silver.emargement_clean (
  id BIGINT NOT NULL DEFAULT nextval('silver.emargement_clean_id_seq'::regclass),
  date_jour DATE NOT NULL,
  session TEXT NOT NULL,
  cours_id INTEGER NOT NULL,
  numero_et TEXT,
  nom_complet TEXT,
  filiere TEXT,
  niveau TEXT,
  present BOOLEAN,
  present_raw TEXT,
  remarque TEXT,
  fichier_source TEXT,
  cleaned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- =========
-- gold.*
-- =========
CREATE TABLE IF NOT EXISTS gold.absences_repetees (
  numero_et TEXT NOT NULL,
  date_jour DATE NOT NULL,
  nb_absences_consecutives INTEGER NOT NULL,
  seuil INTEGER NOT NULL,
  flagged_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gold.presence_par_cours (
  cours_id INTEGER NOT NULL,
  date_jour DATE NOT NULL,
  session TEXT NOT NULL,
  nb_inscrits INTEGER NOT NULL,
  nb_presents INTEGER NOT NULL,
  taux_presence NUMERIC NOT NULL,
  computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gold.presence_par_etudiant (
  numero_et TEXT NOT NULL,
  date_jour DATE NOT NULL,
  session TEXT NOT NULL,
  cours_id INTEGER NOT NULL,
  present BOOLEAN,
  filiere TEXT,
  niveau TEXT,
  computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gold.retour_feuilles (
  enseignant_id TEXT NOT NULL,
  date_jour DATE NOT NULL,
  session TEXT NOT NULL,
  nb_attendus INTEGER NOT NULL,
  nb_recus INTEGER NOT NULL,
  taux_retour NUMERIC NOT NULL,
  computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gold.scoring_etudiants (
  numero_et TEXT NOT NULL,
  score_serieux NUMERIC,
  badge TEXT,
  last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

