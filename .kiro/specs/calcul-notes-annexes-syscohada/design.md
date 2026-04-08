# Design Document - Calcul Automatique des Notes Annexes SYSCOHADA Révisé

## Overview

Ce document présente la conception technique du système d'automatisation du calcul et du remplissage des 33 notes annexes des états financiers SYSCOHADA révisé. Le système est conçu comme une architecture modulaire composée de 33 scripts Python individuels, chacun responsable du calcul d'une note spécifique, s'appuyant sur des modules partagés pour la lecture des balances, l'extraction des comptes, les calculs et la génération de sorties HTML/Excel.

Le système lit des fichiers Excel de balances à 8 colonnes couvrant trois exercices comptables (N, N-1, N-2), extrait les comptes pertinents selon le plan comptable SYSCOHADA, effectue les calculs de mouvements et de soldes, puis génère des tableaux HTML conformes au format officiel de la liasse SYSCOHADA révisé. L'architecture privilégie la modularité, la maintenabilité et la performance, avec un objectif de traitement complet des 33 notes en moins de 30 secondes.

## Architecture

### Architecture Globale

Le système adopte une architecture en couches avec séparation claire des responsabilités:

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Claraverse                      │
│              (Frontend React + Backend Flask)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrateur Principal                     │
│              (calcul_notes_annexes_main.py)                  │
│  - Coordination des 33 calculateurs                          │
│  - Gestion du cache des balances                             │
│  - Validation de cohérence inter-notes                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Calculateur  │ │ Calculateur  │ │ Calculateur  │
│   Note 01    │ │   Note 02    │ │   Note 33    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Modules Partagés                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Balance    │  │   Account    │  │   Movement   │      │
│  │   Reader     │  │  Extractor   │  │  Calculator  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     VNC      │  │     HTML     │  │    Excel     │      │
│  │  Calculator  │  │  Generator   │  │   Exporter   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Mapping    │  │  Coherence   │  │    Trace     │      │
│  │   Manager    │  │  Validator   │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Données Sources                           │
│  - Balances Excel (N, N-1, N-2)                              │
│  - correspondances_syscohada.json                            │
│  - Liasse_officielle_revise.xlsx                             │
└─────────────────────────────────────────────────────────────┘
```

### Principes Architecturaux

1. **Modularité**: Chaque note annexe est calculée par un script indépendant suivant une structure commune
2. **Réutilisabilité**: Les modules partagés évitent la duplication de code
3. **Performance**: Chargement unique des balances en mémoire avec mise en cache
4. **Traçabilité**: Chaque calcul est tracé avec ses sources et métadonnées
5. **Robustesse**: Gestion gracieuse des erreurs et des données manquantes
6. **Extensibilité**: Ajout facile de nouvelles notes ou modifications du mapping

## Components and Interfaces

### 1. Balance_Reader

**Responsabilité**: Lecture et chargement des balances multi-exercices depuis Excel

**Interface**:
```python
class BalanceReader:
    def __init__(self, fichier_balance: str):
        """Initialise le lecteur avec le chemin du fichier Excel"""
        
    def charger_balances(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les 3 balances (N, N-1, N-2)
        
        Returns:
            Tuple de 3 DataFrames (balance_n, balance_n1, balance_n2)
            
        Raises:
            BalanceNotFoundException: Si un onglet requis est manquant
            InvalidBalanceFormatException: Si le format est invalide
        """
        
    def detecter_onglets(self, sheet_names: List[str]) -> Dict[str, str]:
        """
        Détecte automatiquement les onglets N, N-1, N-2
        
        Args:
            sheet_names: Liste des noms d'onglets du fichier Excel
            
        Returns:
            Dict mappant 'N', 'N-1', 'N-2' aux noms d'onglets détectés
        """
        
    def nettoyer_colonnes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les noms de colonnes (suppression espaces, normalisation)
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame avec colonnes nettoyées
        """
        
    def convertir_montants(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convertit tous les montants en float, remplace valeurs invalides par 0.0
        
        Args:
            df: DataFrame à convertir
            
        Returns:
            DataFrame avec montants convertis
        """
```

**Colonnes attendues dans les balances**:
- Numéro (str): Numéro de compte
- Intitulé (str): Libellé du compte
- Ant Débit (float): Solde débiteur d'ouverture
- Ant Crédit (float): Solde créditeur d'ouverture
- Débit (float): Mouvements débiteurs de l'exercice
- Crédit (float): Mouvements créditeurs de l'exercice
- Solde Débit (float): Solde débiteur de clôture
- Solde Crédit (float): Solde créditeur de clôture

### 2. Account_Extractor

**Responsabilité**: Extraction des soldes des comptes par racine

**Interface**:
```python
class AccountExtractor:
    def __init__(self, balance: pd.DataFrame):
        """Initialise l'extracteur avec une balance"""
        
    def extraire_solde_compte(self, numero_compte: str) -> Dict[str, float]:
        """
        Extrait les 6 valeurs d'un compte par sa racine
        
        Args:
            numero_compte: Racine du compte (ex: "211")
            
        Returns:
            Dict avec clés: ant_debit, ant_credit, mvt_debit, mvt_credit,
                           solde_debit, solde_credit
        """
        
    def extraire_comptes_multiples(self, racines: List[str]) -> Dict[str, float]:
        """
        Extrait et somme les soldes de plusieurs racines de comptes
        
        Args:
            racines: Liste de racines de comptes
            
        Returns:
            Dict avec les sommes des 6 valeurs
        """
        
    def filtrer_par_racine(self, racine: str) -> pd.DataFrame:
        """
        Filtre les comptes commençant par une racine
        
        Args:
            racine: Racine de compte
            
        Returns:
            DataFrame des comptes filtrés
        """
```

### 3. Movement_Calculator

**Responsabilité**: Calcul des mouvements et soldes avec validation de cohérence

**Interface**:
```python
class MovementCalculator:
    def calculer_solde_ouverture(self, solde_debit_n1: float, 
                                  solde_credit_n1: float) -> float:
        """Calcule le solde d'ouverture: Solde Débit N-1 - Solde Crédit N-1"""
        
    def calculer_augmentations(self, mvt_debit_n: float) -> float:
        """Calcule les augmentations: Mouvement Débit N"""
        
    def calculer_diminutions(self, mvt_credit_n: float) -> float:
        """Calcule les diminutions: Mouvement Crédit N"""
        
    def calculer_solde_cloture(self, solde_debit_n: float, 
                                solde_credit_n: float) -> float:
        """Calcule le solde de clôture: Solde Débit N - Solde Crédit N"""
        
    def verifier_coherence(self, solde_ouverture: float, augmentations: float,
                          diminutions: float, solde_cloture: float) -> Tuple[bool, float]:
        """
        Vérifie: Solde_Cloture = Solde_Ouverture + Augmentations - Diminutions
        
        Returns:
            Tuple (coherent: bool, ecart: float)
        """
        
    def calculer_mouvements_amortissement(self, compte_amort: str, 
                                          balance_n: pd.DataFrame) -> Dict[str, float]:
        """
        Calcule les mouvements d'amortissement (signes inversés)
        
        Returns:
            Dict avec clés: dotations (crédit), reprises (débit)
        """
```

### 4. VNC_Calculator

**Responsabilité**: Calcul des valeurs nettes comptables

**Interface**:
```python
class VNCCalculator:
    def calculer_vnc_ouverture(self, brut_ouverture: float, 
                               amort_ouverture: float) -> float:
        """Calcule VNC Ouverture = Brut Ouverture - Amortissement Ouverture"""
        
    def calculer_vnc_cloture(self, brut_cloture: float, 
                             amort_cloture: float) -> float:
        """Calcule VNC Clôture = Brut Clôture - Amortissement Clôture"""
        
    def extraire_dotations(self, comptes_amort: List[str], 
                          balance_n: pd.DataFrame) -> float:
        """Extrait les dotations aux amortissements (mouvements crédit 28X)"""
        
    def extraire_reprises(self, comptes_amort: List[str], 
                         balance_n: pd.DataFrame) -> float:
        """Extrait les reprises d'amortissements (mouvements débit 28X)"""
        
    def valider_vnc(self, vnc: float) -> Tuple[bool, str]:
        """
        Valide que VNC >= 0
        
        Returns:
            Tuple (valide: bool, message_avertissement: str)
        """
```

### 5. HTML_Generator

**Responsabilité**: Génération des fichiers HTML de visualisation

**Interface**:
```python
class HTMLGenerator:
    def __init__(self, titre_note: str, numero_note: str):
        """Initialise le générateur avec le titre et numéro de la note"""
        
    def generer_html(self, df: pd.DataFrame, colonnes_config: Dict) -> str:
        """
        Génère le HTML complet d'une note annexe
        
        Args:
            df: DataFrame avec les données de la note
            colonnes_config: Configuration des colonnes (en-têtes, groupes)
            
        Returns:
            Code HTML complet
        """
        
    def generer_entetes(self, colonnes_config: Dict) -> str:
        """Génère les en-têtes du tableau avec groupes et sous-colonnes"""
        
    def generer_lignes(self, df: pd.DataFrame) -> str:
        """Génère les lignes du tableau avec formatage des montants"""
        
    def formater_montant(self, montant: float) -> str:
        """Formate un montant: séparateur de milliers, 0 décimales"""
        
    def appliquer_style_css(self) -> str:
        """Retourne le CSS pour le tableau"""
```

### 6. Excel_Exporter

**Responsabilité**: Export des notes annexes vers Excel

**Interface**:
```python
class ExcelExporter:
    def __init__(self, fichier_sortie: str):
        """Initialise l'exporteur avec le nom du fichier de sortie"""
        
    def exporter_note(self, df: pd.DataFrame, nom_onglet: str, 
                     colonnes_config: Dict):
        """
        Exporte une note dans un onglet Excel
        
        Args:
            df: DataFrame de la note
            nom_onglet: Nom de l'onglet
            colonnes_config: Configuration des colonnes
        """
        
    def exporter_toutes_notes(self, notes: Dict[str, pd.DataFrame]):
        """
        Exporte toutes les notes dans un seul fichier Excel
        
        Args:
            notes: Dict mappant nom_note -> DataFrame
        """
        
    def appliquer_formatage(self, worksheet, colonnes_config: Dict):
        """Applique bordures, couleurs, formats numériques"""
        
    def sauvegarder(self):
        """Sauvegarde le fichier Excel"""
```

### 7. Mapping_Manager

**Responsabilité**: Gestion des correspondances SYSCOHADA

**Interface**:
```python
class MappingManager:
    def __init__(self, fichier_json: str = "correspondances_syscohada.json"):
        """Charge le fichier de correspondances"""
        
    def charger_correspondances(self) -> Dict:
        """
        Charge le fichier JSON
        
        Returns:
            Dict avec les 4 sections: bilan_actif, bilan_passif, charges, produits
            
        Raises:
            InvalidJSONException: Si le JSON est invalide
        """
        
    def obtenir_racines_compte(self, poste: str, section: str) -> List[str]:
        """
        Retourne les racines de comptes pour un poste
        
        Args:
            poste: Nom du poste (ex: "Immobilisations incorporelles")
            section: Section (bilan_actif, bilan_passif, charges, produits)
            
        Returns:
            Liste des racines de comptes
        """
        
    def valider_racines(self, racines: List[str]) -> Tuple[bool, List[str]]:
        """
        Valide que les racines sont des chaînes numériques valides
        
        Returns:
            Tuple (valide: bool, racines_invalides: List[str])
        """
        
    def ajouter_correspondance(self, poste: str, section: str, racines: List[str]):
        """Ajoute une nouvelle correspondance au mapping"""
```

### 8. Coherence_Validator

**Responsabilité**: Validation de la cohérence inter-notes

**Interface**:
```python
class CoherenceValidator:
    def __init__(self, notes: Dict[str, pd.DataFrame]):
        """Initialise le validateur avec toutes les notes calculées"""
        
    def valider_total_immobilisations(self) -> Tuple[bool, float]:
        """
        Vérifie que total Notes 3A-3E = Bilan Actif
        
        Returns:
            Tuple (coherent: bool, ecart: float)
        """
        
    def valider_dotations_amortissements(self) -> Tuple[bool, float]:
        """
        Vérifie que dotations Notes 3A-3E = Compte de Résultat
        
        Returns:
            Tuple (coherent: bool, ecart: float)
        """
        
    def valider_continuite_temporelle(self) -> Dict[str, Tuple[bool, float]]:
        """
        Vérifie que Solde Clôture N-1 = Solde Ouverture N pour toutes les notes
        
        Returns:
            Dict mappant nom_note -> (coherent: bool, ecart: float)
        """
        
    def calculer_taux_coherence(self) -> float:
        """
        Calcule le taux de cohérence global (% d'écarts < 1%)
        
        Returns:
            Taux de cohérence entre 0 et 100
        """
        
    def generer_rapport_coherence(self) -> str:
        """
        Génère un rapport HTML de cohérence
        
        Returns:
            Code HTML du rapport
        """
```

### 9. Trace_Manager

**Responsabilité**: Traçabilité et audit des calculs

**Interface**:
```python
class TraceManager:
    def __init__(self, numero_note: str):
        """Initialise le gestionnaire de traces pour une note"""
        
    def enregistrer_calcul(self, libelle: str, montant: float, 
                          comptes_sources: List[Dict]):
        """
        Enregistre un calcul avec ses sources
        
        Args:
            libelle: Libellé de la ligne
            montant: Montant calculé
            comptes_sources: Liste des comptes sources avec leurs soldes
        """
        
    def enregistrer_metadata(self, fichier_balance: str, hash_md5: str):
        """Enregistre les métadonnées de génération"""
        
    def sauvegarder_trace(self, fichier_sortie: str):
        """Sauvegarde la trace en JSON"""
        
    def exporter_csv(self, fichier_sortie: str):
        """Exporte la trace en CSV pour analyse Excel"""
        
    def gerer_historique(self, max_historique: int = 10):
        """Conserve les N dernières générations"""
```

### 10. Calculateur_Note (Template)

**Responsabilité**: Calcul d'une note annexe spécifique

**Interface** (structure commune à tous les calculateurs):
```python
class CalculateurNoteXX:
    def __init__(self, fichier_balance: str):
        """Initialise le calculateur avec le fichier de balances"""
        self.mapping_comptes = {...}  # Mapping spécifique à la note
        
    def charger_balances(self) -> bool:
        """Charge les 3 balances via Balance_Reader"""
        
    def calculer_ligne_note(self, libelle: str, comptes_brut: List[str],
                           comptes_amort: List[str]) -> Dict:
        """
        Calcule une ligne de la note
        
        Returns:
            Dict avec toutes les colonnes de la note
        """
        
    def generer_note(self) -> pd.DataFrame:
        """
        Génère la note complète avec toutes les lignes et le total
        
        Returns:
            DataFrame de la note
        """
        
    def generer_html(self, df: pd.DataFrame) -> str:
        """Génère le HTML de la note via HTML_Generator"""
        
    def sauvegarder_html(self, html: str, fichier_sortie: str):
        """Sauvegarde le fichier HTML"""
```

## Data Models

### Balance (DataFrame)

Structure d'une balance chargée en mémoire:

```python
{
    'Numéro': str,           # Numéro de compte (ex: "211", "2811")
    'Intitulé': str,         # Libellé du compte
    'Ant Débit': float,      # Solde débiteur d'ouverture
    'Ant Crédit': float,     # Solde créditeur d'ouverture
    'Débit': float,          # Mouvements débiteurs de l'exercice
    'Crédit': float,         # Mouvements créditeurs de l'exercice
    'Solde Débit': float,    # Solde débiteur de clôture
    'Solde Crédit': float    # Solde créditeur de clôture
}
```

### Ligne_Note_Annexe (Dict)

Structure d'une ligne de note annexe calculée:

```python
{
    'libelle': str,                  # Libellé de la ligne
    'brut_ouverture': float,         # Valeur brute d'ouverture
    'augmentations': float,          # Augmentations de l'exercice
    'diminutions': float,            # Diminutions de l'exercice
    'brut_cloture': float,           # Valeur brute de clôture
    'amort_ouverture': float,        # Amortissements d'ouverture
    'dotations': float,              # Dotations aux amortissements
    'reprises': float,               # Reprises d'amortissements
    'amort_cloture': float,          # Amortissements de clôture
    'vnc_ouverture': float,          # VNC d'ouverture
    'vnc_cloture': float             # VNC de clôture
}
```

### Correspondances_SYSCOHADA (JSON)

Structure du fichier correspondances_syscohada.json:

```json
{
    "bilan_actif": {
        "Immobilisations incorporelles": {
            "brut": ["211", "212", "213", "214", "215", "216", "217", "218"],
            "amort": ["2811", "2812", "2813", "2814", "2815", "2816", "2817", "2818",
                     "2911", "2912", "2913", "2914", "2915", "2916", "2917", "2918"]
        },
        "Immobilisations corporelles": {
            "brut": ["221", "222", "223", "224", "225", "226", "227", "228", "229"],
            "amort": ["2821", "2822", "2823", "2824", "2825", "2826", "2827", "2828", "2829",
                     "2921", "2922", "2923", "2924", "2925", "2926", "2927", "2928", "2929"]
        }
    },
    "bilan_passif": {
        "Capital": ["101", "102", "103", "104", "105"],
        "Réserves": ["111", "112", "113", "114", "115", "116", "117", "118"]
    },
    "charges": {
        "Achats de marchandises": ["601", "602", "603"],
        "Achats de matières premières": ["604", "605", "606"]
    },
    "produits": {
        "Ventes de marchandises": ["701", "702", "703"],
        "Ventes de produits finis": ["704", "705", "706"]
    }
}
```

### Trace_Calcul (JSON)

Structure d'un fichier de trace:

```json
{
    "note": "3A",
    "titre": "Immobilisations incorporelles",
    "date_generation": "2026-04-08T14:30:00",
    "fichier_balance": "P000 -BALANCE DEMO N_N-1_N-2.xlsx",
    "hash_md5_balance": "a1b2c3d4e5f6...",
    "lignes": [
        {
            "libelle": "Frais de recherche et de développement",
            "brut_ouverture": 1500000.0,
            "comptes_sources_brut": [
                {"compte": "211", "solde_debit_n1": 1500000.0, "solde_credit_n1": 0.0}
            ],
            "augmentations": 500000.0,
            "comptes_sources_augmentations": [
                {"compte": "211", "mvt_debit_n": 500000.0}
            ],
            "amort_ouverture": 300000.0,
            "comptes_sources_amort": [
                {"compte": "2811", "solde_credit_n1": 300000.0}
            ],
            "dotations": 200000.0,
            "comptes_sources_dotations": [
                {"compte": "2811", "mvt_credit_n": 200000.0}
            ]
        }
    ],
    "total": {
        "brut_ouverture": 5000000.0,
        "vnc_cloture": 3500000.0
    }
}
```

### Rapport_Coherence (Structure)

Structure du rapport de cohérence inter-notes:

```python
{
    'date_validation': datetime,
    'taux_coherence_global': float,  # Pourcentage 0-100
    'validations': {
        'total_immobilisations': {
            'coherent': bool,
            'total_notes': float,
            'total_bilan': float,
            'ecart': float,
            'ecart_pct': float
        },
        'dotations_amortissements': {
            'coherent': bool,
            'total_notes': float,
            'total_compte_resultat': float,
            'ecart': float,
            'ecart_pct': float
        },
        'continuite_temporelle': {
            'note_3a': {'coherent': bool, 'ecart': float},
            'note_3b': {'coherent': bool, 'ecart': float},
            # ... pour toutes les notes
        }
    },
    'alertes': [
        {
            'niveau': str,  # 'warning' ou 'critical'
            'message': str,
            'details': Dict
        }
    ]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Balance Loading Completeness

*For any* valid Excel file containing balance sheets, when the Balance_Reader loads the file, all three worksheets (BALANCE N, BALANCE N-1, BALANCE N-2) must be detected and loaded with exactly 8 columns each.

**Validates: Requirements 1.1, 1.2**

### Property 2: Column Name Normalization

*For any* balance sheet with column names containing multiple spaces, the Balance_Reader must normalize them to single-space format, and this normalization must be idempotent (normalizing twice produces the same result as normalizing once).

**Validates: Requirements 1.4**

### Property 3: Numeric Conversion Robustness

*For any* balance sheet loaded, all monetary values must be converted to float type, and any invalid or empty values must be replaced with 0.0 without raising exceptions.

**Validates: Requirements 1.5, 1.6**

### Property 4: Account Filtering by Root

*For any* account root number and any balance sheet, the Account_Extractor must return only accounts whose numbers start with that root, and the sum of filtered accounts must equal the sum of all matching accounts in the original balance.

**Validates: Requirements 2.1, 2.5**

### Property 5: Account Extraction Completeness

*For any* account found in a balance, the Account_Extractor must extract all 6 values (ant_debit, ant_credit, mvt_debit, mvt_credit, solde_debit, solde_credit) with their original precision preserved.

**Validates: Requirements 2.2, 2.6**

### Property 6: Missing Account Handling

*For any* account root that does not exist in a balance, the Account_Extractor must return a dictionary with all 6 values set to 0.0 without raising exceptions.

**Validates: Requirements 2.3, 8.1**

### Property 7: Accounting Equation Coherence

*For any* account analyzed, the Movement_Calculator must verify that: Solde_Cloture = Solde_Ouverture + Augmentations - Diminutions, where Solde_Ouverture = (Solde Débit N-1 - Solde Crédit N-1), Augmentations = Mouvement Débit N, Diminutions = Mouvement Crédit N, and Solde_Cloture = (Solde Débit N - Solde Crédit N).

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 8: Depreciation Account Sign Inversion

*For any* depreciation account (accounts starting with 28 or 29), the Movement_Calculator must treat credit movements as increases (dotations) and debit movements as decreases (reprises), which is the inverse of normal accounts.

**Validates: Requirements 3.7, 4.4, 4.5**

### Property 9: VNC Calculation Formula

*For any* fixed asset line, the VNC_Calculator must calculate VNC_Ouverture = Brut_Ouverture - Amortissement_Ouverture and VNC_Cloture = Brut_Cloture - Amortissement_Cloture, and both VNC values must be non-negative.

**Validates: Requirements 4.1, 4.2, 4.6**

### Property 10: Script Structure Conformity

*For any* generated calculer_note_XX.py script, it must contain a class CalculateurNoteXX with methods charger_balances(), calculer_note(), and generer_html(), and must define a mapping_comptes dictionary.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 11: HTML Generation Conformity

*For any* note annexe generated, the HTML_Generator must produce valid HTML containing a table with headers conforming to the official SYSCOHADA format, CSS styling with borders and alternating row colors, monetary amounts formatted with thousand separators and 0 decimals, and a total row with distinct styling.

**Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6**

### Property 12: Mapping Lookup Consistency

*For any* valid poste name in the correspondances_syscohada.json file, the Mapping_Manager must return the associated list of account roots, and adding new correspondences to the JSON must not require code changes.

**Validates: Requirements 7.2, 7.5, 7.7**

### Property 13: Graceful Degradation with Missing Data

*For any* balance sheet with missing accounts or missing exercise data (N-2), the system must continue processing and produce complete note annexes with zero values for missing data, without interrupting execution.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 14: Warning Logging Completeness

*For any* warning emitted during processing (incoherent balances, negative VNC, abnormal account balances), the system must log it to calcul_notes_warnings.log with timestamp and details.

**Validates: Requirements 3.6, 4.7, 8.5, 8.6**

### Property 15: Excel Export Structure Preservation

*For any* note annexe exported to Excel, the Excel_Exporter must create a worksheet with the same structure as the HTML table (headers, data rows, total row), with numeric formatting for amounts and styling (borders, header colors).

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

### Property 16: Inter-Note Coherence Validation

*For any* complete set of calculated notes, the Coherence_Validator must verify that: (1) total immobilizations from Notes 3A-3E equals the balance sheet actif, (2) total depreciation dotations from Notes 3A-3E equals the income statement, and (3) closing balances N-1 equal opening balances N for all notes.

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 17: Coherence Rate Calculation

*For any* set of coherence validations, the Coherence_Validator must calculate a global coherence rate as the percentage of validations with deviations < 1%, and must emit a critical alert if the rate is below 95%.

**Validates: Requirements 10.5, 10.6**

### Property 18: Performance Constraint

*For any* complete calculation of all 33 notes with a standard balance file, the system must complete processing in less than 30 seconds, loading balances only once into memory.

**Validates: Requirements 12.1, 12.2**

### Property 19: Calculation Caching

*For any* calculation that is repeated with the same input data, the system must return cached results, and the second execution must be significantly faster than the first.

**Validates: Requirements 12.4**

### Property 20: API Integration Round-Trip

*For any* balance file uploaded through the Claraverse interface, the backend endpoint /api/calculer_notes_annexes must receive the file, execute calculations, and return a JSON object containing all 33 notes, which the frontend must display in clickable accordions.

**Validates: Requirements 13.2, 13.3, 13.4**

### Property 21: Balance Format Flexibility

*For any* balance file with column name variations (multiple spaces, different separators), the Balance_Parser must automatically detect and normalize column names, and must accept both comma and period as decimal separators, with or without thousand separators.

**Validates: Requirements 14.1, 14.2, 14.3, 14.5, 14.6**

### Property 22: Calculation Traceability

*For any* note annexe generated, the Trace_Manager must create a trace_note_XX.json file containing: all calculated amounts with their source accounts and balances, generation timestamp, source balance file name and MD5 hash, and this trace must enable complete audit reconstruction of the calculation.

**Validates: Requirements 15.1, 15.2, 15.3, 15.4**

### Property 23: Trace History Management

*For any* note annexe generated multiple times, the system must maintain the 10 most recent trace files, automatically deleting older traces.

**Validates: Requirements 15.7**

### Property 24: Trace Export Format Conversion

*For any* trace file in JSON format, the system must be able to export it to CSV format preserving all calculation details for analysis in Excel.

**Validates: Requirements 15.6**

## Error Handling

### Error Categories

Le système gère quatre catégories d'erreurs avec des stratégies de traitement distinctes:

#### 1. Erreurs Critiques (Arrêt du Traitement)

Ces erreurs empêchent la poursuite du traitement et nécessitent une intervention:

- **BalanceNotFoundException**: Fichier de balance introuvable ou onglets requis manquants
  - Message: "Impossible de trouver l'onglet 'BALANCE N' dans le fichier Excel"
  - Action: Arrêt immédiat, affichage du message d'erreur à l'utilisateur
  - Logging: ERROR level avec stack trace complet

- **InvalidBalanceFormatException**: Format de balance non conforme (colonnes manquantes)
  - Message: "Colonnes manquantes dans la balance: ['Débit', 'Crédit']"
  - Action: Arrêt immédiat, liste des colonnes manquantes
  - Logging: ERROR level avec détails des colonnes attendues vs trouvées

- **InvalidJSONException**: Fichier correspondances_syscohada.json invalide ou corrompu
  - Message: "Fichier JSON invalide: erreur de syntaxe à la ligne 45"
  - Action: Arrêt immédiat, indication de la ligne problématique
  - Logging: ERROR level avec détails de l'erreur JSON

- **FilePermissionException**: Impossible d'écrire les fichiers de sortie
  - Message: "Permission refusée pour écrire dans le dossier Tests/"
  - Action: Arrêt immédiat, vérification des permissions
  - Logging: ERROR level avec chemin du fichier

#### 2. Avertissements (Continuation avec Logging)

Ces situations anormales permettent la continuation mais nécessitent une attention:

- **IncoherentBalanceWarning**: Équation comptable non respectée
  - Message: "Incohérence détectée pour le compte 211: écart de 1500.00"
  - Action: Continuation, émission d'un avertissement, logging
  - Logging: WARNING level avec détails de l'écart

- **NegativeVNCWarning**: Valeur nette comptable négative
  - Message: "VNC négative détectée pour 'Frais de recherche': -50000.00"
  - Action: Continuation, émission d'un avertissement, logging
  - Logging: WARNING level avec détails de la ligne

- **AbnormalAccountBalanceWarning**: Solde débiteur et créditeur simultanés
  - Message: "Compte 211 a des soldes débit (1000) et crédit (500) simultanés"
  - Action: Continuation, émission d'un avertissement, logging
  - Logging: WARNING level avec détails du compte

- **MissingAccountWarning**: Compte attendu absent de la balance
  - Message: "Compte 2811 non trouvé dans la balance N"
  - Action: Continuation avec valeur 0.0, logging
  - Logging: WARNING level

- **LowCoherenceRateWarning**: Taux de cohérence inter-notes < 95%
  - Message: "Taux de cohérence global: 92.5% (seuil: 95%)"
  - Action: Continuation, génération du rapport de cohérence
  - Logging: WARNING level avec détails des écarts

#### 3. Informations (Logging Uniquement)

Événements normaux du traitement:

- Chargement réussi des balances
- Nombre de lignes chargées par exercice
- Début/fin du calcul de chaque note
- Fichiers HTML/Excel générés avec succès
- Durée totale du traitement

#### 4. Erreurs de Validation (Retour à l'Utilisateur)

Erreurs liées aux données utilisateur:

- **EmptyBalanceException**: Balance vide ou sans données
  - Message: "La balance N ne contient aucune ligne de données"
  - Action: Arrêt, demande de vérification du fichier
  - Logging: ERROR level

- **InvalidAccountNumberException**: Numéro de compte invalide dans le mapping
  - Message: "Racine de compte invalide dans le JSON: 'ABC' (doit être numérique)"
  - Action: Arrêt, correction du fichier JSON requise
  - Logging: ERROR level

### Stratégies de Récupération

#### Récupération Automatique

Le système tente une récupération automatique dans ces cas:

1. **Compte manquant**: Utilisation de valeurs nulles (0.0) pour tous les montants
2. **Exercice N-2 manquant**: Calcul avec N et N-1 uniquement
3. **Valeur non numérique**: Conversion en 0.0 avec avertissement
4. **Colonne avec espaces multiples**: Normalisation automatique

#### Récupération Manuelle Requise

Ces situations nécessitent une intervention:

1. **Onglet de balance manquant**: Ajout de l'onglet au fichier Excel
2. **Colonnes essentielles manquantes**: Correction du format de balance
3. **JSON invalide**: Correction de la syntaxe JSON
4. **Permissions insuffisantes**: Modification des droits d'accès

### Logging et Traçabilité des Erreurs

#### Fichiers de Log

Le système génère trois fichiers de log:

1. **calcul_notes_annexes.log**: Log principal avec tous les niveaux (INFO, WARNING, ERROR)
2. **calcul_notes_warnings.log**: Uniquement les avertissements pour revue rapide
3. **calcul_notes_errors.log**: Uniquement les erreurs critiques

#### Format des Logs

```
[2026-04-08 14:30:15] [WARNING] [CalculateurNote3A] Incohérence détectée pour le compte 211
  Solde ouverture: 1500000.00
  Augmentations: 500000.00
  Diminutions: 200000.00
  Solde clôture attendu: 1800000.00
  Solde clôture réel: 1801500.00
  Écart: 1500.00 (0.08%)
```

#### Rotation des Logs

- Les fichiers de log sont conservés pendant 30 jours
- Rotation quotidienne avec horodatage
- Compression automatique des logs de plus de 7 jours

### Gestion des Erreurs dans l'API

Pour l'intégration Claraverse, l'endpoint /api/calculer_notes_annexes retourne des codes HTTP appropriés:

- **200 OK**: Calcul réussi, JSON avec les 33 notes
- **400 Bad Request**: Fichier de balance invalide ou format incorrect
- **404 Not Found**: Fichier de balance non trouvé
- **500 Internal Server Error**: Erreur interne du serveur
- **503 Service Unavailable**: Système surchargé, réessayer plus tard

Format de réponse d'erreur:

```json
{
    "success": false,
    "error": {
        "code": "INVALID_BALANCE_FORMAT",
        "message": "Colonnes manquantes dans la balance: ['Débit', 'Crédit']",
        "details": {
            "colonnes_attendues": ["Numéro", "Intitulé", "Ant Débit", "Ant Crédit", "Débit", "Crédit", "Solde Débit", "Solde Crédit"],
            "colonnes_trouvees": ["Numéro", "Intitulé", "Ant Débit", "Ant Crédit", "Solde Débit", "Solde Crédit"]
        }
    }
}
```

## Testing Strategy

### Dual Testing Approach

Le système utilise une approche de test duale combinant tests unitaires et tests basés sur les propriétés (property-based testing) pour garantir une couverture complète:

- **Tests unitaires**: Vérifient des exemples spécifiques, cas limites et conditions d'erreur
- **Tests basés sur propriétés**: Vérifient les propriétés universelles sur des milliers d'entrées générées aléatoirement

Cette approche complémentaire assure que:
- Les tests unitaires capturent les bugs concrets et les cas d'usage réels
- Les tests de propriétés vérifient la correction générale sur un large éventail d'entrées

### Property-Based Testing Configuration

#### Bibliothèque Choisie

**Hypothesis** (Python) sera utilisée pour les tests basés sur propriétés:
- Génération automatique de données de test
- Shrinking automatique pour trouver les cas minimaux d'échec
- Intégration native avec pytest
- Support des stratégies personnalisées pour les balances comptables

#### Configuration des Tests

Chaque test de propriété sera configuré avec:
- **Minimum 100 itérations** par test (paramètre `max_examples=100`)
- **Timeout de 60 secondes** par test pour éviter les blocages
- **Seed aléatoire enregistré** pour reproductibilité

#### Tagging des Tests

Chaque test de propriété doit référencer sa propriété de conception avec un tag:

```python
@given(balance=st_balance(), compte_racine=st.text(min_size=3, max_size=4))
@settings(max_examples=100)
def test_property_4_account_filtering_by_root(balance, compte_racine):
    """
    Feature: calcul-notes-annexes-syscohada
    Property 4: For any account root number and any balance sheet, 
    the Account_Extractor must return only accounts whose numbers 
    start with that root.
    """
    extractor = AccountExtractor(balance)
    filtered = extractor.filtrer_par_racine(compte_racine)
    
    # Vérifier que tous les comptes retournés commencent par la racine
    assert all(compte.startswith(compte_racine) for compte in filtered['Numéro'])
```

### Test Organization

#### Structure des Dossiers

```
py_backend/Doc calcul notes annexes/
├── Tests/
│   ├── unit/
│   │   ├── test_balance_reader.py
│   │   ├── test_account_extractor.py
│   │   ├── test_movement_calculator.py
│   │   ├── test_vnc_calculator.py
│   │   ├── test_html_generator.py
│   │   ├── test_excel_exporter.py
│   │   ├── test_mapping_manager.py
│   │   ├── test_coherence_validator.py
│   │   └── test_trace_manager.py
│   ├── property/
│   │   ├── test_properties_balance.py
│   │   ├── test_properties_extraction.py
│   │   ├── test_properties_calculation.py
│   │   ├── test_properties_coherence.py
│   │   └── test_properties_integration.py
│   ├── integration/
│   │   ├── test_note_3a_integration.py
│   │   ├── test_note_3b_integration.py
│   │   ├── ...
│   │   ├── test_all_notes_integration.py
│   │   └── test_api_integration.py
│   ├── fixtures/
│   │   ├── balance_demo_n_n1_n2.xlsx
│   │   ├── balance_incomplete.xlsx
│   │   ├── balance_invalid_format.xlsx
│   │   └── correspondances_test.json
│   └── conftest.py
```

#### Stratégies de Génération Hypothesis

Stratégies personnalisées pour générer des données de test réalistes:

```python
# conftest.py

import hypothesis.strategies as st
from hypothesis import assume
import pandas as pd

@st.composite
def st_balance(draw):
    """Génère une balance comptable valide"""
    num_comptes = draw(st.integers(min_value=10, max_value=100))
    
    comptes = []
    for _ in range(num_comptes):
        numero = draw(st.text(alphabet='0123456789', min_size=3, max_size=5))
        intitule = draw(st.text(min_size=5, max_size=50))
        ant_debit = draw(st.floats(min_value=0, max_value=10000000))
        ant_credit = draw(st.floats(min_value=0, max_value=10000000))
        mvt_debit = draw(st.floats(min_value=0, max_value=5000000))
        mvt_credit = draw(st.floats(min_value=0, max_value=5000000))
        
        # Calculer les soldes de clôture cohérents
        solde_ouverture = ant_debit - ant_credit
        solde_cloture = solde_ouverture + mvt_debit - mvt_credit
        
        solde_debit = max(0, solde_cloture)
        solde_credit = max(0, -solde_cloture)
        
        comptes.append({
            'Numéro': numero,
            'Intitulé': intitule,
            'Ant Débit': ant_debit,
            'Ant Crédit': ant_credit,
            'Débit': mvt_debit,
            'Crédit': mvt_credit,
            'Solde Débit': solde_debit,
            'Solde Crédit': solde_credit
        })
    
    return pd.DataFrame(comptes)

@st.composite
def st_compte_racine(draw):
    """Génère une racine de compte SYSCOHADA valide"""
    classe = draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9']))
    sous_classe = draw(st.integers(min_value=0, max_value=9))
    return f"{classe}{sous_classe}"
```

### Unit Testing Strategy

#### Tests par Module

Chaque module partagé a une suite de tests unitaires couvrant:

1. **Balance_Reader**:
   - Chargement de fichiers valides
   - Détection d'onglets avec variations de noms
   - Gestion des onglets manquants
   - Normalisation des colonnes
   - Conversion des montants
   - Gestion des valeurs invalides

2. **Account_Extractor**:
   - Extraction par racine simple
   - Extraction par racines multiples
   - Sommation de comptes multiples
   - Gestion des comptes inexistants
   - Préservation de la précision

3. **Movement_Calculator**:
   - Calcul des soldes d'ouverture
   - Calcul des augmentations/diminutions
   - Calcul des soldes de clôture
   - Vérification de cohérence
   - Inversion des signes pour amortissements

4. **VNC_Calculator**:
   - Calcul VNC ouverture/clôture
   - Extraction dotations/reprises
   - Validation VNC >= 0
   - Gestion des VNC négatives

5. **HTML_Generator**:
   - Génération de structure HTML valide
   - Formatage des montants
   - Application du CSS
   - Génération des en-têtes groupés
   - Ligne de total

6. **Excel_Exporter**:
   - Création de fichier Excel
   - Création d'onglets multiples
   - Formatage numérique
   - Application des styles
   - Nom de fichier avec date

7. **Mapping_Manager**:
   - Chargement du JSON
   - Recherche de postes
   - Gestion des 4 sections
   - Validation des racines
   - Ajout de correspondances

8. **Coherence_Validator**:
   - Validation total immobilisations
   - Validation dotations
   - Validation continuité temporelle
   - Calcul taux de cohérence
   - Génération rapport HTML

9. **Trace_Manager**:
   - Enregistrement des calculs
   - Enregistrement des métadonnées
   - Sauvegarde JSON
   - Export CSV
   - Gestion historique

#### Exemples de Tests Unitaires

```python
# test_balance_reader.py

import pytest
from balance_reader import BalanceReader, BalanceNotFoundException

def test_charger_balances_fichier_valide():
    """Test du chargement d'un fichier de balance valide"""
    reader = BalanceReader("fixtures/balance_demo_n_n1_n2.xlsx")
    balance_n, balance_n1, balance_n2 = reader.charger_balances()
    
    assert len(balance_n) > 0
    assert len(balance_n1) > 0
    assert len(balance_n2) > 0
    assert list(balance_n.columns) == ['Numéro', 'Intitulé', 'Ant Débit', 
                                        'Ant Crédit', 'Débit', 'Crédit', 
                                        'Solde Débit', 'Solde Crédit']

def test_charger_balances_onglet_manquant():
    """Test de la gestion d'un onglet manquant"""
    reader = BalanceReader("fixtures/balance_incomplete.xlsx")
    
    with pytest.raises(BalanceNotFoundException) as exc_info:
        reader.charger_balances()
    
    assert "BALANCE N-2" in str(exc_info.value)

def test_nettoyer_colonnes():
    """Test de la normalisation des noms de colonnes"""
    reader = BalanceReader("fixtures/balance_demo_n_n1_n2.xlsx")
    df = pd.DataFrame(columns=['Ant  Débit', 'Ant     Crédit', 'Solde  Débit'])
    
    df_clean = reader.nettoyer_colonnes(df)
    
    assert list(df_clean.columns) == ['Ant Débit', 'Ant Crédit', 'Solde Débit']

def test_convertir_montants_valeurs_invalides():
    """Test de la conversion avec valeurs invalides"""
    reader = BalanceReader("fixtures/balance_demo_n_n1_n2.xlsx")
    df = pd.DataFrame({
        'Débit': [1000, '', None, 'abc', 2000],
        'Crédit': [500, 1500, None, '', 3000]
    })
    
    df_converted = reader.convertir_montants(df)
    
    assert df_converted['Débit'].tolist() == [1000.0, 0.0, 0.0, 0.0, 2000.0]
    assert df_converted['Crédit'].tolist() == [500.0, 1500.0, 0.0, 0.0, 3000.0]
```

### Integration Testing Strategy

#### Tests d'Intégration par Note

Chaque note annexe a un test d'intégration complet:

```python
# test_note_3a_integration.py

def test_note_3a_calcul_complet():
    """
    Test d'intégration complet de la Note 3A
    Feature: calcul-notes-annexes-syscohada
    """
    calculateur = CalculateurNote3A("fixtures/balance_demo_n_n1_n2.xlsx")
    
    # Charger les balances
    assert calculateur.charger_balances() == True
    
    # Générer la note
    df_note = calculateur.generer_note()
    
    # Vérifications
    assert len(df_note) == 5  # 4 lignes + 1 total
    assert df_note.iloc[-1]['libelle'] == 'TOTAL IMMOBILISATIONS INCORPORELLES'
    
    # Vérifier la cohérence des calculs
    for _, row in df_note.iterrows():
        assert row['brut_cloture'] == row['brut_ouverture'] + row['augmentations'] - row['diminutions']
        assert row['vnc_ouverture'] == row['brut_ouverture'] - row['amort_ouverture']
        assert row['vnc_cloture'] == row['brut_cloture'] - row['amort_cloture']
    
    # Générer le HTML
    html = calculateur.generer_html(df_note)
    assert '<table>' in html
    assert 'NOTE 3A' in html
    assert 'IMMOBILISATIONS INCORPORELLES' in html
```

#### Test d'Intégration Global

```python
# test_all_notes_integration.py

def test_calcul_33_notes_complet():
    """
    Test d'intégration de toutes les 33 notes
    Feature: calcul-notes-annexes-syscohada
    Property 18: Performance constraint < 30 seconds
    """
    import time
    
    start_time = time.time()
    
    orchestrateur = CalculNotesAnnexesMain("fixtures/balance_demo_n_n1_n2.xlsx")
    resultats = orchestrateur.calculer_toutes_notes()
    
    end_time = time.time()
    duree = end_time - start_time
    
    # Vérifier que les 33 notes sont calculées
    assert len(resultats) == 33
    
    # Vérifier la performance
    assert duree < 30.0, f"Calcul trop lent: {duree:.2f}s (max: 30s)"
    
    # Vérifier la cohérence inter-notes
    validator = CoherenceValidator(resultats)
    taux_coherence = validator.calculer_taux_coherence()
    assert taux_coherence >= 95.0, f"Taux de cohérence trop faible: {taux_coherence:.1f}%"
```

#### Test d'Intégration API

```python
# test_api_integration.py

def test_api_calculer_notes_annexes():
    """
    Test d'intégration de l'endpoint API
    Feature: calcul-notes-annexes-syscohada
    Property 20: API Integration Round-Trip
    """
    from flask import Flask
    from flask.testing import FlaskClient
    
    app = Flask(__name__)
    client = app.test_client()
    
    # Upload du fichier de balance
    with open('fixtures/balance_demo_n_n1_n2.xlsx', 'rb') as f:
        response = client.post('/api/calculer_notes_annexes',
                              data={'balance': f},
                              content_type='multipart/form-data')
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['success'] == True
    assert 'notes' in data
    assert len(data['notes']) == 33
    
    # Vérifier la structure d'une note
    note_3a = data['notes']['note_3a']
    assert 'titre' in note_3a
    assert 'lignes' in note_3a
    assert 'html' in note_3a
```

### Test Coverage Goals

Objectifs de couverture de code:

- **Couverture globale**: Minimum 85%
- **Modules critiques** (Balance_Reader, Account_Extractor, Movement_Calculator): Minimum 95%
- **Modules de génération** (HTML_Generator, Excel_Exporter): Minimum 80%
- **Gestion d'erreurs**: 100% des branches d'erreur testées

### Continuous Integration

Configuration CI/CD pour exécution automatique des tests:

```yaml
# .github/workflows/test_notes_annexes.yml

name: Tests Notes Annexes SYSCOHADA

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov hypothesis
    
    - name: Run unit tests
      run: pytest Tests/unit/ -v --cov=. --cov-report=html
    
    - name: Run property tests
      run: pytest Tests/property/ -v --hypothesis-show-statistics
    
    - name: Run integration tests
      run: pytest Tests/integration/ -v
    
    - name: Check coverage
      run: |
        coverage report --fail-under=85
```

### Test Execution Commands

Commandes pour exécuter les différents types de tests:

```bash
# Tous les tests
pytest Tests/ -v

# Tests unitaires uniquement
pytest Tests/unit/ -v

# Tests de propriétés uniquement
pytest Tests/property/ -v --hypothesis-show-statistics

# Tests d'intégration uniquement
pytest Tests/integration/ -v

# Tests avec couverture
pytest Tests/ -v --cov=. --cov-report=html

# Test d'une note spécifique
pytest Tests/integration/test_note_3a_integration.py -v

# Test de performance
pytest Tests/integration/test_all_notes_integration.py::test_calcul_33_notes_complet -v
```

