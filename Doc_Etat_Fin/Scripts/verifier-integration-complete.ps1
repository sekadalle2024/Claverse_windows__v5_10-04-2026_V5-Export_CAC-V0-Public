# Script PowerShell pour vérifier l'intégration complète des États de Contrôle

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  VÉRIFICATION INTÉGRATION COMPLÈTE - ÉTATS DE CONTRÔLE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$erreurs = 0
$avertissements = 0

# ============================================================================
# 1. VÉRIFICATION BACKEND
# ============================================================================
Write-Host "1. VÉRIFICATION BACKEND" -ForegroundColor Yellow
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 1.1 Module principal
Write-Host "   1.1 Module etats_controle_exhaustifs_html.py..." -ForegroundColor White
if (Test-Path "py_backend/etats_controle_exhaustifs_html.py") {
    Write-Host "       ✅ Fichier trouvé" -ForegroundColor Green
} else {
    Write-Host "       ❌ Fichier manquant" -ForegroundColor Red
    $erreurs++
}

# 1.2 Test rapide
Write-Host "   1.2 Test de génération rapide..." -ForegroundColor White
if (Test-Path "test-16-etats-rapide.py") {
    Write-Host "       ✅ Script de test trouvé" -ForegroundColor Green
    
    Write-Host "       ⏳ Exécution du test..." -ForegroundColor Gray
    $output = python test-16-etats-rapide.py 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "       ✅ Test réussi" -ForegroundColor Green
    } else {
        Write-Host "       ❌ Test échoué" -ForegroundColor Red
        $erreurs++
    }
} else {
    Write-Host "       ⚠️  Script de test manquant" -ForegroundColor Yellow
    $avertissements++
}

# 1.3 Vérification des imports
Write-Host "   1.3 Vérification des imports Python..." -ForegroundColor White
$testImport = @"
try:
    from py_backend.etats_controle_exhaustifs_html import generate_all_16_etats_controle_html
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
"@

$result = $testImport | python 2>&1
if ($result -match "OK") {
    Write-Host "       ✅ Imports fonctionnels" -ForegroundColor Green
} else {
    Write-Host "       ❌ Erreur d'import: $result" -ForegroundColor Red
    $erreurs++
}

Write-Host ""

# ============================================================================
# 2. VÉRIFICATION DOCUMENTATION
# ============================================================================
Write-Host "2. VÉRIFICATION DOCUMENTATION" -ForegroundColor Yellow
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$docs = @(
    "Doc_Etat_Fin/README.md",
    "Doc_Etat_Fin/00_INDEX_COMPLET_ETATS_CONTROLE.md",
    "Doc_Etat_Fin/Documentation/MEMO_PROBLEMES_PYTHON_F_STRINGS.md",
    "Doc_Etat_Fin/Documentation/00_CORRECTION_F_STRING_05_AVRIL_2026.md",
    "Doc_Etat_Fin/Documentation/ARCHITECTURE_MENU_ACCORDEON_ETATS_CONTROLE.md"
)

foreach ($doc in $docs) {
    $filename = Split-Path $doc -Leaf
    Write-Host "   • $filename..." -ForegroundColor White -NoNewline
    
    if (Test-Path $doc) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌" -ForegroundColor Red
        $erreurs++
    }
}

Write-Host ""

# ============================================================================
# 3. VÉRIFICATION SCRIPTS
# ============================================================================
Write-Host "3. VÉRIFICATION SCRIPTS" -ForegroundColor Yellow
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$scripts = @(
    @{Path="Doc_Etat_Fin/Scripts/add_etats_controle_to_menu.py"; Type="Python"},
    @{Path="Doc_Etat_Fin/Scripts/test-menu-etats-controle.ps1"; Type="PowerShell"},
    @{Path="Doc_Etat_Fin/Scripts/test_integration_16_etats.py"; Type="Python"},
    @{Path="Doc_Etat_Fin/Scripts/test-integration-16-etats.ps1"; Type="PowerShell"}
)

