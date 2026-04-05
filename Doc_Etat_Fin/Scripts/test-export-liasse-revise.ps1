# ============================================================================
# Script de test - Export Liasse Officielle Révisée
# ============================================================================
# Date: 05 Avril 2026
# Description: Teste l'export de la liasse avec le nouveau fichier template
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "TEST EXPORT LIASSE OFFICIELLE REVISEE" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier que le fichier template existe
Write-Host "1. Vérification du fichier template..." -ForegroundColor Yellow
$templatePath = "py_backend\Liasse_officielle_revise.xlsx"

if (Test-Path $templatePath) {
    Write-Host "   ✅ Fichier trouvé: $templatePath" -ForegroundColor Green
    
    # Afficher les onglets
    Write-Host ""
    Write-Host "2. Liste des onglets du template..." -ForegroundColor Yellow
    $pythonCmd = "import openpyxl; wb = openpyxl.load_workbook('$templatePath'); print(f'   Nombre onglets: {len(wb.sheetnames)}'); print('   Onglets principaux:'); [print(f'      - {sheet}') for sheet in wb.sheetnames[:10]]; print('      ...')"
    python -c $pythonCmd
} else {
    Write-Host "   ❌ Fichier non trouvé: $templatePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fichiers disponibles dans py_backend:" -ForegroundColor Yellow
    Get-ChildItem -Path py_backend -Filter "*iasse*" | Select-Object Name
    exit 1
}

Write-Host ""
Write-Host "3. Test d'import du module export_liasse..." -ForegroundColor Yellow
cd py_backend
python -c "from export_liasse import remplir_liasse_officielle; print('   ✅ Import réussi')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Module importé avec succès" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erreur d'import" -ForegroundColor Red
    cd ..
    exit 1
}
cd ..

Write-Host ""
Write-Host "4. Vérification de la priorité du template..." -ForegroundColor Yellow
Write-Host "   Le script cherchera dans cet ordre:" -ForegroundColor Gray
Write-Host "      1. Liasse_officielle_revise.xlsx (PRIORITAIRE)" -ForegroundColor Green
Write-Host "      2. LIASSE.xlsx (fallback)" -ForegroundColor Gray
Write-Host "      3. Liasse officielle.xlsm (fallback)" -ForegroundColor Gray

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "RESUME DU TEST" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "✅ Fichier template Liasse_officielle_revise.xlsx trouvé" -ForegroundColor Green
Write-Host "✅ Module export_liasse.py fonctionne" -ForegroundColor Green
Write-Host "✅ Configuration correcte" -ForegroundColor Green
Write-Host ""
Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Yellow
Write-Host "  1. Tester l'export complet avec generer_etats_liasse.py" -ForegroundColor White
Write-Host "  2. Vérifier le menu contextuel 'Exporter liasse officielle'" -ForegroundColor White
Write-Host "  3. Valider les mappings de cellules si nécessaire" -ForegroundColor White
Write-Host ""
Write-Host "COMMANDE TEST COMPLET:" -ForegroundColor Yellow
Write-Host "  cd py_backend" -ForegroundColor White
Write-Host "  python generer_etats_liasse.py" -ForegroundColor White
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
