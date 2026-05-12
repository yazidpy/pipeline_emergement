# 🎓 Plan de Présentation : Système d’Émargement Intelligent

Ce document détaille le contenu pour une présentation PowerPoint de **12 slides**.

---

## Slide 1 — Page de garde

### Objectif
Introduire le projet, l'interlocuteur et le cadre de la présentation.

### Contenu texte
*   **Titre :** Système d’Émargement Intelligent & Analytics
*   **Sous-titre :** Digitalisation, Automatisation et Pilotage de l'Assiduité Académique
*   **Présenté par :** [Votre Nom]
*   **Date :** 11 Mai 2024

### Points clés
*   Nom du projet : **SmartAcademy**
*   Focus sur la transformation digitale des processus administratifs.

### Visuels recommandés
*   Une image d'arrière-plan moderne en haute résolution : dashboard data/analytique avec des tons bleu nuit et blanc.
*   Logo de l'institut (si disponible).

### Conseils de présentation
*   Accueillir l'auditoire.
*   Poser le décor : "Comment transformer une corvée administrative en un levier de pilotage ?"

---

## Slide 2 — Contexte et problématique

### Objectif
Expliquer pourquoi ce projet est né et quelle douleur il vient soulager.

### Contenu texte
*   **Processus actuel :** Manuel, papier ou fichiers Excel hétérogènes.
*   **Pain Points :**
    *   Saisie chronophage et erreurs humaines (frappe, perte de données).
    *   Données silotées (pas de vue d'ensemble sur l'institut).
    *   Absence de réactivité face au décrochage étudiant.

### Points clés
*   Perte de temps administratif estimée à plusieurs heures par semaine.
*   Manque de traçabilité et de sécurité.

### Visuels recommandés
*   Infographie : **Avant vs Après**.
    *   *Gauche (Avant) :* Image d'une pile de papier ou d'un Excel chaotique.
    *   *Droite (Après) :* Icône de cloud, plateforme centralisée et clean.

### Conseils de présentation
*   Mettre l'accent sur le coût caché de la mauvaise gestion de la donnée.

---

## Slide 3 — Objectifs du projet

### Objectif
Présenter les résultats concrets attendus par la mise en place du système.

### Contenu texte
*   **Automatisation :** Génération et collecte "On-demand".
*   **Centralisation :** Un seul point de vérité (Single Source of Truth).
*   **Pilotage :** Tableaux de bord interactifs pour l'administration.
*   **Engagement :** Système de scoring pour motiver les étudiants.
*   **Sécurisation :** Authentification et traçabilité complète.

### Points clés
*   Zéro papier.
*   Zéro saisie manuelle pour l'administration.
*   Scoring de sérieux pré-configuré.

### Visuels recommandés
*   Liste à puces avec des icônes professionnelles (Checkmarks, Rocket, Shield).

### Conseils de présentation
*   "Notre but : Passer d'une gestion subie à une gestion proactive."

---

## Slide 4 — Architecture globale

### Objectif
Montrer la robustesse de la pile technologique sans entrer dans un détail excessif.

### Contenu texte
*   **Interfaces (UI) :** Streamlit (Dashboards Saas modernes).
*   **Orchestration :** Apache Airflow (Pipeline de données).
*   **Cœur de traitement :** Apache Spark (ETL haute performance).
*   **Stockage :** PostgreSQL 16 (Architecture Medallion : Bronze, Silver, Gold).
*   **Infrastructure :** Docker & Docker Compose pour la portabilité.

### Points clés
*   Stack Open Source de référence.
*   Scalabilité assurée par Spark et Docker.

### Visuels recommandés
*   **Schéma simplifié :**
    *   Utilisateurs → Streamlit → Airflow → Spark → PostgreSQL.

### Conseils de présentation
*   Rassurer sur la modernité et la pérennité des outils choisis.

---

## Slide 5 — Base de données

### Objectif
Démontrer la structuration intelligente des données.

### Contenu texte
*   **Modèle Medallion :**
    *   **Bronze :** Données brutes (Excel enseignants).
    *   **Silver :** Données normalisées et validées.
    *   **Gold :** KPIs agrégés (Scoring, Taux de présence).
*   **Référentiel :** Gestion centralisée des Etudiants, Cours, Formations et Plannings.

### Points clés
*   Séparation des préoccupations (Data Quality).
*   Indexation optimisée pour des dashboards rapides.

### Visuels recommandés
*   Mini-diagramme montrant les 3 couches (Bronze → Silver → Gold).
*   Capture d'écran simplifiée de quelques tables SQL clés.

### Conseils de présentation
*   Expliquer que la couche "Gold" est ce qui alimente directement les écrans de décision.

---

## Slide 6 — Workflow métier

### Objectif
Parcourir le cycle de vie d'une séance d'émargement.

### Contenu texte
1.  **Génération :** L'enseignant génère son template Excel sur le portail.
2.  **Remplissage :** Saisie rapide par l'enseignant (Présent O/N).
3.  **Upload :** Dépôt sécurisé du fichier sur le portail.
4.  **Pipeline :** Déclenchement automatique du traitement (Nettoyage/Agrégation).
5.  **Dashboard :** Mise à jour en temps réel des statistiques admin.

