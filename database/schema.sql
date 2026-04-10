-- Phase 0: Schémas & tables de base (ref/bronze/silver/gold)

CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Logs techniques (mentionnés dans le plan Airflow)
CREATE TABLE IF NOT EXISTS ref.pipeline_logs (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  dag_id TEXT NULL,
  task_id TEXT NULL,
  run_id TEXT NULL,
  session TEXT NULL,
  date_jour DATE NULL,
  status TEXT NULL,
  message TEXT NULL
);

-- =========
-- ref.*
-- =========
CREATE TABLE IF NOT EXISTS ref.etudiant (
  numero_et TEXT PRIMARY KEY,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  filiere TEXT NOT NULL,
  niveau TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref.enseignant (
  id SERIAL PRIMARY KEY,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref.cours (
  id SERIAL PRIMARY KEY,
  intitule TEXT NOT NULL,
  section TEXT NOT NULL,
  horaire TEXT NOT NULL,
  session TEXT NOT NULL CHECK (session IN ('matin', 'apres-midi')),
  enseignant_id INT NOT NULL REFERENCES ref.enseignant(id)
);

CREATE TABLE IF NOT EXISTS ref.planning (
  id SERIAL PRIMARY KEY,
  cours_id INT NOT NULL REFERENCES ref.cours(id),
  jour_semaine TEXT NOT NULL,
  heure_debut TIME NOT NULL,
  heure_fin TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS ref.inscription (
  id_etudiant TEXT NOT NULL REFERENCES ref.etudiant(numero_et),
  cours_id INT NOT NULL REFERENCES ref.cours(id),
  date_inscription DATE NOT NULL,
  PRIMARY KEY (id_etudiant, cours_id)
);

-- ============
-- bronze.*
-- ============
CREATE TABLE IF NOT EXISTS bronze.emargement_raw (
  id BIGSERIAL PRIMARY KEY,
  date_jour DATE NOT NULL,
  session TEXT NOT NULL CHECK (session IN ('matin', 'apres-midi')),
  cours_id INT NOT NULL,
  etudiant_nom TEXT NULL,
  etudiant_prenom TEXT NULL,
  present TEXT NULL,
  remarque TEXT NULL,
  fichier_source TEXT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============
-- silver.*
-- ============
CREATE TABLE IF NOT EXISTS silver.emargement_clean (
  id BIGSERIAL PRIMARY KEY,
  date_jour DATE NOT NULL,
  session TEXT NOT NULL CHECK (session IN ('matin', 'apres-midi')),
  cours_id INT NOT NULL REFERENCES ref.cours(id),
  numero_et TEXT NULL REFERENCES ref.etudiant(numero_et),
  nom_complet TEXT NULL,
  filiere TEXT NULL,
  niveau TEXT NULL,
  present BOOLEAN NULL,
  present_raw TEXT NULL,
  remarque TEXT NULL,
  fichier_source TEXT NULL,
  cleaned_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ==========
-- gold.*
-- ==========
CREATE TABLE IF NOT EXISTS gold.presence_par_cours (
  cours_id INT NOT NULL REFERENCES ref.cours(id),
  date_jour DATE NOT NULL,
  session TEXT NOT NULL CHECK (session IN ('matin', 'apres-midi')),
  nb_inscrits INT NOT NULL,
  nb_presents INT NOT NULL,
  taux_presence NUMERIC(5,2) NOT NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (cours_id, date_jour, session)
);

CREATE TABLE IF NOT EXISTS gold.presence_par_etudiant (
  numero_et TEXT NOT NULL REFERENCES ref.etudiant(numero_et),
  date_jour DATE NOT NULL,
  session TEXT NOT NULL CHECK (session IN ('matin', 'apres-midi')),
  cours_id INT NOT NULL REFERENCES ref.cours(id),
  present BOOLEAN NULL,
  filiere TEXT NULL,
  niveau TEXT NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (numero_et, date_jour, session, cours_id)
);

CREATE TABLE IF NOT EXISTS gold.absences_repetees (
  numero_et TEXT NOT NULL REFERENCES ref.etudiant(numero_et),
  date_jour DATE NOT NULL,
  nb_absences_consecutives INT NOT NULL,
  seuil INT NOT NULL,
  flagged_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (numero_et, date_jour)
);

CREATE TABLE IF NOT EXISTS gold.retour_feuilles (
  enseignant_id INT NOT NULL REFERENCES ref.enseignant(id),
  date_jour DATE NOT NULL,
  session TEXT NOT NULL CHECK (session IN ('matin', 'apres-midi')),
  nb_attendus INT NOT NULL,
  nb_recus INT NOT NULL,
  taux_retour NUMERIC(5,2) NOT NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (enseignant_id, date_jour, session)
);
