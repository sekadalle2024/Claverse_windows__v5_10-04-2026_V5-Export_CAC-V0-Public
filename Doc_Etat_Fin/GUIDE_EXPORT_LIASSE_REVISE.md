# Guide d'Export - Liasse Officielle SYSCOHADA Révisé

**Version**: 2.1  
**Date**: 05 Avril 2026  
**Statut**: ✅ Opérationnel

---

## 🎯 Objectif

Exporter les états financiers vers le fichier Excel **Liasse_officielle_revise.xlsx** conforme au référentiel SYSCOHADA Révisé.

---

## 📋 Prérequis

- ✅ États financiers générés (via "Etat fin")
- ✅ Fichier template `Liasse_officielle_revise.xlsx` présent dans `py_backend/`
- ✅ Backend Python opérationnel

---

## 🚀 Méthode 1 : Via le Menu Contextuel (Recommandé)

### Étape 1 : Générer les États Financiers

1. Dans le chat, taper : **`Etat fin`**
2. Sélectionner le fichier Balance Excel (N, N-1, N-2)
3. Attendre la génération des états financiers
4. Les états s'affichent en accordéons

### Étape 2 : Exporter la Liasse

1. **Clic droit** sur la table des états financiers
2. Sélectionner : **📥 Exporter liasse officielle**
3. Le fichier Excel se télécharge automatiquement

### Étape 3 : Vérifier le Fichier

1. Ouvrir le fichier Excel téléchargé
2. Vérifier les onglets :
   - ✅ BILAN, ACTIF, PASSIF
   - ✅ RESULTAT (Compte de Résultat)
   - ✅ TFT (Tableau des Flux de Trésorerie)
   - ✅ NOTE 1 à NOTE 39
3. Vérifier que les valeurs sont remplies

---

## 🖥️ Méthode 2 : Via Script Python

### Commandes

```bash
# Activer l'environnement conda
conda activate claraverse_backend

# Aller dans le dossier backend
cd py_backend

# Générer les états et exporter
python generer_etats_liasse.py
```

### Résultat

- Fichier HTML généré sur le Bureau
- Contient tous les états financiers
- Option d'export Excel disponible

---

## 🌐 Méthode 3 : Via API

### Endpoint

```
POST http://localhost:5000/export-liasse/generer
```

### Body (JSON)

```json
{
  "results": {
    "bilan_actif": {...},
    "bilan_passif": {...},
    "compte_resultat": {...},
    "tft": {...},
    "annexes": {...}
  },
  "nom_entreprise": "ENTREPRISE SA",
  "exercice": "2024"
}
```

### Réponse

```json
{
  "success": true,
  "message": "Liasse officielle générée avec succès...",
  "file_base64": "UEsDBBQABgAIAAAAIQD...",
  "filename": "Liasse_Officielle_ENTREPRISE_SA_2024.xlsx"
}
```

---

## 📊 Structure du Fichier Exporté

### Onglets Principaux

| Onglet | Description | Contenu |
|--------|-------------|---------|
| **BILAN** | Vue consolidée du bilan | Actif + Passif |
| **ACTIF** | Détail de l'actif | Immobilisations, Actif circulant, Trésorerie |
| **PASSIF** | Détail du passif | Capitaux propres, Dettes, Trésorerie |
| **RESULTAT** | Compte de résultat | Charges + Produits |
| **TFT** | Tableau des flux de trésorerie | Flux opérationnels, investissement, financement |

### Notes Annexes (39 notes)

| Notes | Description |
|-------|-------------|
| **NOTE 1-2** | Informations générales |
| **NOTE 3A-3E** | Immobilisations |
| **NOTE 4-9** | Actif circulant |
| **NOTE 10-15** | Capitaux propres et dettes |
| **NOTE 16-20** | Dettes financières |
| **NOTE 21-35** | Compte de résultat détaillé |
| **NOTE 36-39** | Informations complémentaires |

### Fiches Complémentaires

- **FICHE R1** : Renseignements généraux
- **FICHE R2** : Effectifs et masse salariale
- **FICHE R3** : Investissements
- **FICHE R4** : Tableau de financement

---

## 🔧 Configuration

### Fichier Template

**Emplacement** : `py_backend/Liasse_officielle_revise.xlsx`

**Caractéristiques** :
- 84 onglets
- Format SYSCOHADA Révisé
- Conforme aux normes comptables OHADA

### Ordre de Priorité des Templates

Le script cherche les templates dans cet ordre :

1. **Liasse_officielle_revise.xlsx** ⭐ (PRIORITAIRE)
2. LIASSE.xlsx (fallback)
3. Liasse officielle.xlsm (fallback)

---

## ⚙️ Mappings des Cellules

### Bilan Actif

Les postes du bilan actif sont mappés vers les cellules du template :

