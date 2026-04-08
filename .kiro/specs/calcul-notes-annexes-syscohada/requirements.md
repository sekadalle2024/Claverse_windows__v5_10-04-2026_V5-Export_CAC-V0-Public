# Requirements Document - Calcul Automatique des Notes Annexes SYSCOHADA Révisé

## Introduction

Ce document définit les exigences pour l'automatisation du calcul et du remplissage des 33 notes annexes des états financiers SYSCOHADA révisé. Le système doit lire les balances à 8 colonnes (exercices N, N-1, N-2), extraire les comptes pertinents selon le plan comptable SYSCOHADA, calculer les mouvements et soldes, puis générer des tableaux HTML conformes au format officiel de la liasse SYSCOHADA révisé.

## Glossary

- **SYSCOHADA**: Système Comptable Harmonisé de l'Organisation pour l'Harmonisation en Afrique du Droit des Affaires
- **Note_Annexe**: Document détaillé accompagnant les états financiers, numéroté de 1 à 33
- **Balance_8_Colonnes**: Fichier Excel contenant les comptes avec 8 colonnes (Numéro, Intitulé, Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit)
- **Exercice_N**: Exercice comptable en cours
- **Exercice_N1**: Exercice comptable précédent (N-1)
- **Exercice_N2**: Exercice comptable antérieur (N-2)
- **Calculateur_Note**: Script Python responsable du calcul d'une note annexe spécifique
- **Liasse_Officielle**: Template Excel contenant le format officiel des 33 notes annexes
- **Plan_Comptable_SYSCOHADA**: Référentiel des comptes comptables SYSCOHADA révisé
- **Solde_Ouverture**: Solde d'un compte au début de l'exercice
- **Solde_Cloture**: Solde d'un compte à la fin de l'exercice
- **Mouvement_Debit**: Somme des débits d'un compte pendant l'exercice
- **Mouvement_Credit**: Somme des crédits d'un compte pendant l'exercice
- **VNC**: Valeur Nette Comptable (Valeur brute - Amortissements)
- **Correspondances_JSON**: Fichier JSON mappant les postes des états financiers aux comptes comptables

## Requirements

### Requirement 1: Lecture des Balances Multi-Exercices

**User Story:** En tant qu'utilisateur, je veux que le système lise automatiquement les balances des exercices N, N-1 et N-2 depuis un fichier Excel, afin de disposer des données nécessaires au calcul des notes annexes.

#### Acceptance Criteria

1. WHEN un fichier Excel de balances est fourni, THE Balance_Reader SHALL détecter automatiquement les onglets "BALANCE N", "BALANCE N-1" et "BALANCE N-2"
2. WHEN les onglets sont détectés, THE Balance_Reader SHALL charger les 8 colonnes (Numéro, Intitulé, Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit) pour chaque exercice
3. IF un onglet requis est manquant, THEN THE Balance_Reader SHALL retourner un message d'erreur descriptif indiquant l'onglet manquant
4. THE Balance_Reader SHALL nettoyer les noms de colonnes en supprimant les espaces superflus
5. WHEN les données sont chargées, THE Balance_Reader SHALL convertir tous les montants en valeurs numériques (float)
6. IF une valeur est vide ou non numérique, THEN THE Balance_Reader SHALL la remplacer par 0.0
7. THE Balance_Reader SHALL afficher le nombre de lignes chargées pour chaque exercice

### Requirement 2: Extraction des Comptes par Racine

**User Story:** En tant qu'utilisateur, je veux que le système extraie les soldes des comptes selon leur numéro de racine, afin de regrouper les comptes pertinents pour chaque ligne de note annexe.

#### Acceptance Criteria

