import pytest
from app import models


@pytest.fixture
def test_vote(authorized_client, test_posts, test_user, session):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()


def test_add_vote(authorized_client, test_user, test_posts):
    data = {
        "post_id": test_posts[0].id,
        "dir": 1
    }
    res = authorized_client.post("/vote/", json=data)

    assert res.status_code == 201
    assert res.json()["message"] == "voted successfully"


def test_add_twice_vote(authorized_client, test_user, test_posts, test_vote):
    data = {
        "post_id": test_posts[3].id,
        "dir": 1
    }
    res = authorized_client.post("/vote/", json=data)

    assert res.status_code == 409
    assert res.json().get("detail") == "already voted!"


def test_remove_vote(authorized_client, test_user, test_posts, test_vote):
    data = {
        "post_id": test_posts[3].id,
        "dir": 0
    }
    res = authorized_client.post("/vote/", json=data)

    assert res.status_code == 204


def test_remove_vote_on_not_vote_post(authorized_client, test_user, test_posts, test_vote):
    data = {
        "post_id": test_posts[2].id,
        "dir": 0
    }
    res = authorized_client.post("/vote/", json=data)

    assert res.status_code == 404


def test_unauthorized_user_add_vote(client, test_posts):
    data = {
        "post_id": test_posts[0].id,
        "dir": 1
    }
    res = client.post("/vote/", json=data)

    assert res.status_code == 401


def test_add_vote_on_none_exist_post(authorized_client, test_vote, test_posts):
    data = {
        "post_id": 999999999,
        "dir": 1
    }
    res = authorized_client.post("/vote/", json=data)

    assert res.status_code == 404
    assert res.json().get("detail") == "post not found!"


def test_remove_vote_on_none_exist_post(authorized_client, test_vote, test_posts):
    data = {
        "post_id": 999999999,
        "dir": 0
    }
    res = authorized_client.post("/vote/", json=data)

    assert res.status_code == 404
    assert res.json().get("detail") == "post not found!"
