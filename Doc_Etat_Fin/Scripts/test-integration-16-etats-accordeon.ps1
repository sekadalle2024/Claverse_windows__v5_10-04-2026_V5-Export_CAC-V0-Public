# Script de test pour verifier l'integration des 16 etats de controle dans le menu accordeon
# Date: 05 Avril 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST INTEGRATION 16 ETATS DE CONTROLE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verifier que le module Python existe
Write-Host "1. Verification du module Python..." -ForegroundColor Yellow
if (Test-Path "py_backend/etats_controle_exhaustifs_html.py") {
    Write-Host "   OK Module etats_controle_exhaustifs_html.py trouve" -ForegroundColor Green
} else {
    Write-Host "   ERREUR Module etats_controle_exhaustifs_html.py manquant" -ForegroundColor Red
    exit 1
}

# 2. Verifier que les styles CSS sont presents dans etats_financiers.py
Write-Host ""
Write-Host "2. Verification des styles CSS..." -ForegroundColor Yellow
$content = Get-Content "py_backend/etats_financiers.py" -Raw

$css_checks = @{
    ".section {" = "Classe section"
    ".section-header {" = "Classe section-header"
    ".section-content {" = "Classe section-content"
    ".success-box {" = "Boite success"
    ".warning-box {" = "Boite warning"
    ".danger-box {" = "Boite danger"
    ".badge-success {" = "Badge success"
    ".badge-warning {" = "Badge warning"
    ".badge-danger {" = "Badge danger"
    ".badge-critical {" = "Badge critical"
}

$all_css_ok = $true
foreach ($check in $css_checks.GetEnumerator()) {
    if ($content -match [regex]::Escape($check.Key)) {
        Write-Host "   OK $($check.Value)" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR $($check.Value) manquant" -ForegroundColor Red
        $all_css_ok = $false
    }
}

if (-not $all_css_ok) {
    Write-Host ""
    Write-Host "ERREUR Certains styles CSS sont manquants" -ForegroundColor Red
    exit 1
}

# 3. Verifier que le script JavaScript est present
Write-Host ""
Write-Host "3. Verification du script JavaScript..." -ForegroundColor Yellow

$js_checks = @{
    "function toggleSection" = "Fonction toggleSection"
    "document.querySelectorAll('.section-header')" = "Selecteur section-header"
    "section.classList.toggle('active')" = "Toggle active"
}

$all_js_ok = $true
foreach ($check in $js_checks.GetEnumerator()) {
    if ($content -match [regex]::Escape($check.Key)) {
        Write-Host "   OK $($check.Value)" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR $($check.Value) manquant" -ForegroundColor Red
        $all_js_ok = $false
    }
}

if (-not $all_js_ok) {
    Write-Host ""
    Write-Host "ERREUR Le script JavaScript est incomplet" -ForegroundColor Red
    exit 1
}

# 4. Verifier que generate_all_16_etats_controle_html est appele
Write-Host ""
Write-Host "4. Verification de l'appel de la fonction..." -ForegroundColor Yellow

if ($content -match "from etats_controle_exhaustifs_html import generate_all_16_etats_controle_html") {
    Write-Host "   OK Import du module" -ForegroundColor Green
} else {
    Write-Host "   ERREUR Import du module manquant" -ForegroundColor Red
    exit 1
}

if ($content -match "html_etats = generate_all_16_etats_controle_html") {
    Write-Host "   OK Appel de la fonction" -ForegroundColor Green
} else {
    Write-Host "   ERREUR Appel de la fonction manquant" -ForegroundColor Red
    exit 1
}

if ($content -match "html \+= html_etats") {
    Write-Host "   OK Ajout du HTML au resultat" -ForegroundColor Green
} else {
    Write-Host "   ERREUR Ajout du HTML manquant" -ForegroundColor Red
    exit 1
}

# Resume final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUME DU TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "OK Module Python: OK" -ForegroundColor Green
Write-Host "OK Styles CSS: OK" -ForegroundColor Green
Write-Host "OK Script JavaScript: OK" -ForegroundColor Green
Write-Host "OK Integration backend: OK" -ForegroundColor Green
Write-Host ""
Write-Host "SUCCES TOUS LES TESTS SONT PASSES!" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "   1. Tester avec une vraie balance" -ForegroundColor Gray
Write-Host "   2. Verifier l'affichage dans le navigateur" -ForegroundColor Gray
Write-Host "   3. Tester l'API" -ForegroundColor Gray
Write-Host ""
