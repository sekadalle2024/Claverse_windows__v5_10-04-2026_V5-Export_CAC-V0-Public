"""
Module de lecture des balances multi-exercices depuis Excel.

Ce module gère le chargement des balances à 8 colonnes pour les exercices N, N-1 et N-2.
"""

import pandas as pd
import logging
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)


class BalanceNotFoundException(Exception):
    """Exception levée quand un onglet de balance est introuvable."""
    pass


class InvalidBalanceFormatException(Exception):
    """Exception levée quand le format de balance est invalide."""
    pass


class BalanceReader:
    """Lecteur de balances multi-exercices depuis Excel."""
    
    COLONNES_REQUISES = [
        'Numéro', 'Intitulé', 'Ant Débit', 'Ant Crédit',
        'Débit', 'Crédit', 'Solde Débit', 'Solde Crédit'
    ]
    
    def __init__(self, fichier_balance: str):
        """
        Initialise le lecteur avec le chemin du fichier Excel.
        
        Args:
            fichier_balance: Chemin vers le fichier Excel de balances
        """
        self.fichier_balance = fichier_balance
        logger.info(f"Initialisation du BalanceReader avec {fichier_balance}")
    
    def charger_balances(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Charge les 3 balances (N, N-1, N-2).
        
        Returns:
            Tuple de 3 DataFrames (balance_n, balance_n1, balance_n2)
            
        Raises:
            BalanceNotFoundException: Si un onglet requis est manquant
            InvalidBalanceFormatException: Si le format est invalide
        """
        try:
            # Lire les noms d'onglets
            xl_file = pd.ExcelFile(self.fichier_balance)
            sheet_names = xl_file.sheet_names
            logger.info(f"Onglets trouvés: {sheet_names}")
            
            # Détecter les onglets
            onglets = self.detecter_onglets(sheet_names)
            
            # Charger chaque balance
            balance_n = self._charger_onglet(onglets['N'])
            balance_n1 = self._charger_onglet(onglets['N-1'])
            balance_n2 = self._charger_onglet(onglets['N-2'])
            
            logger.info(f"✓ Balance N: {len(balance_n)} lignes chargées")
            logger.info(f"✓ Balance N-1: {len(balance_n1)} lignes chargées")
            logger.info(f"✓ Balance N-2: {len(balance_n2)} lignes chargées")
            
            return balance_n, balance_n1, balance_n2
            
        except FileNotFoundError:
            raise BalanceNotFoundException(f"Fichier introuvable: {self.fichier_balance}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des balances: {e}")
            raise
    
    def detecter_onglets(self, sheet_names: List[str]) -> Dict[str, str]:
        """
        Détecte automatiquement les onglets N, N-1, N-2.
        
        Args:
            sheet_names: Liste des noms d'onglets du fichier Excel
            
        Returns:
            Dict mappant 'N', 'N-1', 'N-2' aux noms d'onglets détectés
            
        Raises:
            BalanceNotFoundException: Si un onglet requis est manquant
        """
        onglets = {}
        
        # Patterns de recherche
        patterns = {
            'N': ['BALANCE N', 'Balance N', 'N', 'BALANCE_N'],
            'N-1': ['BALANCE N-1', 'Balance N-1', 'N-1', 'BALANCE_N-1', 'N1'],
            'N-2': ['BALANCE N-2', 'Balance N-2', 'N-2', 'BALANCE_N-2', 'N2']
        }
        
        for exercice, pattern_list in patterns.items():
            found = False
            for pattern in pattern_list:
                for sheet_name in sheet_names:
                    if pattern.upper() in sheet_name.upper():
                        onglets[exercice] = sheet_name
                        found = True
                        break
                if found:
                    break
            
            if not found:
                raise BalanceNotFoundException(
                    f"Onglet '{exercice}' introuvable. Onglets disponibles: {sheet_names}"
                )
        
        logger.info(f"Onglets détectés: {onglets}")
        return onglets
    
    def _charger_onglet(self, sheet_name: str) -> pd.DataFrame:
        """Charge un onglet et applique les transformations."""
        df = pd.read_excel(self.fichier_balance, sheet_name=sheet_name)
        df = self.nettoyer_colonnes(df)
        df = self.convertir_montants(df)
        self._valider_colonnes(df)
        return df
    
    def nettoyer_colonnes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les noms de colonnes (suppression espaces, normalisation).
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame avec colonnes nettoyées
        """
        # Supprimer les espaces multiples
        df.columns = [' '.join(col.split()) for col in df.columns]
        return df
    
    def convertir_montants(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convertit tous les montants en float, remplace valeurs invalides par 0.0.
        
        Args:
            df: DataFrame à convertir
            
        Returns:
            DataFrame avec montants convertis
        """
        colonnes_montants = ['Ant Débit', 'Ant Crédit', 'Débit', 'Crédit', 
                            'Solde Débit', 'Solde Crédit']
        
        for col in colonnes_montants:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        return df
    
    def _valider_colonnes(self, df: pd.DataFrame):
        """Valide que toutes les colonnes requises sont présentes."""
        colonnes_manquantes = [col for col in self.COLONNES_REQUISES 
                              if col not in df.columns]
        
        if colonnes_manquantes:
            raise InvalidBalanceFormatException(
                f"Colonnes manquantes: {colonnes_manquantes}. "
                f"Colonnes trouvées: {list(df.columns)}"
            )
