# 🤖 Prompt pour Générateur de Présentation IA

*C
---

## Instructions Générales
**Rôle :** Expert en Design de Présentations Business et Technique.
**Objectif :** Créer une présentation PowerPoint professionnelle de 12 slides pour le projet "SmartAcademy : Système d'Émargement Intelligent".
**Style :** Moderne, corporatif, tech, épuré. Couleurs : Bleu nuit, Blanc, Gris clair.
**Contraintes :** PAS d'IA ni de Machine Learning. Focus sur l'automatisation, la data engineering et l'efficacité administrative.

---

## Contenu des Slides

### Slide 1 : Titre
- **Titre :** SmartAcademy : Système d’Émargement Intelligent
- **Sous-titre :** Digitalisation et Pilotage de l'Assiduité Académique
- **Éléments :** [Votre Nom], Mai 2024.
- **Image suggérée :** Dashboard analytique élégant en arrière-plan.

### Slide 2 : Problématique
- **Titre :** Le défi de la gestion manuelle
- **Contenu :**
    - Saisie chronophage et erreurs humaines répétitives.
    - Données silotées (absence de vue d'ensemble).
    - Latence dans l'identification du décrochage étudiant.
- **Visual :** Comparaison "Avant (Chaos papier)" vs "Après (Fluidité digitale)".

### Slide 3 : Objectifs
- **Titre :** Nos Ambitions
- **Contenu :**
    - **Automatiser** la collecte (Zéro papier).
    - **Centraliser** les données (Une seule source de vérité).
    - **Valoriser** l'assiduité par le scoring (Gamification).
    - **Sécuriser** les accès (Traçabilité totale).

### Slide 4 : Architecture Technique
- **Titre :** Une Infrastructure Scalable
- **Contenu :**
    - **Interfaces :** Dashboards Streamlit (Admin & Enseignant).
    - **Orchestration :** Apache Airflow.
    - **Traitement :** Apache Spark (ETL).
    - **Data :** PostgreSQL (Architecture Medallion).
    - **Infrastructure :** Conteneurs Docker.

### Slide 5 : Stratégie de Données (Medallion)
- **Titre :** L'Architecture Medallion
- **Contenu :**
    - **Bronze :** Ingestion des fichiers bruts (Excel).
    - **Silver :** Nettoyage, normalisation et dédoublonnage.
    - **Gold :** Agrégation métier et scoring prêt à l'emploi.

### Slide 6 : Workflow Métier
- **Titre :** Un Cycle 100% Digital
- **Contenu :**
    1. Génération de template Excel sur mesure.
    2. Remplissage simplifié par l'enseignant.
    3. Upload et déclenchement du pipeline automatique.
    4. Analyse immédiate sur le dashboard admin.

### Slide 7 : Orchestration & Pipelines
- **Titre :** Le Cerveau du Système : Airflow
- **Contenu :**
    - Pipelines dédiés (Morning/Afternoon).
    - Enchaînement automatique : Extract → Transform → Aggregate → Score.
    - Gestion robuste des erreurs et monitoring en temps réel.

### Slide 8 : Dashboard Administration
- **Titre :** Pilotage Stratégique
- **Contenu :**
    - KPIs de présence globale et par formation.
    - Fiche 360° Étudiant (Historique, Paiements, Scoring).
    - Gestion CRUD du référentiel (Plannings, Cours).
    - Export de rapports PDF officiels.

### Slide 9 : Portail Enseignant
- **Titre :** Simplicité sur le Terrain
- **Contenu :**
    - Vue simplifiée des cours planifiés.
    - Génération et téléchargement d'Excel en un clic.
    - Zone de dépôt sécurisée avec validation instantanée.
    - Historique des feuilles traitées.

### Slide 10 : Déploiement Docker
- **Titre :** Stabilité & Portabilité
- **Contenu :**
    - Environnement multi-conteneurs (6 services synchronisés).
    - Déploiement rapide et sans conflit de dépendances.
    - Infrastructure prête pour le passage en Cloud/SaaS.

### Slide 11 : Retours d'Expérience
- **Titre :** Défis & Solutions Apportées
- **Contenu :**
    - **Défi :** Gestion des sessions Spark persistantes → **Solution :** Refonte de la logique de stop/start.
    - **Défi :** Intégrité des saisies Excel → **Solution :** Validation stricte "O/N" à l'upload.

### Slide 12 : Conclusion
- **Titre :** Vers une Académie Data-Driven
- **Contenu :**
    - Gain de productivité majeur.
    - Fiabilité des données garantie à 100%.
    - **Perspectives :** App Mobile, Signature QR Code, Intégration RH.

---
**Note pour l'IA :** Génère un visuel cohérent pour chaque slide en utilisant un thème "Business Technology Blue".
