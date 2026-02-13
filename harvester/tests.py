from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class JWTWorksAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        self.username = "testuser"
        self.password = "testpass12345"

        # создаём пользователя в ТЕСТОВОЙ базе (она отдельная, не твоя sqlite)
        User.objects.create_user(username=self.username, password=self.password)

    def test_works_requires_auth(self):
        # Без токена должно быть 401
        resp = self.client.get("/api/works/")
        self.assertEqual(resp.status_code, 401)

    def test_token_obtain_returns_access(self):
        # Получаем токен
        resp = self.client.post(
            "/api/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_works_with_token_is_ok(self):
        # Берём access
        token_resp = self.client.post(
            "/api/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        access = token_resp.data["access"]

        # Добавляем заголовок Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = self.client.get("/api/works/")
        self.assertEqual(resp.status_code, 200)