1. WHEN un numéro de compte racine est fourni (ex: "211"), THE Account_Extractor SHALL filtrer tous les comptes commençant par cette racine
2. WHEN un compte est trouvé, THE Account_Extractor SHALL extraire les 6 valeurs (Ant Débit, Ant Crédit, Débit, Crédit, Solde Débit, Solde Crédit)
3. IF aucun compte ne correspond à la racine, THEN THE Account_Extractor SHALL retourner des valeurs nulles (0.0) pour toutes les colonnes
4. THE Account_Extractor SHALL gérer les comptes avec plusieurs niveaux (ex: "2811", "28111")
5. WHEN plusieurs comptes partagent la même racine, THE Account_Extractor SHALL sommer leurs valeurs
6. THE Account_Extractor SHALL préserver la précision des montants sans arrondi prématuré

### Requirement 3: Calcul des Mouvements et Soldes

**User Story:** En tant qu'utilisateur, je veux que le système calcule automatiquement les soldes d'ouverture, les mouvements (augmentations, diminutions) et les soldes de clôture, afin de remplir les colonnes des notes annexes.

#### Acceptance Criteria

1. WHEN un compte est analysé, THE Movement_Calculator SHALL calculer le Solde_Ouverture comme (Solde Débit N-1 - Solde Crédit N-1)
2. WHEN un compte est analysé, THE Movement_Calculator SHALL calculer les Augmentations comme (Mouvement Débit N)
3. WHEN un compte est analysé, THE Movement_Calculator SHALL calculer les Diminutions comme (Mouvement Crédit N)
4. WHEN un compte est analysé, THE Movement_Calculator SHALL calculer le Solde_Cloture comme (Solde Débit N - Solde Crédit N)
5. THE Movement_Calculator SHALL vérifier la cohérence: Solde_Cloture = Solde_Ouverture + Augmentations - Diminutions
6. IF la cohérence n'est pas respectée, THEN THE Movement_Calculator SHALL émettre un avertissement avec l'écart constaté
7. WHEN des comptes d'amortissement sont traités, THE Movement_Calculator SHALL inverser les signes (crédit = augmentation)

### Requirement 4: Calcul des Valeurs Nettes Comptables

**User Story:** En tant qu'utilisateur, je veux que le système calcule automatiquement les valeurs nettes comptables (VNC) en soustrayant les amortissements des valeurs brutes, afin de présenter les immobilisations à leur valeur nette.

#### Acceptance Criteria

1. WHEN une ligne d'immobilisation est calculée, THE VNC_Calculator SHALL calculer VNC_Ouverture = Brut_Ouverture - Amortissement_Ouverture
2. WHEN une ligne d'immobilisation est calculée, THE VNC_Calculator SHALL calculer VNC_Cloture = Brut_Cloture - Amortissement_Cloture
3. THE VNC_Calculator SHALL gérer les comptes de brut (classe 2X) et d'amortissement (classe 28X, 29X) séparément
4. WHEN les dotations aux amortissements sont calculées, THE VNC_Calculator SHALL les extraire des mouvements crédit des comptes 28X
5. WHEN les reprises d'amortissements sont calculées, THE VNC_Calculator SHALL les extraire des mouvements débit des comptes 28X
6. THE VNC_Calculator SHALL vérifier que VNC >= 0 pour toutes les lignes
7. IF VNC < 0, THEN THE VNC_Calculator SHALL émettre un avertissement de valeur anormale

### Requirement 5: Génération des Scripts de Calcul (Note 1 à Note 33)

**User Story:** En tant que développeur, je veux créer 33 scripts Python individuels (calculer_note_XX.py), afin de calculer chaque note annexe de manière modulaire et maintenable.

#### Acceptance Criteria

