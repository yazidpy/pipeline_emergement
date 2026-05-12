# Guide Utilisateur : Dashboard Administration (SaaS)

Ce guide décrit l'utilisation du **SmartAcademy Dashboard Admin**, l'interface centrale pour la gestion de l'institut et le suivi de l'émargement.

---

## 🔒 1. Accès & Sécurité

### Connexion
- **Lien** : `http://localhost:8501`
- **Authentification** : Saisissez votre identifiant et votre mot de passe (par défaut `admin` / `admin`).
- **Déconnexion** : Utilisez le bouton **🚪 Déconnexion** dans la barre latérale gauche.

### Gestion des Comptes
Les comptes administrateurs et enseignants sont gérés dans la base de données (table `ref.credentials`). Pour modifier un mot de passe ou ajouter un utilisateur, contactez le support technique.

---

## 📊 2. Tableau de Bord (Onglet : Présence)

L'onglet **Présence** offre une vue panoramique de l'assiduité.
- **KPIs** : Visualisez le nombre total de cours, le taux de présence moyen et le taux de retour des feuilles.
- **Filtres** : Utilisez la barre de filtres pour sélectionner une période précise.
- **Évolution** : Le graphique en barres montre la présence par semaine ou par mois, segmentée par session (Matin/Après-midi).
- **Performance Enseignants** : Suivez le taux de retour des feuilles par enseignant pour identifier les retards de collecte.

---

## 👨‍🎓 3. Suivi Académique (Onglet : Étudiants)

### Alertes Absences
La colonne de gauche affiche les étudiants en situation de décrochage (alertes rouges pour 5+ absences consécutives).

### Fiche Étudiant (Nouveau)
Consultez le dossier complet d'un étudiant en sélectionnant son nom dans le sous-onglet **🔍 Fiche Étudiant** :
- **Score de sérieux** : Note sur 100 calculée automatiquement.
- **Situation financière** : État des paiements et solde restant (Exprimé en **Euro €**).
- **Historique complet** : Liste de toutes les séances passées avec l'état de présence.

---

## 🎯 4. Analyse & Scoring (Onglet : Scoring)

Le système calcule chaque nuit le "Score de Sérieux" des étudiants.
- **Badges** : Or (90+), Argent (70+), Bronze (50+).
- **Comparaison** : Visualisez quelle formation est la plus assidue grâce au graphique linéaire.
- **Classement** : Le tableau affiche le Top 20 des étudiants les plus sérieux.

---

## ⚙️ 5. Centre de Gestion (Onglet : Administration)

C'est ici que vous gérez le référentiel de l'institut via les sous-onglets :

1.  **Formations** : Créer de nouvelles filières, définir les tarifs (en **€**).
2.  **Paiements** : Enregistrez les versements des étudiants (en **€**) et suivez les impayés.
3.  **Étudiants** : Inscrire manuellement de nouveaux élèves ou modifier leurs profils.
4.  **Enseignants** : Gestion du corps professoral.
5.  **Cours** : Catalogue des matières enseignées.
6.  **Planning** : Organisez les séances par jour et par salle. **Le bouton PDF permet de générer le planning du jour pour affichage.**
7.  **Inscriptions** : Gérez le rattachement des étudiants à leurs formations respectives.

---

## 🛠️ 6. Maintenance & Pipeline

- **Airflow** : Le traitement des données est automatisé. Si une donnée ne s'affiche pas, vérifiez que le portail enseignant a bien reçu les feuilles.
- **Exportation** : La plupart des tableaux peuvent être exportés en CSV en survolant le tableau Streamlit.

*© 2026 SmartAcademy Institute — Système d'Émargement Intelligent*
