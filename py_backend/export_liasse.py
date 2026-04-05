# -*- coding: utf-8 -*-
"""
Module d'export de la liasse officielle Excel remplie avec les valeurs calculées
"""
import pandas as pd
import openpyxl
from openpyxl import load_workbook
import os
import shutil
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import base64
import io

logger = logging.getLogger("export_liasse")

router = APIRouter(prefix="/export-liasse", tags=["Export Liasse"])


# ==================== MODÈLES PYDANTIC ====================

class ExportLiasseRequest(BaseModel):
    """Requête pour exporter la liasse officielle"""
    results: Dict[str, Any]  # Résultats des états financiers
    nom_entreprise: Optional[str] = "ENTREPRISE"
    exercice: Optional[str] = None

class ExportLiasseResponse(BaseModel):
    success: bool
    message: str
    file_base64: Optional[str] = None
    filename: Optional[str] = None


# ==================== MAPPING POSTES VERS CELLULES ====================

# Mapping des références de postes vers les cellules Excel de la liasse officielle
# Format: {'ref_poste': 'cellule_excel'}

MAPPING_BILAN_ACTIF = {
    # ACTIF IMMOBILISÉ
    'AD': 'C10',   # Charges immobilisées
    'AE': 'C11',   # Frais de recherche et développement
    'AF': 'C12',   # Brevets, licences, logiciels
    'AG': 'C13',   # Fonds commercial
    'AH': 'C14',   # Autres immobilisations incorporelles
    'AI': 'C15',   # Terrains
    'AJ': 'C16',   # Bâtiments
    'AK': 'C17',   # Installations et agencements
    'AL': 'C18',   # Matériel
    'AM': 'C19',   # Matériel de transport
    'AN': 'C20',   # Avances et acomptes versés sur immobilisations
    'AP': 'C21',   # Titres de participation
    'AQ': 'C22',   # Autres immobilisations financières
    'AZ': 'C23',   # TOTAL ACTIF IMMOBILISÉ
    
    # ACTIF CIRCULANT
    'BA': 'C25',   # Actif circulant HAO
    'BB': 'C26',   # Stocks et encours
    'BC': 'C27',   # Marchandises
    'BD': 'C28',   # Matières premières
    'BE': 'C29',   # Autres approvisionnements
    'BF': 'C30',   # En-cours
    'BG': 'C31',   # Produits fabriqués
    'BH': 'C32',   # Fournisseurs, avances versées
    'BI': 'C33',   # Clients
    'BJ': 'C34',   # Autres créances
    'BK': 'C35',   # Capital souscrit, appelé non versé
    'BQ': 'C36',   # TOTAL ACTIF CIRCULANT
    
    # TRÉSORERIE-ACTIF
    'BT': 'C38',   # Titres de placement
    'BU': 'C39',   # Valeurs à encaisser
    'BV': 'C40',   # Banques, chèques postaux, caisse
    'BZ': 'C41',   # TOTAL TRÉSORERIE-ACTIF
    
    # ÉCARTS DE CONVERSION-ACTIF
    'CA': 'C43',   # Diminution des créances
    'CB': 'C44',   # Augmentation des dettes
    'CZ': 'C45',   # TOTAL ÉCARTS DE CONVERSION-ACTIF
}

MAPPING_BILAN_PASSIF = {
    # CAPITAUX PROPRES
    'DA': 'E10',   # Capital
    'DB': 'E11',   # Apporteurs, capital non appelé
    'DC': 'E12',   # Primes liées au capital social
    'DD': 'E13',   # Écarts de réévaluation
    'DE': 'E14',   # Réserves indisponibles
    'DF': 'E15',   # Réserves libres
    'DG': 'E16',   # Report à nouveau
    'DH': 'E17',   # Résultat net de l'exercice
    'DI': 'E18',   # Subventions d'investissement
    'DJ': 'E19',   # Provisions réglementées
    'DZ': 'E20',   # TOTAL CAPITAUX PROPRES
    
    # DETTES FINANCIÈRES ET RESSOURCES ASSIMILÉES
    'RA': 'E22',   # Emprunts
    'RB': 'E23',   # Dettes de crédit-bail et contrats assimilés
    'RC': 'E24',   # Dettes financières diverses
    'RD': 'E25',   # Provisions financières pour risques et charges
    'RZ': 'E26',   # TOTAL DETTES FINANCIÈRES
    
    # PASSIF CIRCULANT
    'TA': 'E28',   # Dettes circulantes HAO
    'TB': 'E29',   # Clients, avances reçues
    'TC': 'E30',   # Fournisseurs d'exploitation
    'TD': 'E31',   # Dettes fiscales
    'TE': 'E32',   # Dettes sociales
    'TF': 'E33',   # Autres dettes
    'TG': 'E34',   # Provisions pour risques à court terme
    'TZ': 'E35',   # TOTAL PASSIF CIRCULANT
    
    # TRÉSORERIE-PASSIF
    'UA': 'E37',   # Banques, crédits d'escompte
    'UB': 'E38',   # Banques, crédits de trésorerie
    'UC': 'E39',   # Banques, découverts
    'UZ': 'E40',   # TOTAL TRÉSORERIE-PASSIF
    
    # ÉCARTS DE CONVERSION-PASSIF
    'VA': 'E42',   # Augmentation des créances
    'VB': 'E43',   # Diminution des dettes
    'VZ': 'E44',   # TOTAL ÉCARTS DE CONVERSION-PASSIF
}

