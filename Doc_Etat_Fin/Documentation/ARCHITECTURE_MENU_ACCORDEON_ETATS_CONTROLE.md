# ARCHITECTURE MENU ACCORDÉON - ÉTATS DE CONTRÔLE

## VUE D'ENSEMBLE

Ce document décrit l'architecture complète pour intégrer les 16 états de contrôle dans le menu accordéon de ClaraVerse.

## COMPOSANTS NÉCESSAIRES

### 1. Composant React Principal

**Fichier:** `src/components/Clara_Components/EtatsControleAccordionRenderer.tsx`

**Responsabilités:**
- Recevoir les données HTML des 16 états
- Parser et structurer les sections
- Gérer l'état d'ouverture/fermeture des accordéons
- Appliquer les styles CSS appropriés

**Props:**
```typescript
interface EtatsControleAccordionRendererProps {
  htmlContent: string;  // HTML complet des 16 états
  exerciceN?: string;   // Année de l'exercice N
  exerciceN1?: string;  // Année de l'exercice N-1
}
```

**Structure:**
```typescript
const EtatsControleAccordionRenderer: React.FC<Props> = ({ htmlContent, exerciceN, exerciceN1 }) => {
  const [openSections, setOpenSections] = useState<Set<number>>(new Set());
  
  // Parser le HTML en sections
  const sections = parseHtmlSections(htmlContent);
  
  // Gérer l'ouverture/fermeture
  const toggleSection = (index: number) => {
    const newOpen = new Set(openSections);
    if (newOpen.has(index)) {
      newOpen.delete(index);
    } else {
      newOpen.add(index);
    }
    setOpenSections(newOpen);
  };
  
  return (
    <div className="etats-controle-container">
      {sections.map((section, index) => (
        <AccordionSection
          key={index}
          section={section}
          isOpen={openSections.has(index)}
          onToggle={() => toggleSection(index)}
        />
      ))}
    </div>
  );
};
```

### 2. Composant Section Accordéon

**Fichier:** `src/components/Clara_Components/AccordionSection.tsx`

**Responsabilités:**
- Afficher une section individuelle
- Gérer l'animation d'ouverture/fermeture
- Afficher les badges et boîtes colorées

**Props:**
```typescript
interface AccordionSectionProps {
  section: ParsedSection;
  isOpen: boolean;
  onToggle: () => void;
}

interface ParsedSection {
  id: string;
  title: string;
  badge: BadgeInfo;
  content: string;
  exercice: 'N' | 'N-1';
}

interface BadgeInfo {
  type: 'success' | 'warning' | 'danger' | 'info' | 'critical';
  text: string;
}
```

### 3. Fichier CSS

**Fichier:** `src/components/Clara_Components/EtatsControleAccordionRenderer.css`

**Classes principales:**
```css
/* Container principal */
.etats-controle-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* Section accordéon */
.accordion-section {
  margin-bottom: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

/* En-tête cliquable */
.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  background: #f9fafb;
  transition: background 0.2s;
}

.accordion-header:hover {
  background: #f3f4f6;
}

/* Contenu */
.accordion-content {
  padding: 1rem;
  background: white;
}

/* Badges */
.badge-success { background: #10b981; color: white; }
.badge-warning { background: #f59e0b; color: white; }
.badge-danger { background: #ef4444; color: white; }
.badge-info { background: #3b82f6; color: white; }
.badge-critical { background: #dc2626; color: white; }

/* Boîtes colorées */
.success-box { background: #d1fae5; border-left: 4px solid #10b981; }
.warning-box { background: #fef3c7; border-left: 4px solid #f59e0b; }
.danger-box { background: #fee2e2; border-left: 4px solid #ef4444; }
.info-box { background: #dbeafe; border-left: 4px solid #3b82f6; }
```

## FLUX DE DONNÉES

