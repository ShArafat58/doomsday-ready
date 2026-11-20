import pytest
def movie_ids(client) -> dict[str, int]:
    return {m["title"]: m["id"] for m in client.get("/api/movies").json()}
def cinema_ids(client) -> dict[str, int]:
    return {c["name"]: c["id"] for c in client.get("/api/cinemas").json()}
def rewatch(client, title: str) -> dict:
    response = client.get(f"/api/movies/{movie_ids(client)[title]}/rewatch-order")
    assert response.status_code == 200
    return response.json()
# Rewatch order (task examples)
def test_rewatch_order_for_doomsday(client):
    plan = rewatch(client, "Avengers: Doomsday")
    titles = [m["title"] for m in plan["movies"]]
    position = {m["id"]: i for i, m in enumerate(plan["movies"])}
    assert len(titles) == 7
    assert len(set(titles)) == 7
    assert "Avengers: Doomsday" not in titles
    for movie in plan["movies"]:
        for prerequisite_id in movie["prerequisiteIds"]:
            assert position[prerequisite_id] < position[movie["id"]]
    assert plan["watchedCount"] == 0
    assert plan["unwatchedRuntimeMinutes"] == 1000
def test_rewatch_order_for_civil_war(client):
    titles = [m["title"] for m in rewatch(client, "Captain America: Civil War")["movies"]]
    assert set(titles[:2]) == {"Iron Man", "Captain America: The First Avenger"}
    assert titles[2:] == ["The Avengers"]
def test_rewatch_order_for_ragnarok_is_empty(client):
    plan = rewatch(client, "Thor: Ragnarok")
    assert plan["movies"] == []
    assert plan["unwatchedRuntimeMinutes"] == 0
def test_watched_movies_update_progress(client):
    ids = movie_ids(client)
    client.patch(f"/api/movies/{ids['Iron Man']}", json={"watched": True})
    client.patch(f"/api/movies/{ids['The Avengers']}", json={"watched": True})
    plan = rewatch(client, "Avengers: Doomsday")
    assert plan["watchedCount"] == 2
    assert plan["unwatchedRuntimeMinutes"] == 1000 - 126 - 143
def test_rewatch_order_for_unknown_movie_returns_404(client):
    assert client.get("/api/movies/99999/rewatch-order").status_code == 404
# Circular dependency (task example)
def test_endgame_as_prerequisite_of_iron_man_returns_409(client):
    ids = movie_ids(client)
    response = client.patch(
        f"/api/movies/{ids['Iron Man']}", json={"prerequisiteIds": [ids["Avengers: Endgame"]]}
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CIRCULAR_DEPENDENCY"
    assert client.get(f"/api/movies/{ids['Iron Man']}").json()["prerequisiteIds"] == []
def test_movie_cannot_be_its_own_prerequisite(client):
    ids = movie_ids(client)
    response = client.patch(f"/api/movies/{ids['Iron Man']}", json={"prerequisiteIds": [ids["Iron Man"]]})
    assert response.status_code == 409
# Movie validation
def test_create_movie_returns_201(client):
    response = client.post("/api/movies", json={"title": "Thor", "releaseYear": 2011, "runtimeMinutes": 115})
    assert response.status_code == 201
    assert response.json()["watched"] is False
@pytest.mark.parametrize(
    "body, status, code",
    [
        ({"title": "New", "releaseYear": 2020, "runtimeMinutes": 0}, 422, "VALIDATION_ERROR"),
        ({"title": "New", "releaseYear": 2020, "runtimeMinutes": 301}, 422, "VALIDATION_ERROR"),
        ({"title": "iron man", "releaseYear": 2020, "runtimeMinutes": 100}, 409, "TITLE_TAKEN"),
        (
            {"title": "New", "releaseYear": 2020, "runtimeMinutes": 100, "prerequisiteIds": [99999]},
            422,
            "PREREQUISITE_NOT_FOUND",
        ),
    ],
)
def test_create_movie_rejects_bad_input(client, body, status, code):
    response = client.post("/api/movies", json=body)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
def test_update_unknown_movie_returns_404(client):
    assert client.patch("/api/movies/99999", json={"watched": True}).status_code == 404
# Booking (task examples)
@pytest.mark.parametrize(
    "name, group_size, total, bundles",
    [
        ("Starlight Cinema", 6, 2, [{"size": 3, "count": 2}]),
        ("Nebula Screens", 11, 4, [{"size": 5, "count": 1}, {"size": 2, "count": 3}]),
        (
            "Quantum Theatre",
            44,
            4,
            [{"size": 20, "count": 1}, {"size": 9, "count": 2}, {"size": 6, "count": 1}],
        ),
    ],
)
def test_booking_task_examples(client, name, group_size, total, bundles):
    cinema_id = cinema_ids(client)[name]
    response = client.get(f"/api/cinemas/{cinema_id}/booking", params={"groupSize": group_size})
    body = response.json()
    assert response.status_code == 200
    assert body["possible"] is True
    assert body["totalBundles"] == total
    assert body["bundles"] == bundles
def test_booking_not_possible(client):
    cinema_id = cinema_ids(client)["Orbit Hall"]
    body = client.get(f"/api/cinemas/{cinema_id}/booking", params={"groupSize": 7}).json()
    assert body["possible"] is False
    assert body["bundles"] == []
# Cinema validation
@pytest.mark.parametrize(
    "body, status",
    [
        ({"name": "New", "bundleSizes": [2, 2]}, 422),
        ({"name": "New", "bundleSizes": list(range(1, 12))}, 422),
        ({"name": "New", "bundleSizes": [0]}, 422),
        ({"name": "New", "bundleSizes": [501]}, 422),
        ({"name": "New", "bundleSizes": []}, 422),
        ({"name": "starlight cinema", "bundleSizes": [2]}, 409),
    ],
)
def test_create_cinema_rejects_bad_input(client, body, status):
    assert client.post("/api/cinemas", json=body).status_code == status
@pytest.mark.parametrize("group_size", [0, 10001])
def test_booking_rejects_group_size_out_of_range(client, group_size):
    cinema_id = cinema_ids(client)["Quantum Theatre"]
    response = client.get(f"/api/cinemas/{cinema_id}/booking", params={"groupSize": group_size})
    assert response.status_code == 422
def test_booking_for_unknown_cinema_returns_404(client):
    assert client.get("/api/cinemas/99999/booking", params={"groupSize": 5}).status_code == 404