1. THE System SHALL créer un fichier calculer_note_XX.py pour chaque note (XX = 01 à 33)
2. WHEN un script est créé, THE Script_Generator SHALL inclure une classe CalculateurNoteXX avec les méthodes charger_balances(), calculer_note(), generer_html()
3. WHEN un script est créé, THE Script_Generator SHALL définir le mapping des comptes spécifique à la note dans un dictionnaire mapping_comptes
4. THE Script_Generator SHALL suivre la structure du modèle calculer_note_3a.py
5. WHEN un script est exécuté, THE Calculateur_Note SHALL lire le fichier de balance depuis le chemin relatif "../../P000 -BALANCE DEMO N_N-1_N-2.xlsx"
6. WHEN un script est exécuté, THE Calculateur_Note SHALL sauvegarder le fichier HTML dans le dossier "../Tests/test_note_XX.html"
7. THE Calculateur_Note SHALL afficher un résumé des calculs dans la console avec des indicateurs visuels (✓, ✗)

### Requirement 6: Génération des Fichiers HTML de Test

**User Story:** En tant qu'utilisateur, je veux visualiser chaque note annexe dans un fichier HTML formaté, afin de vérifier visuellement la conformité avec le format SYSCOHADA officiel.

#### Acceptance Criteria

1. THE System SHALL créer un fichier test_note_XX.html pour chaque note (XX = 01 à 33)
2. WHEN un fichier HTML est généré, THE HTML_Generator SHALL inclure un tableau avec les en-têtes conformes au format de la Liasse_Officielle
3. WHEN un fichier HTML est généré, THE HTML_Generator SHALL appliquer un style CSS avec bordures, couleurs d'en-tête et alternance de lignes
4. THE HTML_Generator SHALL formater les montants avec séparateur de milliers et 0 décimales
5. WHEN un fichier HTML est généré, THE HTML_Generator SHALL inclure une ligne de total en bas du tableau avec un style distinct
6. THE HTML_Generator SHALL utiliser la police Courier New pour les montants afin d'aligner les chiffres
7. WHEN un fichier HTML est ouvert dans un navigateur, THE HTML_Generator SHALL afficher un tableau responsive adapté à différentes tailles d'écran

### Requirement 7: Mapping des Comptes SYSCOHADA

**User Story:** En tant que développeur, je veux utiliser le fichier correspondances_syscohada.json pour mapper les postes aux comptes, afin de garantir la cohérence avec le plan comptable SYSCOHADA révisé.

#### Acceptance Criteria

1. THE System SHALL lire le fichier correspondances_syscohada.json au démarrage
2. WHEN un poste est recherché, THE Mapping_Manager SHALL retourner la liste des racines de comptes associées
3. THE Mapping_Manager SHALL gérer les 4 sections: bilan_actif, bilan_passif, charges, produits
4. WHEN une racine de compte est manquante dans le JSON, THE Mapping_Manager SHALL émettre un avertissement
5. THE Mapping_Manager SHALL permettre l'ajout de nouvelles correspondances sans modifier le code Python
6. WHEN le fichier JSON est invalide, THEN THE Mapping_Manager SHALL retourner un message d'erreur descriptif
7. THE Mapping_Manager SHALL valider que chaque racine de compte est une chaîne numérique valide

### Requirement 8: Gestion des Cas Particuliers

**User Story:** En tant qu'utilisateur, je veux que le système gère les cas où certains comptes n'existent pas dans la balance, afin d'éviter les erreurs et de produire des notes annexes complètes même avec des données partielles.

#### Acceptance Criteria

1. WHEN un compte n'existe pas dans la balance, THE System SHALL utiliser des valeurs nulles (0.0) sans interrompre le traitement
2. WHEN une balance d'exercice est manquante (N-2 par exemple), THE System SHALL continuer le calcul avec les exercices disponibles
3. IF tous les comptes d'une ligne sont à zéro, THEN THE System SHALL quand même afficher la ligne dans le tableau HTML
4. THE System SHALL distinguer entre "compte inexistant" et "compte à solde nul"
5. WHEN des comptes ont des soldes anormaux (débit et crédit simultanés), THE System SHALL émettre un avertissement
6. THE System SHALL logger tous les avertissements dans un fichier calcul_notes_warnings.log
7. WHEN le traitement est terminé, THE System SHALL afficher un résumé des avertissements émis

