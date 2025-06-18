# Application de Gestion Scolaire

Une application de bureau développée pour simplifier la gestion des étudiants, des formations, des notes et des inscriptions au sein d'un établissement scolaire.



## Fonctionnalités

* Système d'authentification sécurisé avec 3 niveaux de rôles (Administrateur, Responsable, Secrétaire).
* Gestion complète (CRUD) des Départements, Formations, Années Académiques et Matières.
* Module de gestion des Étudiants : création, modification, suppression et inscription à une formation pour une année donnée.
* Interface intuitive pour la saisie des notes (contrôles, examens, rattrapages).
* Calcul automatique des moyennes et du statut de validation des matières.
* Consultation des bulletins de notes par étudiant et par année académique.

`Par défaut, il extse trois utilisateur avec des mots de passe définir par défaut:
    **responsable1**: resppass
    **admin**: adminpass
    **secretaire1**: secpass
`

## Technologies Utilisées

* **Langage :** Python 3
* **Interface Graphique :** PySide6 (Qt for Python)
* **Base de Données :** SQLite 3

## Installation et Lancement

1.  **Cloner le dépôt (ou télécharger le ZIP) :**
    ```sh
    git clone https://github.com/rudolf-k-hounlete/Gestions-des-etudiants-et-des-notes.git
    cd Gestions-des-etudiants-et-des-notes
    ```

2.  **Installer les dépendances :**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Lancer l'application :**
    ```sh
    python3 main.py
    ```