### 1. Backend → Frontend

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python)                         │
├─────────────────────────────────────────────────────────────┤
│  py_backend/etats_controle_exhaustifs_html.py               │
│  ↓                                                           │
│  generate_all_16_etats_controle_html()                      │
│  ↓                                                           │
│  Retourne: HTML complet (16 sections)                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    API ENDPOINT                             │
├─────────────────────────────────────────────────────────────┤
│  POST /api/etats-controle                                   │
│  Body: { balance_n, balance_n1 }                            │
│  Response: { html: "...", exercice_n: "2024", ... }         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
├─────────────────────────────────────────────────────────────┤
│  claraApiService.ts                                         │
│  ↓                                                           │
│  fetchEtatsControle(balanceN, balanceN1)                    │
│  ↓                                                           │
│  EtatsControleAccordionRenderer                             │
│  ↓                                                           │
│  Affichage des 16 accordéons                                │
└─────────────────────────────────────────────────────────────┘
```

### 2. Structure des Données

**Réponse API:**
```json
{
  "html": "<div class='accordion-section'>...</div>...",
  "exercice_n": "2024",
  "exercice_n1": "2023",
  "nb_sections": 16,
  "metadata": {
    "nb_comptes_n": 441,
    "nb_comptes_n1": 405,
    "date_generation": "2026-04-05T10:30:00"
  }
}
```

**Sections Parsées:**
```typescript
interface ParsedSection {
  id: string;              // "etat-1-n", "etat-2-n1", etc.
  title: string;           // "État 1: Statistiques de Couverture"
  exercice: 'N' | 'N-1';   // Exercice concerné
  badge: {
    type: 'success' | 'warning' | 'danger' | 'info' | 'critical';
    text: string;          // "✅ Validé", "⚠️ Attention", etc.
  };
  content: string;         // HTML du contenu
  stats?: {                // Statistiques optionnelles
    nb_comptes?: number;
    nb_anomalies?: number;
    taux_couverture?: number;
  };
}
```

## INTÉGRATION DANS DEMARRERMENU.TSX

### 1. Ajout dans la Liste des Modes

```typescript
const modes = [
  "E-Audit",
  "E-CIA Exam",
  "E-Révision",
  "États de Contrôle",  // ← NOUVEAU
  // ... autres modes
];
```

### 2. Ajout du Case dans renderModeContent()

```typescript
case "États de Contrôle":
  return {
    title: "📊 États de Contrôle Exhaustifs",
    description: "16 états de contrôle pour les exercices N et N-1",
    content: (
      <div className="space-y-4">
        {/* Description et guide d'utilisation */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <h3 className="font-bold text-blue-900 mb-2">
            🔍 États de Contrôle SYSCOHADA
          </h3>
          <p className="text-blue-800 text-sm">
            Génération automatique de 16 états de contrôle exhaustifs
          </p>
        </div>

        {/* Grille des états */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h4 className="font-semibold text-gray-900 mb-2">
              📈 Exercice N (8 états)
            </h4>
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
            <h4 className="font-semibold text-gray-900 mb-2">
              📉 Exercice N-1 (8 états)
            </h4>
            <ul className="text-sm text-gray-700 space-y-1">
              {/* Même liste pour N-1 */}
            </ul>
          </div>
        </div>

        {/* Bouton de déclenchement */}
        <button
          onClick={handleGenerateEtatsControle}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
        >
          🚀 Générer les États de Contrôle
        </button>

        {/* Affichage des résultats */}
        {etatsControleData && (
          <EtatsControleAccordionRenderer
            htmlContent={etatsControleData.html}
            exerciceN={etatsControleData.exercice_n}
            exerciceN1={etatsControleData.exercice_n1}
          />
        )}
      </div>
    ),
  };
```

### 3. Fonction de Génération

```typescript
const handleGenerateEtatsControle = async () => {
  try {
    setLoading(true);
    
    // Récupérer les balances depuis le localStorage ou l'API
    const balanceN = getBalanceFromStorage('N');
    const balanceN1 = getBalanceFromStorage('N-1');
    
    if (!balanceN) {
      showNotification('error', 'Balance N non trouvée');
      return;
    }
    
    // Appeler l'API
    const response = await claraApiService.fetchEtatsControle(
      balanceN,
      balanceN1
    );
    
    // Stocker les résultats
    setEtatsControleData(response);
    
    showNotification('success', '16 états de contrôle générés');
  } catch (error) {
    console.error('Erreur génération états:', error);
    showNotification('error', 'Erreur lors de la génération');
  } finally {
    setLoading(false);
  }
};
```

## SERVICE API

### Fichier: src/services/claraApiService.ts

```typescript
export const claraApiService = {
  // ... autres méthodes
  
  /**
   * Génère les 16 états de contrôle
   */
  async fetchEtatsControle(
    balanceN: BalanceData,
    balanceN1?: BalanceData
  ): Promise<EtatsControleResponse> {
    const response = await fetch(`${API_BASE_URL}/api/etats-controle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        balance_n: balanceN,
        balance_n1: balanceN1,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de la génération des états');
    }
    
    return response.json();
  },
};

interface EtatsControleResponse {
  html: string;
  exercice_n: string;
  exercice_n1?: string;
  nb_sections: number;
  metadata: {
    nb_comptes_n: number;
    nb_comptes_n1?: number;
    date_generation: string;
  };
}
```

## ENDPOINT BACKEND

### Fichier: py_backend/main.py

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from etats_controle_exhaustifs_html import generate_all_16_etats_controle_html

app = FastAPI()

class EtatsControleRequest(BaseModel):
    balance_n: dict
    balance_n1: dict = None

@app.post("/api/etats-controle")
async def generate_etats_controle(request: EtatsControleRequest):
    """Génère les 16 états de contrôle"""
    try:
        # Générer le HTML
        html_content = generate_all_16_etats_controle_html(
            request.balance_n,
            request.balance_n1
        )
        
        # Extraire les métadonnées
        nb_comptes_n = len(request.balance_n.get('comptes', []))
        nb_comptes_n1 = len(request.balance_n1.get('comptes', [])) if request.balance_n1 else 0
        
        return {
            "html": html_content,
            "exercice_n": request.balance_n.get('exercice', 'N'),
            "exercice_n1": request.balance_n1.get('exercice', 'N-1') if request.balance_n1 else None,
            "nb_sections": 16 if request.balance_n1 else 8,
            "metadata": {
                "nb_comptes_n": nb_comptes_n,
                "nb_comptes_n1": nb_comptes_n1,
                "date_generation": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## TESTS

### 1. Test Unitaire du Composant

**Fichier:** `src/components/Clara_Components/__tests__/EtatsControleAccordionRenderer.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import EtatsControleAccordionRenderer from '../EtatsControleAccordionRenderer';

describe('EtatsControleAccordionRenderer', () => {
  const mockHtml = `
    <div class="accordion-section">
      <h2>État 1: Test</h2>
      <div class="content">Contenu test</div>
    </div>
  `;
  
  it('affiche les sections', () => {
    render(<EtatsControleAccordionRenderer htmlContent={mockHtml} />);
    expect(screen.getByText('État 1: Test')).toBeInTheDocument();
  });
  
  it('ouvre/ferme les sections au clic', () => {
    render(<EtatsControleAccordionRenderer htmlContent={mockHtml} />);
    const header = screen.getByText('État 1: Test');
    
    fireEvent.click(header);
    expect(screen.getByText('Contenu test')).toBeVisible();
    
    fireEvent.click(header);
    expect(screen.getByText('Contenu test')).not.toBeVisible();
  });
});
```

### 2. Test d'Intégration

**Fichier:** `Doc_Etat_Fin/Scripts/test-integration-complete.ps1`

```powershell
# Test complet de l'intégration

Write-Host "Test 1: Backend génère le HTML" -ForegroundColor Yellow
python test-16-etats-rapide.py

Write-Host "Test 2: API endpoint répond" -ForegroundColor Yellow
curl -X POST http://localhost:8000/api/etats-controle `
  -H "Content-Type: application/json" `
  -d @test-data.json

Write-Host "Test 3: Frontend affiche les accordéons" -ForegroundColor Yellow
# Ouvrir le navigateur et vérifier manuellement
```

## CHECKLIST D'INTÉGRATION

### Backend
- [x] Module `etats_controle_exhaustifs_html.py` créé
- [x] Fonction `generate_all_16_etats_controle_html()` implémentée
- [x] Tests unitaires validés
- [ ] Endpoint API `/api/etats-controle` créé
- [ ] Tests d'intégration API validés

### Frontend
- [ ] Composant `EtatsControleAccordionRenderer.tsx` créé
- [ ] Fichier CSS `EtatsControleAccordionRenderer.css` créé
- [ ] Service API `claraApiService.ts` mis à jour
- [ ] Intégration dans `DemarrerMenu.tsx`
- [ ] Tests unitaires React validés

### Documentation
- [x] Architecture documentée
- [x] Guide d'utilisation créé
- [x] Scripts de test créés
- [ ] Documentation utilisateur finale

## PROCHAINES ÉTAPES

1. **Créer le composant React** `EtatsControleAccordionRenderer.tsx`
2. **Créer le fichier CSS** avec tous les styles nécessaires
3. **Mettre à jour** `claraApiService.ts` avec la nouvelle méthode
4. **Intégrer dans** `DemarrerMenu.tsx` avec le script d'ajout
5. **Créer l'endpoint API** dans `main.py`
6. **Tester l'intégration complète** avec les scripts fournis

---

**Date:** 05 Avril 2026  
**Statut:** Architecture définie, prête pour implémentation  
**Auteur:** Kiro AI Assistant
