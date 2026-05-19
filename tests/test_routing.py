def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (301, 302, 307, 308)
    assert response.headers["location"] == "/static/index.html"
