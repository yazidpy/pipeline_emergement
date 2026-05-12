# Système d'Émargement Intelligent - SmartAcademy

Solution complète de gestion d'émargement, d'assiduité et de scoring pour les instituts de formation. 

---

## 🚀 Fonctionnalités Clés
- **Portail Enseignant** : Génération et dépôt sécurisé de feuilles d'émargement Excel.
- **Dashboard Admin** : Analyse Power BI (KPIs, Taux de présence, Alertes absences).
- **Scoring Automatique** : Calcul du sérieux et attribution de badges (Or, Argent, Bronze).
- **Architecture Medallion** : Pipeline de données Robuste (Bronze → Silver → Gold) via Spark & Airflow.
- **Sécurité** : Authentification centralisée pour tous les utilisateurs.

---

## 🛠️ Architecture Techniques
- **Backend** : Python 3.11, Apache Spark 3.5
- **Orchestration** : Apache Airflow
- **Base de Données** : PostgreSQL 16
- **Interfaces** : Streamlit (Dashboards SaaS)
- **Infrastructure** : Docker Multi-conteneurs

---

## 📂 Structure du Projet
```text
├── app_admin.py        # Dashboard Admin (Modulaire)
├── app_prof.py         # Portail Enseignant (Sécurisé)
├── dashboard/          # Composants UI, Charts et Views
├── dags/               # Pipelines Airflow (Ingestion & Scoring)
├── jobs/               # Traitements Spark (ETL)
├── docs/               # Documentation Utilisateur & Schéma BDD
├── database/           # Scripts d'initialisation SQL
└── utils/              # Sécurité (Auth), DB et PDF
```

---

## ⚙️ Installation & Lancement

1.  **Prérequis** : Docker & Docker Compose installés.
2.  **Configuration** : Copiez `.env.example` en `.env` et ajustez les variables.
3.  **Lancement** :
    ```bash
    docker compose up -d --build
    ```
4.  **Accès** :
    - **Admin** : `http://localhost:8501` (admin/admin ou yazid/Golden2024!)
    - **Portail Prof** : `http://localhost:8502`
    - **Airflow** : `http://localhost:8080` (admin/admin)

---

## 📖 Documentation Complète
Pour plus de détails, consultez les guides dans le dossier `/docs` :
- [Guide Administration](docs/guide_admin.md)
- [Guide Enseignants](docs/guide_prof.md)
- [Schéma Base de Données](docs/database_schema.md)

---

*Contact Support : IT Department - SmartAcademy Institute*
