
# Rapport de performance – Gudlft (Locust)

## Contexte & objectif
Mesurer latence/débit sur les endpoints principaux en environnement local. L’application garde son **état en mémoire** (pas de DB) : sous charge, des rejets métier (points/places/limite 12) sont **attendus**.

## Environnement
- Localhost (`http://127.0.0.1:5000`), serveur Flask de dev
- Windows + Python 3.13.5
- Locust 2.40.x (gevent)
- Scénarios Locust dans `tests/performance/locustfile.py`

## Critère de succès
On marque une requête **“succès”** si :
- **Succès explicite** : `Great-booking complete!`
- **OU** message métier **attendu** (ex. `Pas assez de points`, `Pas assez de places disponibles`, `Maximum 12...`, `Competition already finished`, `Invalid quantity`).

But : refléter la réalité fonctionnelle **sans** gonfler artificiellement le failure rate quand l’état s’épuise.

## Scénarios
- **BrowseUser** (lecture seule) : `GET /`, `POST /showSummary`, `GET /points`, `GET /book/<comp>/<club>`
- **BookingUser** (achat) : `POST /purchasePlaces`

## Procédure de test (reproductible)
Terminal 1 – serveur :
```powershell
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP="server.py"
$env:FLASK_ENV="development"
flask run
```
## Run headless – 20 users, 2 min (Option B)
- Throughput agrégé : ~12–14 req/s (dernier snapshot ≈ 12.7 req/s)
- Latences : p50 ≈ 3 ms, p95 ≈ 4–5 ms, p99 ≤ 17 ms
- Fails : 0% (succès = achat OK **ou** message métier attendu)
- Commande : locust -f tests/performance/locustfile.py --host http://127.0.0.1:5000 --headless -u 20 -r 2 -t 2m --csv perf_run
- CSV : perf_run_stats.csv, perf_run_failures.csv
