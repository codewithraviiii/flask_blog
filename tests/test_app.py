import pytest
from app import create_app, db
from app.models import User, Post
from config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, u="alice", e="a@x.com", p="secret1"):
    return client.post("/auth/register", data=dict(username=u, email=e, password=p, password2=p), follow_redirects=True)


def login(client, u="alice", p="secret1"):
    return client.post("/auth/login", data=dict(username=u, password=p), follow_redirects=True)


def test_register_login_logout(client):
    assert b"Registration successful" in register(client).data
    assert b"alice" in login(client).data
    assert b"Login" in client.get("/auth/logout", follow_redirects=True).data


def test_bad_login(client):
    register(client)
    assert b"Invalid username" in login(client, p="wrong").data


def test_post_crud(client):
    register(client); login(client)
    r = client.post("/posts/new", data=dict(title="Hello", body="World body", tags="flask, python"), follow_redirects=True)
    assert b"Post created" in r.data and b"#flask" in r.data
    assert b"Post updated" in client.post("/posts/1/edit", data=dict(title="Hi2", body="b", tags="x"), follow_redirects=True).data
    assert b"Post deleted" in client.post("/posts/1/delete", follow_redirects=True).data
    assert Post.query.count() == 0


def test_only_author_can_delete(client):
    register(client); login(client)
    client.post("/posts/new", data=dict(title="T", body="B", tags=""))
    client.get("/auth/logout")
    register(client, "bob", "b@x.com"); login(client, "bob")
    assert client.post("/posts/1/delete").status_code == 403


def test_comments_need_login(client):
    register(client); login(client)
    client.post("/posts/new", data=dict(title="T", body="B", tags=""))
    assert b"Nice post" in client.post("/posts/1", data=dict(body="Nice post"), follow_redirects=True).data
    client.get("/auth/logout")
    r = client.post("/posts/1", data=dict(body="anon"), follow_redirects=True)
    assert b"anon" not in r.data


def test_search_filter_pagination(client):
    register(client); login(client)
    for i in range(7):
        client.post("/posts/new", data=dict(title=f"Post {i}", body="content", tags="even" if i % 2 == 0 else "odd"))
    client.post("/posts/new", data=dict(title="Needle", body="special", tags="odd"))
    assert b"Needle" in client.get("/?q=needle").data
    assert b"Post 1" not in client.get("/?q=needle").data
    assert b"Post 2" in client.get("/?tag=even").data
    assert b"Older" in client.get("/").data
    assert client.get("/?page=2").status_code == 200


def test_profile(client):
    register(client)
    assert client.get("/user/alice").status_code == 200
    assert client.get("/user/nobody").status_code == 404
