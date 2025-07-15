from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session


def test_events_upcoming(client: TestClient):
    """Test the /events/upcoming endpoint without no parameters.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/events/upcoming' \\
      -H 'accept: application/json'
    """
    response = client.get(
        "/events/upcoming",
        headers={"accept": "application/json"}
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)


def test_events_upcoming_negative_quantity(client: TestClient):
    """Test the /events/upcoming endpoint with a negative quantity parameter.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/events/upcoming?quantity=-6' \\
      -H 'accept: application/json'
    """
    response = client.get(
        "/events/upcoming?quantity=-6",
        headers={"accept": "application/json"}
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["query", "quantity"]
    assert json_response["detail"][0]["msg"] == "Input should be greater than or equal to 0"


# Events add
def test_add_event_basic(session: Session, client: TestClient, token: str):
    """Test the /events/add endpoint with basic event data and a valid token.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: multipart/form-data' \\
      -F 'name=NASA' \\
      -F 'description=Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA' \\
      -F 'location=UDLA Park' \\
      -F 'maps_link=https://maps.app.goo.gl/a1zZZvko42gDR5ny6' \\
      -F 'capacity=250' \\
      -F 'capacity_type=site_capacity' \
    """
    files = {
        "image": ("test_image.webp", b"fake_image_content", "image/webp")
    }

    response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    json_response = response.json()
    print(json_response)

    assert response.status_code == status.HTTP_201_CREATED
    assert json_response["name"] == "NASA"
    assert json_response["location"] == "UDLA Park"
    assert json_response["capacity_type"] == "site_capacity"
    assert isinstance(json_response["id"], int)


# Events by ID
def test_find_event_by_id(session: Session, client: TestClient, token: str):
    """Test the /events/{id} endpoint to retrieve a specific event by its ID with a valid token.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/events/251' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>'
    """

    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    response = client.get(
        f"/events/{event_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["id"] == event_id
    assert json_response["name"] == "NASA"
    assert json_response["location"] == "UDLA Park"
    assert json_response["capacity_type"] == "site_capacity"


def test_find_event_by_nonexistent_id(session: Session, client: TestClient, token: str):
    """Test the /events/{id} endpoint with a non-existent event ID and a valid token.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/events/6753' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>'
    """

    response = client.get(
        "/events/6753",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


def test_find_event_by_negative_id(session: Session, client: TestClient, token: str):
    """Test the /events/{id} endpoint with a negative event ID and a valid token.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/events/-564' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>'
    """

    response = client.get(
        "/events/-564",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["path", "event_id"]
    assert json_response["detail"][0]["msg"] == "Input should be greater than 0"

# Events image


# Add dates to events
def test_add_event_dates_success(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/dates/add endpoint by adding dates successfully with a valid token.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/251/dates/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '[{"day_date":"2025-04-30","start_time":"07:20:17.219Z","end_time":"10:20:17.219Z","deleted":false}]'
    """

    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    response = client.post(
        f"/events/{event_id}/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-04-30",
                "start_time": "07:20:17.219Z",
                "end_time": "10:20:17.219Z",
                "deleted": False
            }
        ]
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response["event_dates"], list)
    assert len(json_response["event_dates"]) > 0

    first_date = json_response["event_dates"][0]
    assert first_date["day_date"] == "2025-04-30"
    assert first_date["start_time"].startswith("07:20")
    assert first_date["end_time"].startswith("10:20")
    assert first_date["deleted"] is False
    assert first_date["event_id"] == event_id


def test_add_event_dates_invalid_times(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/dates/add endpoint with invalid times (start_time == end_time).

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/765/dates/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '[{"day_date":"2025-04-30","start_time":"07:24:42.043Z","end_time":"07:24:42.043Z","deleted":false}]'
    """

    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    response = client.post(
        f"/events/{event_id}/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-04-30",
                "start_time": "07:24:42.043Z",
                "end_time": "07:24:42.043Z",
                "deleted": False
            }
        ]
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", 0]
    assert json_response["detail"][0]["msg"] == "Value error, Start time must be before end time."


def test_add_event_dates_nonexistent_event(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/dates/add endpoint with a non-existent event ID.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/765/dates/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '[{"day_date":"2025-04-30","start_time":"07:24:42.043Z","end_time":"10:24:42.043Z","deleted":false}]'
    """

    response = client.post(
        "/events/765/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-04-30",
                "start_time": "07:24:42.043Z",
                "end_time": "10:24:42.043Z",
                "deleted": False
            }
        ]
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


def test_add_event_dates_negative_id(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/dates/add endpoint with a negative event ID.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/-765/dates/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '[{"day_date":"2025-04-30","start_time":"07:24:42.043Z","end_time":"10:24:42.043Z","deleted":false}]'
    """

    response = client.post(
        "/events/-765/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-04-30",
                "start_time": "07:24:42.043Z",
                "end_time": "10:24:42.043Z",
                "deleted": False
            }
        ]
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["path", "event_id"]
    assert json_response["detail"][0]["msg"] == "Input should be greater than 0"


def test_add_multiple_event_dates_success(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/dates/add endpoint by adding multiple dates successfully with a valid token.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/251/dates/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '[{"day_date":"2025-05-01","start_time":"07:24:42.043Z","end_time":"12:24:42.043Z","deleted":false}, {"day_date":"2025-05-02","start_time":"07:00:00.000Z","end_time":"12:00:00.000Z","deleted":false}, {"day_date":"2025-05-03","start_time":"07:00:00.000Z","end_time":"12:00:00.000Z","deleted":false}]'
    """

    # Create an event first
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    # Add 3 dates to the created event
    response = client.post(
        f"/events/{event_id}/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-05-01",
                "start_time": "07:24:42.043Z",
                "end_time": "12:24:42.043Z",
                "deleted": False
            },
            {
                "day_date": "2025-05-02",
                "start_time": "07:00:00.000Z",
                "end_time": "12:00:00.000Z",
                "deleted": False
            },
            {
                "day_date": "2025-05-03",
                "start_time": "07:00:00.000Z",
                "end_time": "12:00:00.000Z",
                "deleted": False
            }
        ]
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response["event_dates"], list)
    assert len(json_response["event_dates"]) >= 3

    day_dates = [d["day_date"] for d in json_response["event_dates"]]
    assert "2025-05-01" in day_dates
    assert "2025-05-02" in day_dates
    assert "2025-05-03" in day_dates


def test_add_duplicate_event_dates(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/dates/add endpoint trying to add duplicated dates.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/251/dates/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '[{"day_date":"2025-05-01","start_time":"07:24:42.043Z","end_time":"12:24:42.043Z","deleted":false}, {"day_date":"2025-05-02","start_time":"07:00:00.000Z","end_time":"12:00:00.000Z","deleted":false}, {"day_date":"2025-05-03","start_time":"07:00:00.000Z","end_time":"12:00:00.000Z","deleted":false}]'
    """

    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    client.post(
        f"/events/{event_id}/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-05-01",
                "start_time": "07:24:42.043Z",
                "end_time": "12:24:42.043Z",
                "deleted": False
            },
            {
                "day_date": "2025-05-02",
                "start_time": "07:00:00.000Z",
                "end_time": "12:00:00.000Z",
                "deleted": False
            },
            {
                "day_date": "2025-05-03",
                "start_time": "07:00:00.000Z",
                "end_time": "12:00:00.000Z",
                "deleted": False
            }
        ]
    )

    response = client.post(
        f"/events/{event_id}/dates/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=[
            {
                "day_date": "2025-05-01",
                "start_time": "07:24:42.043Z",
                "end_time": "12:24:42.043Z",
                "deleted": False
            },
            {
                "day_date": "2025-05-02",
                "start_time": "07:00:00.000Z",
                "end_time": "12:00:00.000Z",
                "deleted": False
            },
            {
                "day_date": "2025-05-03",
                "start_time": "07:00:00.000Z",
                "end_time": "12:00:00.000Z",
                "deleted": False
            }
        ]
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"] == "In the provided dates, there are duplicates with the existing dates or among themselves."
# Si valida fechas pasadas, revisar eso

# Add date to an event


def test_add_single_event_date_success(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/date/add endpoint by adding a single date successfully with a valid token.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/251/date/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'day_date=2025-04-28&start_time=07%3A33%3A32.137Z&end_time=10%3A33%3A32.137Z&deleted=false'
    """

    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    response = client.post(
        f"/events/{event_id}/date/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "day_date": "2025-04-28",
            "start_time": "07:33:32.137Z",
            "end_time": "10:33:32.137Z",
            "deleted": "false"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert isinstance(json_response["event_dates"], list)
    assert any(date["day_date"] ==
               "2025-04-28" for date in json_response["event_dates"])


def test_add_single_event_date_duplicate(session: Session, client: TestClient, token: str):
    """Test the /events/{id}/date/add endpoint trying to add a duplicated date.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/events/251/date/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'day_date=2025-06-28&start_time=07%3A33%3A32.137Z&end_time=10%3A33%3A32.137Z&deleted=false'
    """

    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    client.post(
        f"/events/{event_id}/date/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "day_date": "2025-06-28",
            "start_time": "07:33:32.137Z",
            "end_time": "10:33:32.137Z",
            "deleted": "false"
        }
    )

    response = client.post(
        f"/events/{event_id}/date/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "day_date": "2025-06-28",
            "start_time": "07:33:32.137Z",
            "end_time": "10:33:32.137Z",
            "deleted": "false"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"] == "The provided date is a duplicate with an existing date."


# Delete an event date
def test_delete_event_date_marks_as_deleted(session: Session, client: TestClient, token: str):
    """Test the DELETE /events/date/{date_id} endpoint marks the date as deleted.

    curl -X 'DELETE' \\
      'http://127.0.0.1:8000/events/date/1011' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>'
    """

    event_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "NASA",
            "description": "Evento en el que se podra aprender sobre la NASA y todo lo que hacen, y tambien su hermandad conl la UDLA",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity",
        },
        files={
            "image": ("test.webp", b"img", "image/webp")
        }
    )

    event_id = event_response.json()["id"]
    print(event_id)

    add_date_resp = client.post(
        f"/events/{event_id}/date/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "day_date": "2025-04-30",
            "start_time": "07:20:17.000Z",
            "end_time": "10:20:17.000Z",
            "deleted": "False"
        }
    )

    date_id = None
    for date in add_date_resp.json()["event_dates"]:
        if date["day_date"] == "2025-04-30":
            date_id = date["id"]
            break

    assert date_id is not None, "Date was not created"

    delete_response = client.delete(
        f"/events/date/{date_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = delete_response.json()

    assert delete_response.status_code == status.HTTP_200_OK

    found = next(
        (d for d in json_response["event_dates"] if d["id"] == date_id), None)
    assert found is not None
    assert found["deleted"] is True


def test_delete_nonexistent_event_date(client: TestClient, token: str):
    """Test the DELETE /events/date/{date_id} endpoint with a non-existent date ID.

    curl -X 'DELETE' \\
      'http://127.0.0.1:8000/events/date/1000001' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>'
    """
    nonexistent_date_id = 1000001

    response = client.delete(
        f"/events/date/{nonexistent_date_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event date not found"


# Test upcoming events with quantity
def test_events_upcoming_with_quantity(client: TestClient):
    """Test the /events/upcoming endpoint with a positive quantity parameter.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/events/upcoming?quantity=5' \\
      -H 'accept: application/json'
    """
    response = client.get(
        "/events/upcoming?quantity=5",
        headers={"accept": "application/json"}
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)
    assert len(json_response) <= 5


# Test update event
def test_update_event_success(client: TestClient, token: str):
    """Test the PATCH /events/{event_id} endpoint to update an event successfully.

    curl -X 'PATCH' \\
      'http://127.0.0.1:8000/events/123' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>' \\
      -H 'Content-Type: application/json' \\
      -d '{"name": "Updated Event Name", "description": "Updated description"}'
    """
    # Create an event first
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "Original Event",
            "description": "Original description",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    # Update the event
    update_data = {
        "name": "Updated Event Name",
        "description": "Updated description"
    }

    response = client.patch(
        f"/events/{event_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=update_data
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["name"] == "Updated Event Name"
    assert json_response["description"] == "Updated description"
    assert json_response["id"] == event_id


def test_update_nonexistent_event(client: TestClient, token: str):
    """Test the PATCH /events/{event_id} endpoint with a non-existent event ID."""
    update_data = {
        "name": "Updated Event Name",
        "description": "Updated description"
    }

    response = client.patch(
        "/events/999999",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=update_data
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


# Test update event image
def test_update_event_image_success(client: TestClient, token: str):
    """Test the PATCH /events/{event_id}/image endpoint to update an event image successfully."""
    # Create an event first
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "Test Event",
            "description": "Test description",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]
    original_image_uuid = created_event["image_uuid"]

    # Update the image
    new_image_content = b"new_fake_image_content"
    new_files = {
        "image": ("new_test_image.webp", new_image_content, "image/webp")
    }

    response = client.patch(
        f"/events/{event_id}/image",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        files=new_files
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["id"] == event_id
    assert json_response["image_uuid"] != original_image_uuid


def test_update_image_nonexistent_event(client: TestClient, token: str):
    """Test the PATCH /events/{event_id}/image endpoint with a non-existent event ID."""
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    response = client.patch(
        "/events/999999/image",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        files=files
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


# Test get all events
def test_get_all_events(client: TestClient, token: str):
    """Test the GET /events/all endpoint to retrieve all events."""
    response = client.get(
        "/events/all",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)


# Test get my registered events
def test_get_my_registered_events_empty(client: TestClient, token: str):
    """Test the GET /events/my-registered-events endpoint when user has no registrations."""
    response = client.get(
        "/events/my-registered-events",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)


# Test get events to react
def test_get_events_to_react_empty(client: TestClient, token: str):
    """Test the GET /events/events-to-react endpoint when user has no events to react to."""
    response = client.get(
        "/events/events-to-react",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)


# Test get event image
def test_get_event_image_success(client: TestClient, token: str):
    """Test the GET /events/image/{image_uuid} endpoint to retrieve an event image."""
    # Create an event first
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "Test Event",
            "description": "Test description",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    created_event = create_response.json()
    image_uuid = created_event["image_uuid"]

    # Get the image
    response = client.get(
        f"/events/image/{image_uuid}",
        headers={"accept": "application/json"}
    )

    # The endpoint returns a FileResponse, so we check for success status
    assert response.status_code == status.HTTP_200_OK


def test_get_nonexistent_event_image(client: TestClient):
    """Test the GET /events/image/{image_uuid} endpoint with a non-existent image UUID."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/events/image/{fake_uuid}",
        headers={"accept": "application/json"}
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Image not found"


# Test delete event
def test_delete_event_success(client: TestClient, token: str):
    """Test the DELETE /events/{event_id} endpoint to delete an event successfully."""
    # Create an event first
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "Event to Delete",
            "description": "This event will be deleted",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    # Delete the event
    response = client.delete(
        f"/events/{event_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["id"] == event_id


def test_delete_nonexistent_event(client: TestClient, token: str):
    """Test the DELETE /events/{event_id} endpoint with a non-existent event ID."""
    response = client.delete(
        "/events/999999",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


# Test get event dates
def test_get_event_dates_success(client: TestClient, token: str):
    """Test the GET /events/{event_id}/dates endpoint to retrieve event dates."""
    # Create an event first
    image_content = b"fake_image_content"
    files = {
        "image": ("test_image.webp", image_content, "image/webp")
    }

    create_response = client.post(
        "/events/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        },
        data={
            "name": "Test Event",
            "description": "Test description",
            "location": "UDLA Park",
            "maps_link": "https://maps.app.goo.gl/a1zZZvko42gDR5ny6",
            "capacity": "250",
            "capacity_type": "site_capacity"
        },
        files=files
    )

    created_event = create_response.json()
    event_id = created_event["id"]

    # Add a date to the event
    client.post(
        f"/events/{event_id}/date/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "day_date": "2025-08-15",
            "start_time": "09:00:00.000Z",
            "end_time": "17:00:00.000Z",
            "deleted": "false"
        }
    )

    # Get the event dates
    response = client.get(
        f"/events/{event_id}/dates",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)
    assert len(json_response) > 0
    assert any(date["day_date"] == "2025-08-15" for date in json_response)


def test_get_dates_nonexistent_event(client: TestClient, token: str):
    """Test the GET /events/{event_id}/dates endpoint with a non-existent event ID."""
    response = client.get(
        "/events/999999/dates",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


# Events add attendance
def test_add_attendance_success(client: TestClient, token: str):
    """Test the POST /events/add/attendance/{event_date_id}/{registration_id} endpoint successfully."""
    # Note: This test would require setting up registration data
    # Since we don't have access to registration creation in this router,
    # this is a placeholder test that would need the full setup
    pass


def test_add_attendance_by_companion_success(client: TestClient, token: str):
    """Test the POST /events/add/attendance/{event_date_id}/{event_id}/{companion_id} endpoint successfully."""
    # Note: This test would require setting up companion/user registration data
    # Since we don't have access to registration creation in this router,
    # this is a placeholder test that would need the full setup
    pass


def test_add_attendance_nonexistent_event_date(client: TestClient, token: str):
    """Test adding attendance with non-existent event date ID."""
    response = client.post(
        "/events/add/attendance/999999/999999/999999",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Registration not found"
