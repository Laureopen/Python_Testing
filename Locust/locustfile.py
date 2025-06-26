from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Attente entre les requêtes (en secondes)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task
    def login_and_book(self):
        # Simule une connexion avec un email valide
        response = self.client.post("/showSummary", data={"email": "kate@shelifts.co.uk"})

        # Simule une réservation (attention à adapter selon les données en base)
        self.client.post("/purchasePlaces", data={
            "club": "Simply Lift",
            "competition": "Spring Festival",
            "places": "1"
        })