### Requirement 9: Export vers Excel

**User Story:** En tant qu'utilisateur, je veux exporter les notes annexes calculées vers un fichier Excel, afin de les intégrer dans la liasse fiscale officielle.

#### Acceptance Criteria

1. WHEN l'export est demandé, THE Excel_Exporter SHALL créer un fichier Excel avec un onglet par note annexe
2. WHEN un onglet est créé, THE Excel_Exporter SHALL reproduire la structure du tableau HTML (en-têtes, lignes, totaux)
3. THE Excel_Exporter SHALL formater les cellules de montants en format numérique avec séparateur de milliers
4. THE Excel_Exporter SHALL appliquer des bordures et des couleurs d'en-tête similaires au HTML
5. WHEN l'export est terminé, THE Excel_Exporter SHALL sauvegarder le fichier sous le nom "Notes_Annexes_Calculees_AAAAMMJJ.xlsx"
6. THE Excel_Exporter SHALL permettre l'export d'une seule note ou de toutes les notes en une fois
7. WHEN l'export échoue, THEN THE Excel_Exporter SHALL retourner un message d'erreur avec la cause de l'échec

### Requirement 10: Validation de la Cohérence Inter-Notes

**User Story:** En tant qu'utilisateur, je veux que le système valide la cohérence entre les différentes notes annexes, afin de détecter les incohérences dans les états financiers.

#### Acceptance Criteria

