from app import schemas
from .utils import verify_access_token
import pytest


class TestUser():
    def test_root(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json().get("message") == "Welcome to my API!"

    def test_create_user(self, client):
        res = client.post(
            "/users/", json={"email": "test_client3@gmail.com", "password": "password123"})

        new_user = schemas.UserOut(**res.json())
        assert res.status_code == 201
        assert new_user.email == "test_client3@gmail.com"

    def test_user_login(self, client, test_user):
        res = client.post(
            "/login", data={"username": test_user["email"], "password": test_user["password"]})
        res_data = res.json()

        # get user_id from access_token
        id = verify_access_token(res_data["access_token"])

        assert res.status_code == 200
        assert res_data["token_type"] == "bearer"
        # asset user_id is matching
        assert test_user["id"] == id

    @pytest.mark.parametrize("email, password, status_code",
                             [("test_client3@gmail.com", "wrong password", 403),
                              ("test3@gmail.com", "password123", 403),
                              ("test3@gmail.com", None, 422)]
                             )
    def test_invalid_login(self, client, email, password, status_code):
        res = client.post(
            "/login", data={"username": email, "password": password})

        assert res.status_code == status_code
        # assert res.json().get("detail") == "Invalid cretidentials!"
