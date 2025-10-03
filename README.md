Gudlft – P11 OpenClassrooms

Améliorez une application Web Python par des tests et du débogage

Application Flask “light” (sans base de données) pour gérer des compétitions entre clubs : login par e-mail, consultation des compétitions, achat de places contre points, limite de réservation, tableau public des points.
Le projet met l’accent sur tests (unitaires + intégration), gestion d’erreurs, couverture et tests de performance (Locust).

Sommaire

Fonctionnalités

Règles métier

Structure du projet

Prérequis

Installation

Lancer l’application

Tests & Couverture

Performance (Locust)

Rapports livrés

Hygiène du dépôt

Dépannage (FAQ)

Limites connues & pistes

Licence

Fonctionnalités

Authentification par e-mail (liste blanche dans clubs.json)

Page de synthèse : points du club, compétitions, lien “Book”

Réservation de places contre points
(1 point = 1 place)

Tableau public des points sur /points

Déconnexion qui vide la session

Règles métier

Validation à l’achat (POST /purchasePlaces) :

Compétition non passée (on bloque si la date est < maintenant ; format tolérant)

Quantité entière ≥ 1

Stock suffisant (places_required ≤ numberOfPlaces)

Points suffisants (places_required ≤ points)

Plafond 12 places par club et par compétition (cumulé)

Messages flash explicites (succès/erreurs)

Structure du projet
Python_Testing/
  server.py
  clubs.json
  competitions.json
  templates/
    index.html
    welcome.html
    booking.html
    points.html
  tests/
    unit/...
    integration/...
    performance/
      locustfile.py
  docs/
    test-report.md
    perf-report.md
  requirements.txt
  requirements-dev.txt   # (recommandé)
  .gitignore
  README.md

Prérequis

Python 3.11+ (ok 3.13)

pip

(Windows) PowerShell

(Perf) Locust (pip install locust ou via requirements-dev.txt)

Installation
Windows / PowerShell
# à la racine du projet
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
# recommandé pour tests & perf :
pip install -r requirements-dev.txt

macOS / Linux (bash)
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

Lancer l’application
Windows / PowerShell
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP = "server.py"
$env:FLASK_ENV = "development"
flask run   # http://127.0.0.1:5000

macOS / Linux
source .venv/bin/activate
export FLASK_APP=server.py
export FLASK_ENV=development
flask run   # http://127.0.0.1:5000

Tests & Couverture
# Exécuter tous les tests
pytest -q

# Couverture
coverage run -m pytest
coverage report -m
coverage html   # ouvre htmlcov/index.html (Start-Process .\htmlcov\index.html)


Résultats de référence (dev local) : 26 tests PASS, ~97% de couverture.
Les chiffres peuvent varier légèrement selon l’environnement.

Performance (Locust)

Le projet fournit 2 scénarios :

BrowseUser (lecture seule) : GET /, POST /showSummary, GET /points, GET /book/...

BookingUser (achat) : POST /purchasePlaces

Option B (critère “succès métier”) : une requête est comptée success si

le message succès “Great-booking complete!” est présent, ou

un message métier attendu (points/places insuffisants, limite 12, comp passée, “Invalid quantity”…).

Lancer Locust (UI)
# Terminal 1 : serveur Flask
$env:FLASK_APP = "server.py"; $env:FLASK_ENV = "development"; flask run
# Terminal 2 : Locust
locust -f tests\performance\locustfile.py --host http://127.0.0.1:5000
# UI : http://localhost:8089

Headless + CSV
locust -f tests\performance\locustfile.py --host http://127.0.0.1:5000 `
  --headless -u 20 -r 2 -t 2m --csv perf_run


Référence locale (dev) : ~12–14 req/s agrégé, p50 ≈ 3 ms, p95 ≈ 4–5 ms, 0% fails (Option B).
En prod réelle, utiliser un serveur WSGI (gunicorn/waitress) derrière reverse-proxy pour des mesures réalistes.

Rapports livrés

Tests : docs/test-report.md

stratégie (unit + intégration + sad paths), résultats, couverture, commandes de repro

Performance : docs/perf-report.md

scénarios, critère Option B, résultats, commandes, CSV (perf_run*.csv)

Coverage HTML : généré dans htmlcov/index.html

Hygiène du dépôt

À ignorer (ne pas versionner) : environnements, caches, artefacts de build/coverage/perf, fichiers IDE/OS.

.gitignore recommandé :

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so

# Env & caches
.venv/
env/
venv/
.pytest_cache/

# Coverage
.coverage
htmlcov/

# Perf outputs
perf_run*

# IDE / OS
.vscode/
.idea/
.DS_Store

# Builds
dist/
build/


Nettoyer si déjà suivis :

git rm -r --cached .idea .venv __pycache__ .pytest_cache htmlcov dist build .coverage .DS_Store perf_run*
git add .gitignore
git commit -m "chore: repo hygiene (.gitignore)"
git push

Dépannage (FAQ)

ConnectionRefusedError avec Locust : démarre Flask avant Locust, et passe --host http://127.0.0.1:5000.

bytes can only contain ASCII literal characters : dans le locustfile, compare resp.text (str) et non resp.content (bytes) si tu as des accents.

Aucun test ne s’exécute : vérifie que tu lances pytest à la racine du projet et que le venv est activé.

Flask ne se lance pas : vérifie FLASK_APP=server.py et l’activation de l’environnement.

Limites connues & pistes

Persistance : état en mémoire → perdre l’état au redémarrage (piste : SQLite/SQLAlchemy).

Sécurité : SECRET_KEY à externaliser (variable d’env), CSRF (Flask-WTF), rate limiting.

Ops : CI GitHub Actions (pytest + coverage), badge de couverture, logs structurés.

Licence

Ce projet est fourni à des fins pédagogiques (OpenClassrooms P11).
Adapter la licence selon votre besoin (MIT recommandé pour un dépôt public).

Auteur : @r3n3gat — Contributions, PR & issues bienvenues ✨