MAPPING_COMPTE_RESULTAT_CHARGES = {
    # ACTIVITÉ D'EXPLOITATION
    'TA': 'C10',   # Achats de marchandises
    'TB': 'C11',   # Variation de stocks de marchandises
    'TC': 'C12',   # Achats de matières premières
    'TD': 'C13',   # Variation de stocks de matières
    'TE': 'C14',   # Autres achats
    'TF': 'C15',   # Variation de stocks d'autres approvisionnements
    'TG': 'C16',   # Transports
    'TH': 'C17',   # Services extérieurs
    'TI': 'C18',   # Impôts et taxes
    'TJ': 'C19',   # Autres charges
    'TK': 'C20',   # Charges de personnel
    'TL': 'C21',   # Dotations aux amortissements
    'TM': 'C22',   # Dotations aux provisions
    'TZ': 'C23',   # TOTAL CHARGES D'EXPLOITATION
    
    # ACTIVITÉ FINANCIÈRE
    'UA': 'C25',   # Frais financiers
    'UB': 'C26',   # Pertes de change
    'UC': 'C27',   # Dotations aux amortissements et provisions
    'UZ': 'C28',   # TOTAL CHARGES FINANCIÈRES
    
    # HORS ACTIVITÉS ORDINAIRES (HAO)
    'XA': 'C30',   # Valeurs comptables des cessions d'immobilisations
    'XB': 'C31',   # Charges HAO constatées
    'XC': 'C32',   # Dotations HAO
    'XZ': 'C33',   # TOTAL CHARGES HAO
}

MAPPING_COMPTE_RESULTAT_PRODUITS = {
    # ACTIVITÉ D'EXPLOITATION
    'RA': 'E10',   # Ventes de marchandises
    'RB': 'E11',   # Ventes de produits fabriqués
    'RC': 'E12',   # Travaux, services vendus
    'RD': 'E13',   # Production stockée
    'RE': 'E14',   # Production immobilisée
    'RF': 'E15',   # Subventions d'exploitation
    'RG': 'E16',   # Autres produits
    'RH': 'E17',   # Reprises de provisions
    'RI': 'E18',   # Transferts de charges
    'RZ': 'E19',   # TOTAL PRODUITS D'EXPLOITATION
    
    # ACTIVITÉ FINANCIÈRE
    'SA': 'E21',   # Revenus financiers
    'SB': 'E22',   # Gains de change
    'SC': 'E23',   # Reprises de provisions
    'SD': 'E24',   # Transferts de charges
    'SZ': 'E25',   # TOTAL PRODUITS FINANCIERS
    
    # HORS ACTIVITÉS ORDINAIRES (HAO)
    'YA': 'E27',   # Produits des cessions d'immobilisations
    'YB': 'E28',   # Produits HAO constatés
    'YC': 'E29',   # Reprises HAO
    'YD': 'E30',   # Transferts de charges
    'YZ': 'E31',   # TOTAL PRODUITS HAO
}


# ==================== FONCTIONS D'EXPORT ====================

