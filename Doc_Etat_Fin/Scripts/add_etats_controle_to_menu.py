# -*- coding: utf-8 -*-
"""
Script pour ajouter les États de Contrôle au menu accordéon
Ajoute une nouvelle entrée dans DemarrerMenu.tsx
"""

import re
import os


def lire_fichier(chemin):
    """Lit le contenu d'un fichier"""
    with open(chemin, 'r', encoding='utf-8') as f:
        return f.read()


def ecrire_fichier(chemin, contenu):
    """Écrit le contenu dans un fichier"""
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write(contenu)


def ajouter_etats_controle_menu(contenu_menu):
    """Ajoute l'entrée États de Contrôle dans le menu"""
    
    # Chercher la section E-Révision
    pattern_e_revision = r'(case "E-Révision":.*?break;)'
    
    # Nouvelle entrée pour États de Contrôle
    nouvelle_entree = '''
        case "États de Contrôle":
          return {
            title: "📊 États de Contrôle Exhaustifs",
            description: "16 états de contrôle pour les exercices N et N-1",
            content: (
              <div className="space-y-4">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                  <h3 className="font-bold text-blue-900 mb-2">
                    🔍 États de Contrôle SYSCOHADA
                  </h3>
                  <p className="text-blue-800 text-sm">
                    Génération automatique de 16 états de contrôle exhaustifs pour valider
                    la cohérence des états financiers selon le référentiel SYSCOHADA Révisé.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-lg shadow">
                    <h4 className="font-semibold text-gray-900 mb-2">📈 Exercice N (8 états)</h4>
                    <ul className="text-sm text-gray-700 space-y-1">
                      <li>• Statistiques de Couverture</li>
                      <li>• Équilibre du Bilan</li>
                      <li>• Cohérence Résultat</li>
                      <li>• Comptes Non Intégrés</li>
                      <li>• Comptes avec Sens Inversé</li>
                      <li>• Comptes Créant un Déséquilibre</li>
                      <li>• Hypothèse d'Affectation du Résultat</li>
                      <li>• Comptes avec Sens Anormal par Nature</li>
                    </ul>
                  </div>

                  <div className="bg-white p-4 rounded-lg shadow">
                    <h4 className="font-semibold text-gray-900 mb-2">📉 Exercice N-1 (8 états)</h4>
                    <ul className="text-sm text-gray-700 space-y-1">
                      <li>• Statistiques de Couverture</li>
                      <li>• Équilibre du Bilan</li>
                      <li>• Cohérence Résultat</li>
                      <li>• Comptes Non Intégrés</li>
                      <li>• Comptes avec Sens Inversé</li>
                      <li>• Comptes Créant un Déséquilibre</li>
                      <li>• Hypothèse d'Affectation du Résultat</li>
                      <li>• Comptes avec Sens Anormal par Nature</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                  <h4 className="font-semibold text-green-900 mb-2">✅ Contrôles Automatiques</h4>
                  <ul className="text-sm text-green-800 space-y-1">
                    <li>• Vérification de l'équilibre Actif = Passif</li>
                    <li>• Cohérence entre Résultat CR et Résultat Bilan</li>
                    <li>• Détection des comptes avec sens anormal</li>
                    <li>• Validation de l'hypothèse d'affectation</li>
                    <li>• Analyse des comptes non intégrés</li>
                  </ul>
                </div>

                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
                  <h4 className="font-semibold text-yellow-900 mb-2">💡 Format de Sortie</h4>
                  <p className="text-sm text-yellow-800">
                    Les états sont générés en format HTML avec accordéons cliquables,
                    badges colorés selon la gravité, et tableaux détaillés pour chaque contrôle.
                  </p>
                </div>
              </div>
            ),
          };
'''
    
    # Insérer après E-Révision
    contenu_modifie = re.sub(
        pattern_e_revision,
        r'\1\n' + nouvelle_entree,
        contenu_menu,
        flags=re.DOTALL
    )
    
    return contenu_modifie


def ajouter_dans_liste_modes(contenu_menu):
    """Ajoute 'États de Contrôle' dans la liste des modes"""
    
    # Chercher la liste des modes
    pattern_modes = r'(const modes = \[.*?"E-Révision")'
    
    # Ajouter États de Contrôle
    contenu_modifie = re.sub(
        pattern_modes,
        r'\1, "États de Contrôle"',
        contenu_menu,
        flags=re.DOTALL
    )
    
    return contenu_modifie


def main():
    """Fonction principale"""
    print("=" * 70)
    print("  AJOUT DES ÉTATS DE CONTRÔLE AU MENU ACCORDÉON")
    print("=" * 70)
    print()
    
    # Chemin du fichier DemarrerMenu.tsx
    chemin_menu = "src/components/Clara_Components/DemarrerMenu.tsx"
    
    if not os.path.exists(chemin_menu):
        print(f"❌ Fichier non trouvé: {chemin_menu}")
        return
    
    print(f"📂 Lecture de {chemin_menu}...")
    contenu = lire_fichier(chemin_menu)
    
    # Vérifier si déjà présent
    if "États de Contrôle" in contenu:
        print("⚠️  'États de Contrôle' est déjà présent dans le menu")
        return
    
    print("✏️  Ajout de l'entrée 'États de Contrôle'...")
    contenu = ajouter_etats_controle_menu(contenu)
    
    print("✏️  Ajout dans la liste des modes...")
    contenu = ajouter_dans_liste_modes(contenu)
    
    print(f"💾 Sauvegarde de {chemin_menu}...")
    ecrire_fichier(chemin_menu, contenu)
    
    print()
    print("=" * 70)
    print("  ✅ AJOUT TERMINÉ AVEC SUCCÈS")
    print("=" * 70)
    print()
    print("📋 Prochaines étapes:")
    print("  1. Vérifier que le composant compile sans erreur")
    print("  2. Tester l'affichage dans le menu")
    print("  3. Créer le composant EtatsControleAccordionRenderer.tsx si nécessaire")
    print()


if __name__ == "__main__":
    main()
