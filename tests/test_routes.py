from http import client


def test_plan_trip_route():
    response = client.post("/plan-trip", json={
        "destination": "Rome",
        "start_date": "2025-07-01",
        "end_date": "2025-07-05",
        "interests": ["museums", "food"],
        "budget": 1500
    })
    assert response.status_code == 200