### Points clés
*   Flux 100% numérique.
*   Validation de format à l'upload.

### Visuels recommandés
*   Un diagramme linéaire avec des icônes (Excel → Flèche → Cloud → Flèche → Graphique).

### Conseils de présentation
*   Souligner la simplicité pour l'enseignant.

---

## Slide 7 — Pipeline Airflow

### Objectif
Zoom sur le "cerveau" automatique du projet.

### Contenu texte
*   **Orchestration :** Automatisation des tâches récurrentes.
*   **DAGs (Matin / Après-midi) :**
    *   Extraction des données Excel.
    *   Transformation via Spark (Jointures avec le référentiel).
    *   Calcul du Scoring et des alertes absences.
*   **Logs :** Traçabilité totale de chaque exécution.

### Points clés
*   Traitement asynchrone (pas de blocage de l'interface).
*   Gestion des erreurs robuste (Retries).

### Visuels recommandés
*   Capture d'écran de l'interface Airflow montrant un DAG avec ses tâches (nodes).

### Conseils de présentation
*   "L'orchestrateur garantit que les données sont fraîches chaque matin."

---

## Slide 8 — Dashboard Admin

### Objectif
Présenter l'outil de pilotage central.

### Contenu texte
*   **Pilotage de présence :** Taux global, par cours, par formation.
*   **Fiche 360° Étudiant :** Assiduité, score de sérieux, historique complet.
*   **Gestion CRUD :** Interface intuitive pour modifier le planning ou les étudiants.
*   **Export PDF :** Rapports officiels générés en un clic.

### Points clés
*   Vision macro et micro.
*   Aide à la décision immédiate.

### Visuels recommandés
*   Capture d'écran du Dashboard Admin (Onglet Présence ou Étudiants).
*   Zoom sur un graphique (Pie chart ou Bar chart).

### Conseils de présentation
*   Montrer comment un administrateur identifie un étudiant en retard de paiement ou en décrochage.

---

## Slide 9 — Portail Enseignant

### Objectif
Présenter l'interface simplifiée dédiée au terrain.

### Contenu texte
*   **Session Management :** Vue sur les cours du jour.
*   **Actions directes :**
    *   Bouton "Générer Excel" pré-rempli avec la liste d'appel.
    *   Zone d'upload sécurisée.
*   **Historique :** Accès aux séances passées et état du traitement.

### Points clés
*   UX minimaliste (Focus sur l'essentiel).
*   Autonomie totale de l'enseignant.

### Visuels recommandés
*   Capture d'écran du Portail Enseignant (Vue "Séances à venir").
*   Image du Badge de statut ("À remplir", "Traité").

### Conseils de présentation
*   "Un outil conçu pour ne pas déranger le cours, mais pour l'aider."

---

## Slide 10 — Docker et déploiement

### Objectif
Expliquer comment le système est déployé.

### Contenu texte
*   **Conteneurisation :** 6 containers interconnectés.
*   **Architecture stable :**
    *   PostgreSQL (Data)
    *   Redis (Message Broker)
    *   Airflow Scheduler/Webserver
    *   Apps Streamlit (Admin & Prof)
*   **Avantages :** Installation rapide (`docker compose up`), isolation et reproductibilité.

### Points clés
*   Zéro conflit de dépendances.
*   Prêt pour le Cloud (SaaS Ready).

### Visuels recommandés
*   Icône Docker avec des "boîtes" représentant les différents services.

### Conseils de présentation
*   Expliquer que le système peut tourner sur n'importe quel serveur en quelques minutes.

---

## Slide 11 — Difficultés et solutions

### Objectif
Montrer la maturité technique face aux imprévus.

### Contenu texte
*   **Challenge 1 :** Cohérence des contextes Spark.
    *   *Solution :* Centralisation via une session persistante et suppression des stops prématurés.
*   **Challenge 2 :** Validation des saisies Excel.
    *   *Solution :* En-tête enrichi (Header) et validation stricte lors de l'upload.
*   **Challenge 3 :** Performance UI/Data.
    *   *Solution :* Utilisation de cache (st.cache_data) et d'agrégats SQL Gold.

### Points clés
*   Amélioration continue du code.
*   Focus sur l'expérience utilisateur.

### Visuels recommandés
*   Tableau simple "Problème | Solution".

### Conseils de présentation
*   Démontrer que le projet a été testé et "éprouvé" par des itérations.

---

## Slide 12 — Conclusion

### Objectif
Terminer sur une note positive et ouvrir sur l'avenir.

### Contenu texte
*   **Résultats :** Un système opérationnel, robuste et élégant.
*   **Bénéfices :** Gain de temps, fiabilité des données, meilleure image de marque.
*   **Perspectives :**
    *   Application mobile native.
    *   Signature QR Code sur site.
    *   Intégration comptable.

### Points clés
*   Succès de la transition numérique.
*   Plateforme évolutive.

### Visuels recommandés
*   Une image inspirante (Étudiant diplômé ou équipe qui collabore).
*   Remerciements & Vos contacts.

### Conseils de présentation
*   Ouvrir la session de questions-réponses.
*   Réitérer la valeur ajoutée : "Plus qu'un outil d'émargement, un outil de réussite académique."
