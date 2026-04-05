# MÉMO: PROBLÈMES COURANTS AVEC LES F-STRINGS PYTHON

## RÈGLE FONDAMENTALE

**Les expressions f-string ne peuvent PAS contenir de backslashes (`\`)**

## ERREURS COURANTES

### 1. Apostrophes Échappées

#### ❌ INCORRECT
```python
text = f"L\'utilisateur a dit: {message}"
text = f'C\'est une erreur'
```

#### ✅ CORRECT
```python
# Solution 1: Utiliser l'autre type de guillemets
text = f"L'utilisateur a dit: {message}"
text = f"C'est correct"

# Solution 2: Variable intermédiaire
apostrophe_text = "L'utilisateur a dit"
text = f"{apostrophe_text}: {message}"
```

### 2. Guillemets Échappés

#### ❌ INCORRECT
```python
html = f"<div class=\"{class_name}\">Contenu</div>"
```

#### ✅ CORRECT
```python
# Solution 1: Utiliser l'autre type de guillemets
html = f'<div class="{class_name}">Contenu</div>'

# Solution 2: Triple guillemets
html = f"""<div class="{class_name}">Contenu</div>"""
```

### 3. Caractères Spéciaux

#### ❌ INCORRECT
```python
text = f"Ligne 1\\nLigne 2: {value}"
path = f"C:\\Users\\{username}\\Documents"
```

#### ✅ CORRECT
```python
# Solution 1: Variable intermédiaire
newline = "\n"
text = f"Ligne 1{newline}Ligne 2: {value}"

# Solution 2: Concaténation
text = f"Ligne 1\nLigne 2: {value}"  # \n en dehors de l'expression

# Pour les chemins Windows
path = f"C:/Users/{username}/Documents"  # Utiliser /
# ou
base_path = "C:\\Users"
path = f"{base_path}\\{username}\\Documents"
```

### 4. Expressions Conditionnelles Complexes

#### ❌ INCORRECT
```python
html = f"<p>{\'Oui\' if condition else \'Non\'}</p>"
```

#### ✅ CORRECT
```python
# Solution 1: Variable intermédiaire
result = "Oui" if condition else "Non"
html = f"<p>{result}</p>"

# Solution 2: Fonction
def get_text(condition):
    return "Oui" if condition else "Non"

html = f"<p>{get_text(condition)}</p>"
```

## PATTERNS RECOMMANDÉS

### Pattern 1: Variables Pré-définies
```python
# Définir toutes les variables AVANT le f-string
titre = "État de contrôle"
description = "Vérification de l'équilibre"
status = "Validé" if is_valid else "En erreur"

html = f"""
<div>
    <h1>{titre}</h1>
    <p>{description}</p>
    <span>{status}</span>
</div>
"""
```

### Pattern 2: Dictionnaire de Textes
```python
# Utiliser un dictionnaire pour les textes avec apostrophes
TEXTS = {
    'success': "L'opération a réussi",
    'error': "Une erreur s'est produite",
    'warning': "Attention à l'équilibre"
}

message = TEXTS['success']
html = f"<p>{message}</p>"
```

### Pattern 3: Fonction de Formatage
```python
def format_message(type_msg, value):
    """Retourne un message formaté"""
    messages = {
        'balance': f"La balance contient {value} comptes",
        'equilibre': f"L'équilibre est de {value} FCFA",
        'resultat': f"Le résultat s'élève à {value} FCFA"
    }
    return messages.get(type_msg, "Message inconnu")

html = f"<p>{format_message('balance', 150)}</p>"
```

## CHECKLIST DE VÉRIFICATION

Avant de commiter du code avec des f-strings:

- [ ] Aucun `\'` dans les expressions f-string
- [ ] Aucun `\"` dans les expressions f-string
- [ ] Aucun `\\n`, `\\t`, `\\r` dans les expressions f-string
- [ ] Aucun chemin Windows avec `\\` dans les expressions f-string
- [ ] Les textes avec apostrophes sont dans des variables
- [ ] Les expressions conditionnelles complexes sont simplifiées
- [ ] Le code a été testé et fonctionne

## COMMANDES DE DÉTECTION

### Rechercher les backslashes dans les f-strings
```bash
# Dans tous les fichiers Python
grep -rn "f\".*\\\\" *.py
grep -rn "f'.*\\\\" *.py

# Dans un dossier spécifique
grep -rn "f\".*\\\\" py_backend/*.py
grep -rn "f'.*\\\\" py_backend/*.py
```

### Rechercher les apostrophes échappées
```bash
grep -rn "f\".*\\\\'.*\"" *.py
grep -rn "f'.*\\\\'.*'" *.py
```

## OUTILS D'AIDE

### Linter Configuration (.pylintrc)
```ini
[MESSAGES CONTROL]
enable=anomalous-backslash-in-string
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Vérifier les backslashes dans les f-strings
if git diff --cached --name-only | grep '\.py$' | xargs grep -n "f[\"'].*\\\\"; then
    echo "❌ ERREUR: Backslash détecté dans un f-string"
    echo "Les f-strings ne peuvent pas contenir de backslashes"
    exit 1
fi
```

## RESSOURCES

- [PEP 498 - Literal String Interpolation](https://www.python.org/dev/peps/pep-0498/)
- [Python f-strings Documentation](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)
- [Common f-string Mistakes](https://realpython.com/python-f-strings/#common-mistakes)

Date: 05 Avril 2026