```python
MAPPING_BILAN_ACTIF = {
    'AD': 'C10',   # Charges immobilisées
    'AE': 'C11',   # Frais de R&D
    'AF': 'C12',   # Brevets, licences
    # ... (voir export_liasse.py pour la liste complète)
}
```

### Bilan Passif

```python
MAPPING_BILAN_PASSIF = {
    'DA': 'E10',   # Capital
    'DB': 'E11',   # Apporteurs
    'DC': 'E12',   # Primes
    # ... (voir export_liasse.py pour la liste complète)
}
```

### Compte de Résultat

```python
MAPPING_COMPTE_RESULTAT_CHARGES = {
    'TA': 'C10',   # Achats de marchandises
    'TB': 'C11',   # Variation de stocks
    # ... (voir export_liasse.py pour la liste complète)
}

MAPPING_COMPTE_RESULTAT_PRODUITS = {
    'RA': 'E10',   # Ventes de marchandises
    'RB': 'E11',   # Ventes de produits
    # ... (voir export_liasse.py pour la liste complète)
}
```

---

## 🐛 Dépannage

### Problème : Fichier template non trouvé

**Erreur** : `FileNotFoundError: Fichier template de liasse non trouvé`

**Solution** :
1. Vérifier que `Liasse_officielle_revise.xlsx` existe dans `py_backend/`
2. Vérifier les permissions du fichier
3. Essayer avec un des fichiers fallback

### Problème : Valeurs non remplies

**Symptôme** : Le fichier Excel est généré mais les cellules sont vides

**Solution** :
1. Vérifier les mappings de cellules dans `export_liasse.py`
2. Comparer avec le template réel
3. Ajuster les références de cellules si nécessaire

### Problème : Onglets manquants

**Symptôme** : Certains onglets ne sont pas présents dans le fichier exporté

**Solution** :
1. Vérifier que le template contient tous les onglets
2. Vérifier les noms d'onglets dans le code (sensible à la casse)
3. Utiliser le bon template (Liasse_officielle_revise.xlsx)

---

## 📝 Exemples

### Exemple 1 : Export Simple

```python
from export_liasse import remplir_liasse_officielle

# Résultats des états financiers
results = {
    'bilan_actif': {...},
    'bilan_passif': {...},
    'compte_resultat': {...}
}

# Générer la liasse
file_content = remplir_liasse_officielle(
    results=results,
    nom_entreprise="ENTREPRISE SA",
    exercice="2024"
)

# Sauvegarder
with open("liasse_2024.xlsx", "wb") as f:
    f.write(file_content)
```

### Exemple 2 : Export avec TFT et Annexes

```python
results = {
    'bilan_actif': {...},
    'bilan_passif': {...},
    'compte_resultat': {...},
    'tft': {...},           # Tableau des flux de trésorerie
    'annexes': {...}        # Notes annexes
}

file_content = remplir_liasse_officielle(
    results=results,
    nom_entreprise="ENTREPRISE SA",
    exercice="2024"
)
```

---

## 📚 Documentation Associée

### Guides Principaux

- [Index Complet V2.1](00_INDEX_COMPLET_V2.md)
- [Architecture États Financiers](00_ARCHITECTURE_ETATS_FINANCIERS.md)
- [Correction Export Liasse](00_CORRECTION_EXPORT_LIASSE_REVISE_05_AVRIL_2026.txt)

### Scripts

- `py_backend/export_liasse.py` - Module d'export
- `py_backend/generer_etats_liasse.py` - Script autonome
- `Doc_Etat_Fin/Scripts/test-export-liasse-revise.ps1` - Script de test

---

## ✅ Checklist de Validation

Avant de considérer l'export comme réussi, vérifier :

- [ ] Fichier Excel généré sans erreur
- [ ] Tous les onglets présents (BILAN, ACTIF, PASSIF, RESULTAT, TFT)
- [ ] Valeurs du bilan actif remplies
- [ ] Valeurs du bilan passif remplies
- [ ] Valeurs du compte de résultat remplies
- [ ] TFT calculé et rempli
- [ ] Notes annexes présentes
- [ ] Format des cellules préservé
- [ ] Nom de l'entreprise et exercice affichés

---

## 🎉 Conclusion

L'export de la liasse officielle SYSCOHADA Révisé est maintenant opérationnel avec le fichier template `Liasse_officielle_revise.xlsx` contenant 84 onglets complets.

**Avantages** :
- ✅ Conformité totale SYSCOHADA Révisé
- ✅ 84 onglets complets
- ✅ Export automatique
- ✅ Fallback vers anciens templates
- ✅ Documentation complète

---

**Version** : 2.1  
**Date** : 05 Avril 2026  
**Auteur** : ClaraVerse Team  
**Statut** : ✅ Opérationnel
