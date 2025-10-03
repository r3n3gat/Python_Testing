# On considère comme "succès" les réponses métier attendues
# (achat réussi OU messages d'erreur métier prévus), afin de mesurer
# la perf sans faire artificiellement grimper le failure rate.
#
# Lancer :
#   locust -f tests/performance/locustfile.py --host http://127.0.0.1:5000
#   (ou --headless -u 20 -r 2 -t 1m --csv perf_run)

from locust import HttpUser, task, between

TEST_EMAIL = "john@simplylift.co"  # présent dans clubs.json
COMP_NAME = "Fall Classic"
CLUB_NAME = "Simply Lift"  # utilisé seulement pour la page /book/<comp>/<club>

# Réponses "métier" considérées comme OK (en plus du succès explicite)
EXPECTED_OK_MARKERS = [
    "Great-booking complete!",
    "Pas assez de points",
    "Pas assez de places disponibles",
    "Maximum 12 places par club sur une compétition",
    "Competition already finished",
    "Invalid quantity",
    "Invalid quantity (>=1)",
    "Donn",  # garde large si "Données invalides..." apparaît
]


class BrowseUser(HttpUser):
    """
    Parcours lecture seule : home, login, points, page booking.
    Utilisé pour un baseline de latence/throughput sans modifier l'état.
    """
    wait_time = between(0.5, 2.0)

    def on_start(self):
        self.client.get("/", name="GET /", timeout=10)
        self.client.post(
            "/showSummary",
            data={"email": TEST_EMAIL},
            name="POST /showSummary",
            timeout=10,
        )

    @task(3)
    def home(self):
        self.client.get("/", name="GET /", timeout=10)

    @task(2)
    def points(self):
        self.client.get("/points", name="GET /points", timeout=10)

    @task(1)
    def booking_page(self):
        self.client.get(
            f"/book/{COMP_NAME}/{CLUB_NAME}",
            name=f"GET /book/{COMP_NAME}/{CLUB_NAME}",
            timeout=10,
        )


class BookingUser(HttpUser):
    """
    Parcours avec tentative d'achat réelle.
    On marque la requête "success" si :
      - le message de succès est présent, ou
      - un message d'erreur métier attendu est renvoyé
        (points/places insuffisants, limite 12, compétition passée, etc.)
    Ainsi on évalue la perf indépendamment de l'état métier mutable.
    """
    wait_time = between(1, 3)

    def on_start(self):
        self.client.get("/", name="GET /", timeout=10)
        self.client.post(
            "/showSummary",
            data={"email": TEST_EMAIL},
            name="POST /showSummary",
            timeout=10,
        )

    @task
    def purchase(self):
        # Ne pas envoyer 'club' : le serveur se base sur la session
        with self.client.post(
            "/purchasePlaces",
            data={"competition": COMP_NAME, "places": "1"},
            name="POST /purchasePlaces",
            timeout=10,
            catch_response=True,
        ) as resp:
            # Compare des chaînes (UTF-8), pas des bytes ASCII
            try:
                body_text = resp.text or ""
            except Exception:
                # fallback robuste si .text pose souci
                body_text = (resp.content or b"").decode("utf-8", errors="ignore")

            if any(marker in body_text for marker in EXPECTED_OK_MARKERS):
                resp.success()  # succès métier (achat OK ou rejet prévu)
            else:
                resp.failure("Réponse non reconnue (unexpected business state)")
