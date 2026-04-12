## Système d’Émargement Intelligent — Golden Collar Institute

Projet **Data Engineering** (pipeline Bronze / Silver / Gold, Airflow, Spark, Streamlit), conforme au plan de travail du PDF.  
**Phases réalisées : 0 (infrastructure + BDD) et 1 (génération Excel).**

### Dossiers

- `dags/` — DAGs Airflow (matin / après-midi) — *à venir*
- `jobs/` — scripts pipeline : `generate.py` (Phase 1) ; collect, extract, transform, aggregate + `ia/` — *à venir*
- `database/` — `schema.sql` (schémas ref / bronze / silver / gold) et `seed_data.sql`
- `dashboard/` — application Streamlit — *à venir*
- `utils/` — connexion PostgreSQL (`db.py`), logging (`logger.py`)
- `data/` — Excel générés (`generated/`) et collectés (`collected/`) — ignoré par Git
- `models/` — modèles ML sérialisés (bonus)

### Prérequis

- Docker + Docker Compose
- Python 3.10+ (pour lancer les scripts en local)

### Phase 0 — Environnement

1. Copier `.env.example` vers `.env` et renseigner les identifiants PostgreSQL.
2. **Depuis ta machine (PowerShell / terminal)** : pour `generate.py`, utilise `POSTGRES_HOST=127.0.0.1` et le **port publié** (souvent `5433`, voir `POSTGRES_PUBLISH_PORT` dans le compose). Le hostname `postgres` ne fonctionne que **depuis les conteneurs** ; laisse `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` avec `@postgres:5432` pour Airflow.
3. Démarrer les services :

```bash
docker compose up -d
```

- Airflow : `http://localhost:8080` (login par défaut souvent `admin` / `admin` après init)
- Spark master UI : `http://localhost:8081`

PostgreSQL charge automatiquement `database/schema.sql` puis `database/seed_data.sql` au premier démarrage du volume.

### Phase 1 — Génération des feuilles Excel (`jobs/generate.py`)

Génère une feuille **par cours** du jour, avec les inscrits issus de `ref.*`, au format openpyxl.

**Installation des dépendances Python (hôte) :**

```bash
pip install -r requirements.txt
```

**Exemple d’exécution :**

```bash
python jobs/generate.py --session matin
python jobs/generate.py --session apres-midi --date 2026-04-06
```

- `--session` : `matin` ou `apres-midi` (aligné sur `ref.cours.session`).
- `--date` : optionnel, format `YYYY-MM-DD` ; par défaut : date du jour. Choisir un **jour ouvré** présent dans `seed_data.sql` / `ref.planning` (ex. lundi–vendredi), sinon aucun cours ne sera trouvé.

**Sortie :** `data/generated/<YYYY-MM-DD>/<session>/`, un fichier `.xlsx` par cours (nom incluant `_cours<id>` pour les phases suivantes).

### Prochaines étapes

- Phase 2 : `collect.py` (scan `data/collected/`, complétude, `gold.retour_feuilles`)
- Phases 3–5 : extract / transform / aggregate (PySpark → bronze / silver / gold)
- Phase 6 : dashboard Streamlit
- Orchestration : DAGs Airflow dans `dags/`
