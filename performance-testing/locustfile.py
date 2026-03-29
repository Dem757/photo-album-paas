import random
from locust import HttpUser, task, between

class PhotoAlbumUser(HttpUser):
    # Szimulált várakozási idő a kérések között (1 és 5 másodperc között)
    # Ez segít realisztikusabbá tenni a terhelést
    wait_time = between(1, 5)

    def on_start(self):
        """
        Ez a metódus minden virtuális felhasználó indításakor lefut.
        Itt inicializálhatunk session-öket vagy alapvető beállításokat.
        """
        pass

    @task(10)
    def view_gallery(self):
        """
        A leggyakoribb feladat: a galéria megtekintése.
        Ez teszteli a Django nézetet és a PostgreSQL lekérdezéseket.
        """
        self.client.get("/", name="View Gallery")

    @task(5)
    def view_login_pages(self):
        """
        Bejelentkezési oldalak lekérése. 
        Ez a Django auth rendszerét és a session kezelést dolgoztatja meg.
        """
        self.client.get("/accounts/login/", name="User Login Page")
        self.client.get("/admin/login/", name="Admin Login Page")

    @task(2)
    def simulate_heavy_sorting(self):
        """
        Rendezési funkciók tesztelése.
        A különböző query paraméterek kényszerítik a Djangót az adatok újrarendezésére.
        """
        sort_options = ["name", "-uploaded_at"]
        choice = random.choice(sort_options)
        self.client.get(f"/?sort={choice}", name="Sort Gallery")

    @task(1)
    def upload_photo_page(self):
        """
        A feltöltési oldal megnyitása. 
        Ez ritkább feladat, de fontos végpont.
        """
        # Csak akkor hívjuk meg, ha be van állítva az URL
        with self.client.get("/admin/gallery/photo/add/", catch_response=True) as response:
            if response.status_code == 403:
                response.failure("Login required for upload (expected)")
            else:
                response.success()