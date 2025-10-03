# Rapport de tests – Gudlft (Phase 1 & 2)

## Contexte
Application Flask sans base de données ; données en JSON, état en mémoire. Objectif : gestion de compétitions entre clubs (hébergement, inscriptions, frais et administration). Les règles clés testées : points vs places (1 point = 1 place), plafond **12** par club/compétition (cumul), blocage des compétitions passées, validation des entrées, messages flash lisibles.

## Environnement
- OS : Windows (PowerShell)
- Python : 3.13.5
- Outils : `pytest 8.4.x`, `coverage`, (perf séparée via Locust 2.40.x)
- Dossier projet : `Python_Testing/`

## Installation & exécution (reproductible)
```powershell
# Créer/activer l'environnement
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # si présent
```
## Résultats
```
Tests : 26 passed
Couverture : 97% (coverage report -m)
Rapport HTML : htmlcov/index.html

```
