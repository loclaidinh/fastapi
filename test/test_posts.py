from app import schemas
import pytest


class TestPost():

    def test_get_all_posts(self, authorized_client, test_posts):
        res = authorized_client.get("/posts/")

        assert res.status_code == 200
        assert len(res.json()) == len(test_posts)

    def test_unauthorized_user_get_all_posts(self, client):
        res = client.get("/posts/")

        assert res.status_code == 401

    def test_get_single_post(self, authorized_client, test_posts):
        res = authorized_client.get(f"/posts/{test_posts[0].id}")
        post = schemas.PostOut(**res.json())

        assert res.status_code == 200
        assert post.Post.id == test_posts[0].id
        assert post.Post.title == test_posts[0].title
        assert post.Post.content == test_posts[0].content

    def test_unauthorized_user_get_one_posts(self, client, test_posts):
        res = client.get(f"/posts/{test_posts[0].id}")

        assert res.status_code == 401

    def test_get_post_does_exit(self, authorized_client, test_posts):
        res = authorized_client.get("/posts/99999")

        assert res.status_code == 404

    @pytest.mark.parametrize("title, content, published", [
        ("Five thing to do in NY", "The first thing to do is", True),
        ("The 2nd thing to do in the morning", "You have to drink water", False),
        ("Thrid place in the world", "what is it about?", True)
    ])
    def test_create_new_post(self, authorized_client, test_user, title, content, published):
        res = authorized_client.post(
            "/posts/", json={"title": title, "content": content, "published": published})

        new_post = schemas.PostRespond(**res.json())

        assert res.status_code == 201
        assert new_post.title == title
        assert new_post.content == content
        assert new_post.published == published
        assert new_post.owner.id == test_user["id"]

    def test_unauthorized_user_create_new_post(self, client):
        res = client.post(
            "/posts/", json={"title": "create by annonymous", "content": "nothing", "published": True})

        assert res.status_code == 401

    def test_create_new_post_default_published_true(self, authorized_client, test_user):
        res = authorized_client.post(
            "/posts/", json={"title": "test title", "content": "default publish should be True"})

        new_post = schemas.PostRespond(**res.json())

        assert res.status_code == 201
        assert new_post.title == "test title"
        assert new_post.content == "default publish should be True"
        assert new_post.published == True
        assert new_post.owner.id == test_user["id"]

    def test_unauthorized_user_delete_post(self, client, test_user, test_posts):
        res = client.delete(f"/posts/{test_posts[0].id}")

        assert res.status_code == 401

    def test_delete_post_success(self, authorized_client, test_user, test_posts):
        res = authorized_client.delete(f"/posts/{test_posts[0].id}")

        assert res.status_code == 204

    def test_delete_none_exist_post(self, authorized_client, test_user, test_posts):
        res = authorized_client.delete("/posts/999999")

        assert res.status_code == 404

    def test_delete_post_of_other_user(self, authorized_client, test_user, test_posts):
        res = authorized_client.delete(f"/posts/{test_posts[3].id}")

        assert res.status_code == 403

    def test_update_post(self, authorized_client, test_user, test_posts):
        data = {
            "title": "updated title",
            "content": "updated content",
            "id": test_posts[0].id
        }

        res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
        post_update = schemas.PostRespond(**res.json())

        assert res.status_code == 200
        assert post_update.title == data["title"]
        assert post_update.content == data["content"]
        assert post_update.id == data["id"]
        assert post_update.user_id == test_user["id"]

    def test_update_post_of_other_user(self, authorized_client, test_user, test_posts):
        data = {
            "title": "updated title",
            "content": "updated content",
            "id": test_posts[3].id
        }

        res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)

        assert res.status_code == 403
        assert test_posts[3].title != "updated title"
        assert test_posts[3].content != "updated content"
        assert test_posts[3].user_id != test_user["id"]

    def test_unauthorized_user_update_post(self, client, test_user, test_posts):
        data = {
            "title": "updated title",
            "content": "updated content",
            "id": test_posts[0].id
        }
        res = client.put(f"/posts/{test_posts[0].id}")

        assert res.status_code == 401

    def test_update_none_exist_post(self, authorized_client, test_user, test_posts):
        data = {
            "title": "updated title",
            "content": "updated content",
            "id": test_posts[0].id
        }

        res = authorized_client.put("/posts/9999999", json=data)

        assert res.status_code == 404
