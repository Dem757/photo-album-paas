import os
import random
import re
import time
from locust import HttpUser, task, between

class PhotoAlbumUser(HttpUser):
    # Szimulált várakozási idő a kérések között (1 és 5 másodperc között)
    # Ez segít realisztikusabbá tenni a terhelést
    wait_time = between(1, 5)

    @staticmethod
    def _extract_csrf_token(html_text):
        """Extract csrfmiddlewaretoken value from Django form HTML."""
        if not html_text:
            return None
        match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', html_text)
        return match.group(1) if match else None

    @staticmethod
    def _tiny_png_bytes():
        """Return a valid 1x1 PNG payload for upload tests."""
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
            b"\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02"
            b"\xfeA\x89\x91\xb9\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    def on_start(self):
        """
        Ez a metódus minden virtuális felhasználó indításakor lefut.
        Itt inicializálhatunk session-öket vagy alapvető beállításokat.
        """
        timestamp = int(time.time() * 1000)
        self.username = os.getenv("LOCUST_USERNAME") or f"locust_{timestamp}_{random.randint(1000, 9999)}"
        self.password = os.getenv("LOCUST_PASSWORD") or "LocustPass123!"

        # If no explicit credentials are provided, create a user via registration.
        if not os.getenv("LOCUST_USERNAME"):
            register_page = self.client.get("/register/", name="Register Page")
            register_csrf = self._extract_csrf_token(register_page.text)
            if register_csrf:
                self.client.post(
                    "/register/",
                    data={
                        "username": self.username,
                        "email": f"{self.username}@example.com",
                        "password1": self.password,
                        "password2": self.password,
                        "csrfmiddlewaretoken": register_csrf,
                    },
                    headers={"Referer": "/register/"},
                    name="User Register",
                    allow_redirects=False,
                )

        # Log in and keep the authenticated session for subsequent tasks.
        login_page = self.client.get("/accounts/login/", name="User Login Page")
        login_csrf = self._extract_csrf_token(login_page.text)
        if login_csrf:
            self.client.post(
                "/accounts/login/",
                data={
                    "username": self.username,
                    "password": self.password,
                    "csrfmiddlewaretoken": login_csrf,
                },
                headers={"Referer": "/accounts/login/"},
                name="User Login",
                allow_redirects=False,
            )

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
    def upload_photo(self):
        """
        Bejelentkezett felhasználóként képfeltöltés szimulálása.
        """
        with self.client.get("/upload/", name="Upload Page", catch_response=True) as page:
            if page.status_code != 200:
                page.failure(f"Upload page unavailable: {page.status_code}")
                return

            upload_csrf = self._extract_csrf_token(page.text)
            if not upload_csrf:
                page.failure("Missing CSRF token on upload page")
                return

        with self.client.post(
            "/upload/",
            data={
                "name": f"locust-photo-{random.randint(1000, 9999)}",
                "csrfmiddlewaretoken": upload_csrf,
            },
            files={"image": ("locust-test.png", self._tiny_png_bytes(), "image/png")},
            headers={"Referer": "/upload/"},
            name="Upload Photo",
            allow_redirects=False,
            catch_response=True,
        ) as response:
            if response.status_code not in (302, 200):
                response.failure(f"Upload failed: {response.status_code}")
            else:
                response.success()