foreach ($script in $scripts) {
    $filename = Split-Path $script.Path -Leaf
    Write-Host "   • $filename ($($script.Type))..." -ForegroundColor White -NoNewline
    
    if (Test-Path $script.Path) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌" -ForegroundColor Red
        $erreurs++
    }
}

Write-Host ""

# ============================================================================
# 4. VÉRIFICATION FRONTEND (optionnel)
# ============================================================================
Write-Host "4. VÉRIFICATION FRONTEND (optionnel)" -ForegroundColor Yellow
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 4.1 DemarrerMenu.tsx
Write-Host "   4.1 DemarrerMenu.tsx..." -ForegroundColor White
if (Test-Path "src/components/Clara_Components/DemarrerMenu.tsx") {
    $content = Get-Content "src/components/Clara_Components/DemarrerMenu.tsx" -Raw
    
    if ($content -match "États de Contrôle") {
        Write-Host "       ✅ Entrée 'États de Contrôle' trouvée" -ForegroundColor Green
    } else {
        Write-Host "       ⚠️  Entrée 'États de Contrôle' non trouvée" -ForegroundColor Yellow
        Write-Host "       💡 Exécuter: python Doc_Etat_Fin/Scripts/add_etats_controle_to_menu.py" -ForegroundColor Gray
        $avertissements++
    }
} else {
    Write-Host "       ❌ Fichier DemarrerMenu.tsx non trouvé" -ForegroundColor Red
    $erreurs++
}

# 4.2 Composant React (optionnel)
Write-Host "   4.2 EtatsControleAccordionRenderer.tsx..." -ForegroundColor White
if (Test-Path "src/components/Clara_Components/EtatsControleAccordionRenderer.tsx") {
    Write-Host "       ✅ Composant React créé" -ForegroundColor Green
} else {
    Write-Host "       ⚠️  Composant React non créé (optionnel)" -ForegroundColor Yellow
    $avertissements++
}

# 4.3 Fichier CSS (optionnel)
Write-Host "   4.3 EtatsControleAccordionRenderer.css..." -ForegroundColor White
if (Test-Path "src/components/Clara_Components/EtatsControleAccordionRenderer.css") {
    Write-Host "       ✅ Fichier CSS créé" -ForegroundColor Green
} else {
    Write-Host "       ⚠️  Fichier CSS non créé (optionnel)" -ForegroundColor Yellow
    $avertissements++
}

Write-Host ""

# ============================================================================
# 5. VÉRIFICATION API (optionnel)
# ============================================================================
Write-Host "5. VÉRIFICATION API (optionnel)" -ForegroundColor Yellow
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 5.1 Endpoint dans main.py
Write-Host "   5.1 Endpoint /api/etats-controle..." -ForegroundColor White
if (Test-Path "py_backend/main.py") {
    $mainContent = Get-Content "py_backend/main.py" -Raw
    
    if ($mainContent -match "/api/etats-controle" -or $mainContent -match "etats.controle") {
        Write-Host "       ✅ Endpoint trouvé" -ForegroundColor Green
    } else {
        Write-Host "       ⚠️  Endpoint non trouvé (optionnel)" -ForegroundColor Yellow
        $avertissements++
    }
} else {
    Write-Host "       ⚠️  Fichier main.py non trouvé" -ForegroundColor Yellow
    $avertissements++
}

# 5.2 Service API
Write-Host "   5.2 claraApiService.ts..." -ForegroundColor White
if (Test-Path "src/services/claraApiService.ts") {
    $serviceContent = Get-Content "src/services/claraApiService.ts" -Raw
    
    if ($serviceContent -match "fetchEtatsControle" -or $serviceContent -match "etats.controle") {
        Write-Host "       ✅ Méthode API trouvée" -ForegroundColor Green
    } else {
        Write-Host "       ⚠️  Méthode API non trouvée (optionnel)" -ForegroundColor Yellow
        $avertissements++
    }
} else {
    Write-Host "       ⚠️  Fichier claraApiService.ts non trouvé" -ForegroundColor Yellow
    $avertissements++
}

