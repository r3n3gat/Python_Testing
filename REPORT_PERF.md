# Rapport de performance

## Environnement
- Machine locale (Windows, Python venv)
- Application Flask (server.py) en mode développement
- Données en mémoire (JSON), pas de DB

## Outils & Scénarios
- **Locust 2.40.4**
- Scénario utilisateur :
  - POST `/showSummary` (login) – label “/login”
  - GET `/` (liste)
  - POST `/purchasePlaces` (achat 1 place)

## Paramètres de charge
- 10 utilisateurs, ramp-up 2/s
- Durée ~1–2 min (arrêt manuel)

## Résultats (p95)
- GET `/` : **3 ms**  (objectif ≤ 5000 ms) → ✅
- POST `/purchasePlaces` : **4 ms** (objectif ≤ 2000 ms) → ✅
- POST `/login` : **6 ms** (indicatif)
- Agrégé : p95 **3 ms**
- Total : **473 requêtes**, **0 échec**

## Observations
- Aucune saturation observée à cette charge.
- Les latences sont très faibles (application et I/O en mémoire).

## Conclusion
- Les objectifs de performance Phase 1/2 sont **atteints**.
