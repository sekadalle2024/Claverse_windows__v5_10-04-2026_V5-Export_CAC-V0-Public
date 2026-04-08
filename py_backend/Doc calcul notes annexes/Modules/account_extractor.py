"""
Module d'extraction des soldes des comptes par racine.

Ce module permet d'extraire et de sommer les soldes des comptes selon leur numéro de racine.
"""

import pandas as pd
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class AccountExtractor:
    """Extracteur de soldes de comptes par racine."""
    
    def __init__(self, balance: pd.DataFrame):
        """
        Initialise l'extracteur avec une balance.
        
        Args:
            balance: DataFrame de la balance
        """
        self.balance = balance
        logger.debug(f"AccountExtractor initialisé avec {len(balance)} comptes")
    
    def extraire_solde_compte(self, numero_compte: str) -> Dict[str, float]:
        """
        Extrait les 6 valeurs d'un compte par sa racine.
        
        Args:
            numero_compte: Racine du compte (ex: "211")
            
        Returns:
            Dict avec clés: ant_debit, ant_credit, mvt_debit, mvt_credit,
                           solde_debit, solde_credit
        """
        comptes_filtres = self.filtrer_par_racine(numero_compte)
        
        if len(comptes_filtres) == 0:
            logger.warning(f"Aucun compte trouvé pour la racine {numero_compte}")
            return {
                'ant_debit': 0.0,
                'ant_credit': 0.0,
                'mvt_debit': 0.0,
                'mvt_credit': 0.0,
                'solde_debit': 0.0,
                'solde_credit': 0.0
            }
        
        # Sommer les valeurs
        resultat = {
            'ant_debit': comptes_filtres['Ant Débit'].sum(),
            'ant_credit': comptes_filtres['Ant Crédit'].sum(),
            'mvt_debit': comptes_filtres['Débit'].sum(),
            'mvt_credit': comptes_filtres['Crédit'].sum(),
            'solde_debit': comptes_filtres['Solde Débit'].sum(),
            'solde_credit': comptes_filtres['Solde Crédit'].sum()
        }
        
        logger.debug(f"Compte {numero_compte}: {len(comptes_filtres)} comptes trouvés, "
                    f"solde clôture = {resultat['solde_debit'] - resultat['solde_credit']}")
        
        return resultat
    
    def extraire_comptes_multiples(self, racines: List[str]) -> Dict[str, float]:
        """
        Extrait et somme les soldes de plusieurs racines de comptes.
        
        Args:
            racines: Liste de racines de comptes
            
        Returns:
            Dict avec les sommes des 6 valeurs
        """
        resultat_total = {
            'ant_debit': 0.0,
            'ant_credit': 0.0,
            'mvt_debit': 0.0,
            'mvt_credit': 0.0,
            'solde_debit': 0.0,
            'solde_credit': 0.0
        }
        
        for racine in racines:
            resultat = self.extraire_solde_compte(racine)
            for key in resultat_total:
                resultat_total[key] += resultat[key]
        
        logger.debug(f"Extraction multiple de {len(racines)} racines: "
                    f"solde total = {resultat_total['solde_debit'] - resultat_total['solde_credit']}")
        
        return resultat_total
    
    def filtrer_par_racine(self, racine: str) -> pd.DataFrame:
        """
        Filtre les comptes commençant par une racine.
        
        Args:
            racine: Racine de compte
            
        Returns:
            DataFrame des comptes filtrés
        """
        # Convertir la colonne Numéro en string pour la comparaison
        self.balance['Numéro'] = self.balance['Numéro'].astype(str)
        
        # Filtrer les comptes commençant par la racine
        mask = self.balance['Numéro'].str.startswith(racine)
        return self.balance[mask].copy()