def remplir_liasse_officielle(results: Dict[str, Any], nom_entreprise: str, exercice: str) -> bytes:
    """
    Remplit la liasse officielle avec les valeurs calculées
    
    Args:
        results: Résultats des états financiers
        nom_entreprise: Nom de l'entreprise
        exercice: Exercice comptable (ex: "2024")
    
    Returns:
        Contenu du fichier Excel en bytes
    """
    logger.info("📊 Début du remplissage de la liasse officielle")
    
    # Chemin du template (fichier vierge) - UTILISER Liasse_officielle_revise.xlsx
    template_path = "Liasse_officielle_revise.xlsx"
    if not os.path.exists(template_path):
        # Essayer avec les anciens noms en fallback
        template_path = "LIASSE.xlsx"
        if not os.path.exists(template_path):
            template_path = "Liasse officielle.xlsm"
            if not os.path.exists(template_path):
                raise FileNotFoundError("Fichier template de liasse non trouvé (Liasse_officielle_revise.xlsx, LIASSE.xlsx ou Liasse officielle.xlsm)")
    
    logger.info(f"📂 Template trouvé: {template_path}")
    
    # Charger le workbook
    wb = load_workbook(template_path)
    
    # Remplir les informations générales
    if 'Bilan' in wb.sheetnames:
        ws_bilan = wb['Bilan']
        # Cellules pour nom entreprise et exercice (à adapter selon le template)
        # ws_bilan['A1'] = nom_entreprise
        # ws_bilan['A2'] = f"Exercice {exercice}"
    
    # Remplir le BILAN - ACTIF
    if 'Bilan' in wb.sheetnames:
        ws_bilan = wb['Bilan']
        logger.info("📝 Remplissage Bilan Actif...")
        
        for ref, cellule in MAPPING_BILAN_ACTIF.items():
            if ref in results.get('bilan_actif', {}):
                montant = results['bilan_actif'][ref]['montant']
                try:
                    ws_bilan[cellule] = montant
                    logger.debug(f"   {ref} -> {cellule}: {montant:,.2f}")
                except Exception as e:
                    logger.warning(f"   Erreur {ref} -> {cellule}: {e}")
    
    # Remplir le BILAN - PASSIF
    if 'Bilan' in wb.sheetnames:
        ws_bilan = wb['Bilan']
        logger.info("📝 Remplissage Bilan Passif...")
        
        for ref, cellule in MAPPING_BILAN_PASSIF.items():
            if ref in results.get('bilan_passif', {}):
                montant = results['bilan_passif'][ref]['montant']
                try:
                    ws_bilan[cellule] = montant
                    logger.debug(f"   {ref} -> {cellule}: {montant:,.2f}")
                except Exception as e:
                    logger.warning(f"   Erreur {ref} -> {cellule}: {e}")
    
    # Remplir le COMPTE DE RÉSULTAT - CHARGES
    if 'Compte de résultat' in wb.sheetnames or 'CR' in wb.sheetnames:
        ws_cr = wb.get('Compte de résultat', wb.get('CR'))
        if ws_cr:
            logger.info("📝 Remplissage Compte de Résultat - Charges...")
            
            for ref, cellule in MAPPING_COMPTE_RESULTAT_CHARGES.items():
                if ref in results.get('charges', {}):
                    montant = results['charges'][ref]['montant']
                    try:
                        ws_cr[cellule] = montant
                        logger.debug(f"   {ref} -> {cellule}: {montant:,.2f}")
                    except Exception as e:
                        logger.warning(f"   Erreur {ref} -> {cellule}: {e}")
    
    # Remplir le COMPTE DE RÉSULTAT - PRODUITS
    if 'Compte de résultat' in wb.sheetnames or 'CR' in wb.sheetnames:
        ws_cr = wb.get('Compte de résultat', wb.get('CR'))
        if ws_cr:
            logger.info("📝 Remplissage Compte de Résultat - Produits...")
            
            for ref, cellule in MAPPING_COMPTE_RESULTAT_PRODUITS.items():
                if ref in results.get('produits', {}):
                    montant = results['produits'][ref]['montant']
                    try:
                        ws_cr[cellule] = montant
                        logger.debug(f"   {ref} -> {cellule}: {montant:,.2f}")
                    except Exception as e:
                        logger.warning(f"   Erreur {ref} -> {cellule}: {e}")
    
    # Sauvegarder dans un buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    logger.info("✅ Liasse officielle remplie avec succès")
    
    return output.getvalue()


# ==================== ENDPOINT API ====================

@router.post("/generer", response_model=ExportLiasseResponse)
async def generer_liasse(request: ExportLiasseRequest):
    """
    Génère la liasse officielle Excel remplie avec les valeurs calculées
    """
    try:
        logger.info("📥 Réception demande d'export liasse")
        
        # Déterminer l'exercice
        exercice = request.exercice or datetime.now().year
        
        # Remplir la liasse
        file_content = remplir_liasse_officielle(
            results=request.results,
            nom_entreprise=request.nom_entreprise,
            exercice=str(exercice)
        )
        
        # Encoder en base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Nom du fichier
        filename = f"Liasse_Officielle_{request.nom_entreprise}_{exercice}.xlsx"
        filename = filename.replace(' ', '_').replace('/', '_')
        
        logger.info(f"✅ Liasse générée: {filename}")
        
        return ExportLiasseResponse(
            success=True,
            message=f"Liasse officielle générée avec succès pour {request.nom_entreprise} - Exercice {exercice}",
            file_base64=file_base64,
            filename=filename
        )
        
    except FileNotFoundError as e:
        logger.error(f"❌ Fichier template non trouvé: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