Write-Host ""

# ============================================================================
# 6. RÉSUMÉ FINAL
# ============================================================================
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  RÉSUMÉ DE LA VÉRIFICATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($erreurs -eq 0 -and $avertissements -eq 0) {
    Write-Host "✅ INTÉGRATION COMPLÈTE ET FONCTIONNELLE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tous les composants essentiels sont en place:" -ForegroundColor White
    Write-Host "  • Backend: Module et tests validés" -ForegroundColor Gray
    Write-Host "  • Documentation: Complète et à jour" -ForegroundColor Gray
    Write-Host "  • Scripts: Tous présents" -ForegroundColor Gray
    Write-Host ""
    
} elseif ($erreurs -eq 0) {
    Write-Host "⚠️  INTÉGRATION PARTIELLE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Composants essentiels: ✅ OK" -ForegroundColor Green
    Write-Host "Composants optionnels: ⚠️  $avertissements manquant(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "L'intégration backend est complète." -ForegroundColor White
    Write-Host "Les composants frontend sont optionnels pour le moment." -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "❌ INTÉGRATION INCOMPLÈTE" -ForegroundColor Red
    Write-Host ""
    Write-Host "Erreurs critiques: $erreurs" -ForegroundColor Red
    Write-Host "Avertissements: $avertissements" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Action requise: Corriger les erreurs ci-dessus" -ForegroundColor White
    Write-Host ""
}

# ============================================================================
# 7. PROCHAINES ÉTAPES
# ============================================================================
Write-Host "📋 PROCHAINES ÉTAPES RECOMMANDÉES:" -ForegroundColor Cyan
Write-Host ""

if ($erreurs -eq 0) {
    Write-Host "1. ✅ Backend validé - Prêt pour l'intégration frontend" -ForegroundColor Green
    Write-Host ""
    
    if ($avertissements -gt 0) {
        Write-Host "2. Créer les composants React (optionnel):" -ForegroundColor White
        Write-Host "   • EtatsControleAccordionRenderer.tsx" -ForegroundColor Gray
        Write-Host "   • EtatsControleAccordionRenderer.css" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "3. Créer l'endpoint API (optionnel):" -ForegroundColor White
        Write-Host "   • Ajouter route dans py_backend/main.py" -ForegroundColor Gray
        Write-Host "   • Mettre à jour claraApiService.ts" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "4. Tester l'intégration complète:" -ForegroundColor White
    Write-Host "   .\Doc_Etat_Fin\Scripts\test-integration-16-etats.ps1" -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "1. ❌ Corriger les erreurs critiques détectées" -ForegroundColor Red
    Write-Host ""
    Write-Host "2. Relancer cette vérification:" -ForegroundColor White
    Write-Host "   .\Doc_Etat_Fin\Scripts\verifier-integration-complete.ps1" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# 8. STATISTIQUES
# ============================================================================
Write-Host "📊 STATISTIQUES:" -ForegroundColor Cyan
Write-Host "   • Erreurs critiques: $erreurs" -ForegroundColor $(if ($erreurs -eq 0) { "Green" } else { "Red" })
Write-Host "   • Avertissements: $avertissements" -ForegroundColor $(if ($avertissements -eq 0) { "Green" } else { "Yellow" })
Write-Host "   • Statut global: $(if ($erreurs -eq 0) { '✅ OK' } else { '❌ À corriger' })" -ForegroundColor $(if ($erreurs -eq 0) { "Green" } else { "Red" })
Write-Host ""

# Code de sortie
if ($erreurs -gt 0) {
    exit 1
} else {
    exit 0
}
