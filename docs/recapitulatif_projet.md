# Récapitulatif Complet : Projet SmartAcademy

## 📝 1. Problématique
Dans de nombreux instituts de formation, la gestion de l'émargement reste un processus manuel, fastidieux et sujet aux erreurs :
- **Perte de temps** : Saisie manuelle des présences sur papier ou sur des fichiers Excel non structurés.
- **Données Silotées** : Difficulté à centraliser et à analyser l'assiduité sur l'ensemble de l'institut.
- **Manque de Visibilité** : Retards dans l'identification des étudiants en décrochage ou en situation irrégulière.
- **Sécurité Faible** : Absence de traçabilité et de signature numérique sur les feuilles de présence.

---

## 🎯 2. Objectifs du Projet
Ce projet a pour but de digitaliser et d'automatiser l'intégralité du cycle de vie de l'émargement :
1.  **Automatiser** la génération et la collecte des feuilles d'émargement.
2.  **Sécuriser** l'accès aux données par un système d'authentification centralisé.
3.  **Analyser** l'assiduité en temps réel via des dashboards interactifs.
4.  **Valoriser** les données par un algorithme de scoring (gamification) et des alertes automatiques.

---

## 🏗️ 3. Architecture de la Solution
Le système repose sur une architecture **Medallion** moderne pour garantir la qualité des données :
- **Bronze (Données Brutes)** : Collecte des fichiers Excel déposés par les enseignants sans altération.
- **Silver (Données Nettoyées)** : Normalisation, dédoublonnage et validation des données via Spark.
- **Gold (Données Métier)** : Agrégation et calcul des KPIs pour les dashboards.

---

## ✨ 4. Fonctionnalités Clés

### 👨‍🏫 Portail Enseignant (Gestion de Terrain)
- **Génération On-demand** : Création instantanée de feuilles Excel pré-remplies (ID, Noms, Prénoms).
- **Dépôt Sécurisé** : Drag & Drop des fichiers émargés avec validation automatique du format.
- **Suivi Historique** : Consultation des séances passées et de leur état de traitement (Traité / En attente).

### 🛡️ Dashboard Administration (Gouvernance)
- **Pilotage Global** : KPIs sur le taux de présence, nombre de cours et performance des enseignants.
- **Suivi Étudiant (Fiche 360°)** : Vue détaillée par élève incluant l'assiduité, le score de sérieux et la situation financière.
- **Export Officiel** : Génération de rapports d'assiduité au format PDF professionnel.
- **Alertes Décrochage** : Identification automatique des étudiants absents sur plusieurs séances consécutives.
- **Gestion du Référentiel** : CRUD complet sur les formations, les cours, les paiements et le planning.

### 🏆 Intelligence & Scoring
- **Algorithme de Sérieux** : Calcul d'un score sur 100 basé sur la régularité et les remarques.
- **Système de Badges** : Attribution de badges Or, Argent et Bronze pour encourager l'assiduité.

---

## 💻 5. Stack Technique
Une architecture robuste et scalable basée sur les standards de l'industrie :
- **Langage** : Python 3.11
- **Traitement de Données** : Apache Spark (PySpark)
- **Orchestration** : Apache Airflow
- **Base de Données** : PostgreSQL 16
- **Interfaces (UI/UX)** : Streamlit (Architecture SaaS moderne, CSS personnalisé)
- **Infrastructure** : Docker & Docker Compose (Multi-containeurs)
- **Sécurité** : Hachage SHA-256 (hashlib)

---

## 🚀 6. Résultats & Bénéfices
- **Gain de productivité** : Réduction drastique du temps administratif consacré à l'émargement.
- **Fiabilité à 100%** : Suppression des erreurs de saisie manuelle.
- **Décisions Data-Driven** : Intervention rapide auprès des étudiants en difficulté grâce aux alertes en temps réel.
- **Image Professionnelle** : Modernisation du service académique vis-à-vis des étudiants et des partenaires.

---
*Projet SmartAcademy — Système d'Émargement Intelligent & Analytics*