1. WHEN toutes les notes sont calculées, THE Coherence_Validator SHALL vérifier que le total des immobilisations (Notes 3A à 3E) correspond au bilan actif
2. WHEN toutes les notes sont calculées, THE Coherence_Validator SHALL vérifier que les dotations aux amortissements (Notes 3A à 3E) correspondent au compte de résultat
3. THE Coherence_Validator SHALL vérifier que les soldes de clôture N-1 correspondent aux soldes d'ouverture N
4. WHEN une incohérence est détectée, THEN THE Coherence_Validator SHALL générer un rapport d'écart avec les montants concernés
5. THE Coherence_Validator SHALL calculer un taux de cohérence global (pourcentage d'écarts < 1%)
6. WHEN le taux de cohérence est inférieur à 95%, THEN THE Coherence_Validator SHALL émettre une alerte critique
7. THE Coherence_Validator SHALL sauvegarder le rapport de cohérence dans un fichier rapport_coherence.html

### Requirement 11: Documentation et Tests

**User Story:** En tant que développeur, je veux une documentation complète et des tests automatisés, afin de faciliter la maintenance et l'évolution du système.

#### Acceptance Criteria

1. THE System SHALL créer un fichier README.md dans le dossier "Doc calcul notes annexes" expliquant l'architecture globale
2. WHEN un script est créé, THE System SHALL inclure des docstrings Python pour toutes les classes et méthodes
3. THE System SHALL créer un fichier GUIDE_UTILISATION.md avec des exemples d'utilisation pour chaque note
4. THE System SHALL créer un script test_all_notes.py qui exécute le calcul des 33 notes en séquence
5. WHEN test_all_notes.py est exécuté, THE System SHALL générer un rapport HTML récapitulatif avec le statut de chaque note
6. THE System SHALL créer un fichier TROUBLESHOOTING.md listant les erreurs courantes et leurs solutions
7. THE System SHALL inclure des exemples de balances de test dans le dossier "Tests/Balances_Test"

### Requirement 12: Performance et Optimisation

**User Story:** En tant qu'utilisateur, je veux que le calcul des 33 notes annexes soit rapide, afin de pouvoir générer les états financiers en moins de 30 secondes.

#### Acceptance Criteria

1. WHEN les 33 notes sont calculées, THE System SHALL terminer le traitement en moins de 30 secondes sur un ordinateur standard
2. THE System SHALL charger les balances une seule fois en mémoire et les réutiliser pour toutes les notes
3. THE System SHALL utiliser des structures de données optimisées (dictionnaires) pour l'accès aux comptes
4. WHEN un calcul est répété, THE System SHALL mettre en cache les résultats intermédiaires
5. THE System SHALL afficher une barre de progression lors du calcul des 33 notes
6. THE System SHALL permettre le calcul parallèle de plusieurs notes indépendantes
7. WHEN la mémoire disponible est insuffisante, THEN THE System SHALL traiter les notes en mode séquentiel avec libération de mémoire

### Requirement 13: Intégration avec l'Application Claraverse

**User Story:** En tant qu'utilisateur de Claraverse, je veux accéder au calcul des notes annexes depuis l'interface "Etat fin", afin d'avoir un workflow intégré pour les états financiers.

#### Acceptance Criteria

1. WHEN l'utilisateur clique sur "Calculer Notes Annexes" dans l'interface Etat fin, THE Backend SHALL appeler l'endpoint /api/calculer_notes_annexes
2. WHEN l'endpoint est appelé, THE Backend SHALL recevoir le fichier de balances uploadé par l'utilisateur
3. THE Backend SHALL exécuter le calcul des 33 notes et retourner un objet JSON avec les résultats
4. WHEN le calcul est terminé, THE Frontend SHALL afficher les notes annexes dans des accordéons cliquables
5. THE Frontend SHALL permettre l'export individuel de chaque note en HTML ou Excel
6. WHEN une erreur survient, THEN THE Frontend SHALL afficher un message d'erreur descriptif avec les détails techniques
7. THE Frontend SHALL afficher un indicateur de progression pendant le calcul des notes

### Requirement 14: Gestion des Formats de Balance Variables

**User Story:** En tant qu'utilisateur, je veux que le système accepte différents formats de balances (avec ou sans espaces dans les noms de colonnes), afin de gérer les exports de différents logiciels comptables.

#### Acceptance Criteria

1. WHEN une balance est chargée, THE Balance_Parser SHALL détecter automatiquement les variations de noms de colonnes ("Ant Débit", "Ant  Débit", "Ant    Débit")
2. THE Balance_Parser SHALL normaliser les noms de colonnes en supprimant les espaces multiples
3. WHEN les colonnes ont des noms différents, THE Balance_Parser SHALL utiliser un mapping flexible (ex: "Solde D" → "Solde Débit")
4. IF les colonnes essentielles sont manquantes, THEN THE Balance_Parser SHALL retourner un message d'erreur listant les colonnes manquantes
5. THE Balance_Parser SHALL accepter les formats de nombres avec virgule ou point comme séparateur décimal
6. THE Balance_Parser SHALL accepter les formats de nombres avec ou sans séparateur de milliers
7. WHEN le format de balance est non standard, THE Balance_Parser SHALL proposer un assistant de mapping manuel

### Requirement 15: Traçabilité et Audit

**User Story:** En tant qu'auditeur, je veux tracer l'origine de chaque montant dans les notes annexes, afin de vérifier la conformité des calculs.

#### Acceptance Criteria

1. WHEN une note annexe est générée, THE System SHALL créer un fichier trace_note_XX.json avec le détail des calculs
2. WHEN un montant est affiché, THE Trace_Manager SHALL enregistrer les comptes sources et leurs soldes
3. THE Trace_Manager SHALL enregistrer la date et l'heure de génération de chaque note
4. THE Trace_Manager SHALL enregistrer le nom du fichier de balance utilisé et son hash MD5
5. WHEN un utilisateur clique sur un montant dans le HTML, THE System SHALL afficher une popup avec le détail du calcul
6. THE System SHALL permettre l'export du fichier de trace en format CSV pour analyse dans Excel
7. THE System SHALL conserver l'historique des 10 dernières générations de chaque note

