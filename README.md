## Système d’Émargement Intelligent — Golden Collar Institute

Infrastructure (Phase 0)

### Dossiers
- `dags/`: DAGs Airflow (matin / après-midi)
- `jobs/`: scripts pipeline (generate/collect/extract/transform/aggregate + IA bonus)
- `database/`: schéma PostgreSQL + seed data
- `dashboard/`: application Streamlit
- `utils/`: utilitaires communs (DB, logging)
- `data/`: fichiers Excel générés / collectés (ignorés par git)
- `models/`: modèles ML sérialisés (bonus)

### Prochaines étapes
- Implémenter les scripts `jobs/` et les DAGs.

### Démarrage (Phase 0)
1) Copier `.env.example` en `.env` et ajuster si besoin.
2) Lancer les services:

```bash
docker compose up -d
```

- Airflow: `http://localhost:8080` (login `admin` / `admin`)
- Spark master UI: `http://localhost:8081`

PostgreSQL est initialisé automatiquement via `database/schema.sql` + `database/seed_data.sql`.
