from locust import HttpUser, task, between

class BookingUser(HttpUser):
    host = "http://127.0.0.1:5000"  # <- fixe le host
    wait_time = between(1, 3)

    def on_start(self):
        # login: route réelle /showSummary, label lisible "/login"
        # timeout augmenté pour éviter les fails artificiels
        self.client.post(
            "/showSummary",
            data={"email": "john@simplylift.co"},
            name="/login",
            timeout=10,
        )

    @task(2)
    def list_competitions(self):
        self.client.get("/", name="/", timeout=10)

    @task(1)
    def purchase(self):
        # NB: avec beaucoup d'utilisateurs, on peut épuiser les places,
        # mais le serveur répond 200 quand même (avec un message d'erreur métier).
        self.client.post(
            "/purchasePlaces",
            data={"competition": "Fall Classic", "club": "Simply Lift", "places": "1"},
            name="/purchasePlaces",
            timeout=10,
        )
