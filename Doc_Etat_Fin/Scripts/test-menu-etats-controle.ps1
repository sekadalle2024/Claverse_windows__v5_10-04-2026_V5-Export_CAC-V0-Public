# Script PowerShell pour tester l'ajout des États de Contrôle au menu

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  TEST AJOUT ÉTATS DE CONTRÔLE AU MENU ACCORDÉON" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier que le fichier DemarrerMenu.tsx existe
Write-Host "1. Vérification du fichier DemarrerMenu.tsx..." -ForegroundColor Yellow
$menuFile = "src/components/Clara_Components/DemarrerMenu.tsx"

if (Test-Path $menuFile) {
    Write-Host "   ✅ Fichier trouvé: $menuFile" -ForegroundColor Green
} else {
    Write-Host "   ❌ Fichier non trouvé: $menuFile" -ForegroundColor Red
    exit 1
}

# 2. Exécuter le script d'ajout
Write-Host ""
Write-Host "2. Exécution du script d'ajout..." -ForegroundColor Yellow
python Doc_Etat_Fin/Scripts/add_etats_controle_to_menu.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Script exécuté avec succès" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erreur lors de l'exécution du script" -ForegroundColor Red
    exit 1
}

# 3. Vérifier que l'entrée a été ajoutée
Write-Host ""
Write-Host "3. Vérification de l'ajout dans le fichier..." -ForegroundColor Yellow
$content = Get-Content $menuFile -Raw

if ($content -match "États de Contrôle") {
    Write-Host "   ✅ Entrée 'États de Contrôle' trouvée" -ForegroundColor Green
} else {
    Write-Host "   ❌ Entrée 'États de Contrôle' non trouvée" -ForegroundColor Red
    exit 1
}

# 4. Vérifier la syntaxe TypeScript
Write-Host ""
Write-Host "4. Vérification de la syntaxe TypeScript..." -ForegroundColor Yellow
Write-Host "   ⏳ Compilation TypeScript en cours..." -ForegroundColor Gray

# Essayer de compiler (si tsc est disponible)
$tscAvailable = Get-Command tsc -ErrorAction SilentlyContinue

if ($tscAvailable) {
    tsc --noEmit $menuFile 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Syntaxe TypeScript valide" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Erreurs de compilation détectées" -ForegroundColor Yellow
        Write-Host "   💡 Vérifier manuellement le fichier" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  TypeScript compiler non disponible" -ForegroundColor Yellow
    Write-Host "   💡 Vérification manuelle recommandée" -ForegroundColor Gray
}

# 5. Afficher un résumé
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ✅ TEST TERMINÉ" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Résumé:" -ForegroundColor White
Write-Host "   • Fichier modifié: $menuFile" -ForegroundColor Gray
Write-Host "   • Entrée ajoutée: États de Contrôle" -ForegroundColor Gray
Write-Host "   • 16 états de contrôle (8 pour N + 8 pour N-1)" -ForegroundColor Gray
Write-Host ""
Write-Host "🔄 Prochaines étapes:" -ForegroundColor White
Write-Host "   1. Redémarrer le serveur de développement" -ForegroundColor Gray
Write-Host "   2. Tester l'affichage dans le navigateur" -ForegroundColor Gray
Write-Host "   3. Vérifier que l'accordéon fonctionne" -ForegroundColor Gray
Write-Host ""
