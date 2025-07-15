import json
from pathlib import Path
from uuid import uuid4

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient


def generate_assistant_email(faker: Faker) -> str:
    """Generate a valid email for assistant role (must be from allowed domains)."""
    allowed_domains = ["@gmail.com", "@hotmail.com", "@outlook.com", "@protonmail.com", "@yahoo.com"]
    username = faker.user_name()
    domain = faker.random_element(allowed_domains)
    return f"{username}{domain}"



def test_add_assistant_invalid_id_number(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint with an invalid Ecuadorian ID number.

    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -F 'id_number=1701698834' ...
    """

    id_number_type = "cedula"
    id_number = "1234567890"

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": faker.email(),
    }

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )

    json_response = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["msg"] == "Value error, Invalid Ecuadorian ID number"


def test_add_assistant_without_accepting_terms(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint when terms and conditions are not accepted.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/assistant/add' \\
      -F 'accepted_terms=false' ...
    """

    response = client.post(
        "/assistant/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"},
        data={
            "gender": "female",
            "date_of_birth": "1997-09-19",
            "id_number_type": "cedula",
            "id_number": "1709690034",
            "phone": "0999999999",
            "accepted_terms": "false",
            "last_name": "Mebarak",
            "first_name": "Shakira",
            "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
            "email": "alphawolf@gmail.com"
        },
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", "accepted_terms"]
    assert json_response["detail"][0]["msg"] == "Value error, You must accept the terms and conditions."


def test_add_assistant_with_future_birthdate(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint with a future date of birth.

    curl -X 'POST' \\
      'http://127.0.0.1:8000/assistant/add' \\
      -F 'date_of_birth=2025-09-19' ...
    """

    response = client.post(
        "/assistant/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"},

        data={
            "gender": "female",
            "date_of_birth": "2025-09-19",
            "id_number_type": "cedula",
            "id_number": "1709690034",
            "phone": "0999999999",
            "accepted_terms": "true",
            "last_name": "Mebarak",
            "first_name": "Shakira",
            "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
            "email": "alphawolf@gmail.com"
        },
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", "date_of_birth"]
    assert json_response["detail"][0]["msg"] == "Value error, Date must be before today."



def test_get_assistant_by_id_number_not_found(client: TestClient, token: str, faker: Faker):
    """Test the GET /assistant/get-by-id-number/{id_number} endpoint with a non-existing ID.

    curl -X 'GET' \\
      'http://127.0.0.1:8000/assistant/get-by-id-number/1726754301' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <token>'
    """
    response = client.get(
        f"/assistant/get-by-id-number/{faker.random_int(min=1000000000, max=9999999999)}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Assistant not found"


def test_add_assistant_success(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test the POST /assistant/add endpoint with valid data.

    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -F 'id_number=1701698834' ...
    """

    id_number_type = "cedula"
    id_number = faker.ecuadorian_id_number()

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": generate_assistant_email(faker),
    }

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )

    json_response = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert json_response["email"] == person["email"]
    assert json_response["first_name"] == person["first_name"]
    assert json_response["last_name"] == person["last_name"]
    assert "id" in json_response


def test_add_assistant_duplicate_person(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test the POST /assistant/add endpoint with the same person (same face).
    
    This test verifies that the face recognition system prevents the same person
    from registering multiple times, even with different email addresses.
    
    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -F 'email=existing@example.com' ...
    """
    id_number_type = "cedula"
    id_number = faker.ecuadorian_id_number()
    email = generate_assistant_email(faker)

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": email,
    }

    # First registration should succeed
    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )    # Debug the first registration attempt
    if response.status_code != status.HTTP_201_CREATED:
        print(f"First registration failed with status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    assert response.status_code == status.HTTP_201_CREATED

    # Second registration with same face (but different email and ID) should fail
    person["id_number"] = faker.ecuadorian_id_number()  # Change ID to avoid ID conflict
    person["email"] = generate_assistant_email(faker)  # Change email too

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )

    json_response = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"] == "The person already exists in the database. Please enter a different person."


def test_add_assistant_invalid_phone_number(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint with an invalid phone number.
    
    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -F 'phone=123' ...
    """
    id_number_type = "cedula"
    id_number = faker.ecuadorian_id_number()

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": "123",  # Invalid phone number
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": faker.email(),
    }

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_assistant_missing_image(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint without an image.
    
    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -d '{"first_name": "John"}' ...
    """
    id_number_type = "cedula"
    id_number = faker.ecuadorian_id_number()

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": faker.email(),
    }

    response = client.post(
        "/assistant/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"},
        data=person
        # No files parameter - missing image
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_assistant_info_success(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test the GET /assistant/info endpoint with valid authentication.

    curl -X 'GET' \\
        'http://127.0.0.1:8000/assistant/info' \\
        -H 'Authorization: Bearer <token>'
    """
    # First create an assistant
    id_number = faker.ecuadorian_id_number()
    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": "cedula",
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": generate_assistant_email(faker),
    }

    # Create assistant
    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {"image": ("person.jpeg", image_file, "image/jpeg")}
        create_response = client.post(
            "/assistant/add",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            data=person,
            files=files
        )
    
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Get assistant token
    assistant_token = client.post(
        "/token",
        data={
            "grant_type": "password",
            "username": person["email"],
            "password": person["password"],
            "scope": "assistant",
            "client_id": "",
            "client_secret": ""
        }
    ).json()["access_token"]

    # Test get assistant info
    response = client.get(
        "/assistant/info",
        headers={
            "Authorization": f"Bearer {assistant_token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert json_response["email"] == person["email"]
    assert json_response["first_name"] == person["first_name"]


def test_get_assistant_info_unauthorized(client: TestClient):
    """Test the GET /assistant/info endpoint without authentication.

    curl -X 'GET' \\
        'http://127.0.0.1:8000/assistant/info'
    """
    response = client.get(
        "/assistant/info",
        headers={"accept": "application/json"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_assistant_by_id_number_success(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test the GET /assistant/get-by-id-number/{id_number} endpoint with existing ID.

    curl -X 'GET' \\
        'http://127.0.0.1:8000/assistant/get-by-id-number/1726754301' \\
        -H 'accept: application/json' \\
        -H 'Authorization: Bearer <token>'
    """
    # First create an assistant
    id_number = faker.ecuadorian_id_number()
    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": "cedula",
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": generate_assistant_email(faker),
    }

    # Create assistant
    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {"image": ("person.jpeg", image_file, "image/jpeg")}
        create_response = client.post(
            "/assistant/add",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            data=person,
            files=files
        )
    
    assert create_response.status_code == status.HTTP_201_CREATED

    # Now test getting by ID number
    response = client.get(
        f"/assistant/get-by-id-number/{id_number}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert json_response["assistant"]["id_number"] == id_number
    assert json_response["email"] == person["email"]


def test_add_assistant_invalid_email_format(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint with invalid email format.
    
    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -F 'email=invalid-email' ...
    """
    id_number_type = "cedula"
    id_number = faker.ecuadorian_id_number()

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "email": "invalid-email",  # Invalid email format
    }

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_assistant_weak_password(client: TestClient, token: str, faker: Faker):
    """Test the POST /assistant/add endpoint with weak password.
    
    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/add' \\
        -F 'password=123' ...
    """
    id_number_type = "cedula"
    id_number = faker.ecuadorian_id_number()

    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": id_number_type,
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": "123",  # Weak password
        "email": faker.email(),
    }

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {
            "image": ("person.jpeg", image_file, "image/jpeg")
        }

        response = client.post(
            "/assistant/add",
            headers={
                "Authorization": f"Bearer {token}",
                "accept": "application/json"},
            data=person,
            files=files
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_assistant_register_to_event_success(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test assistant registration to an event.

    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/register-to-event/1' \\
        -H 'Authorization: Bearer <token>'
    """
    # First create an assistant
    id_number = faker.ecuadorian_id_number()
    password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": "cedula",
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": password,
        "email": generate_assistant_email(faker),
    }

    # Create assistant
    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {"image": ("person.jpeg", image_file, "image/jpeg")}
        create_response = client.post(
            "/assistant/add",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            data=person,
            files=files
        )
    
    assert create_response.status_code == status.HTTP_201_CREATED

    # Create an event first
    event_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "location": faker.address(),
        "maps_link": "https://maps.app.goo.gl/testlocation",
        "capacity": 100,
        "capacity_type": "limit_of_spaces",
    }

    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        event_files = {"image": ("event.jpeg", image_file, "image/jpeg")}
        event_response = client.post(
            "/events/add",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            data=event_data,
            files=event_files
        )
    
    assert event_response.status_code == status.HTTP_201_CREATED
    event_id = event_response.json()["id"]

    # Get assistant token
    assistant_token = client.post(
        "/token",
        data={
            "grant_type": "password",
            "username": person["email"],
            "password": password,
            "scope": "assistant",
            "client_id": "",
            "client_secret": ""
        }
    ).json()["access_token"]

    # Register assistant to event
    response = client.post(
        f"/assistant/register-to-event/{event_id}",
        headers={
            "Authorization": f"Bearer {assistant_token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert json_response["event_id"] == event_id


def test_assistant_register_to_nonexistent_event(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test assistant registration to a non-existent event.

    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/register-to-event/9999' \\
        -H 'Authorization: Bearer <token>'
    """
    # First create an assistant
    id_number = faker.ecuadorian_id_number()
    password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": "cedula",
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": password,
        "email": generate_assistant_email(faker),
    }

    # Create assistant
    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {"image": ("person.jpeg", image_file, "image/jpeg")}
        create_response = client.post(
            "/assistant/add",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            data=person,
            files=files
        )
    
    assert create_response.status_code == status.HTTP_201_CREATED

    # Get assistant token
    assistant_token = client.post(
        "/token",
        data={
            "grant_type": "password",
            "username": person["email"],
            "password": password,
            "scope": "assistant",
            "client_id": "",
            "client_secret": ""
        }
    ).json()["access_token"]

    # Try to register to non-existent event
    response = client.post(
        "/assistant/register-to-event/9999",
        headers={
            "Authorization": f"Bearer {assistant_token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Event not found"


def test_assistant_get_registered_events(client: TestClient, token: str, faker: Faker, clean_face_db):
    """Test getting registered events for an assistant.

    curl -X 'GET' \\
        'http://127.0.0.1:8000/assistant/get-registered-events' \\
        -H 'Authorization: Bearer <token>'
    """
    # First create an assistant
    id_number = faker.ecuadorian_id_number()
    password = faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    person = {
        "gender": faker.random_element(elements=["female", "male", "other"]),
        "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d"),
        "id_number_type": "cedula",
        "id_number": id_number,
        "phone": str(faker.random_int(min=1000000000, max=9999999999)),
        "accepted_terms": "true",
        "last_name": faker.last_name(),
        "first_name": faker.first_name(),
        "password": password,
        "email": generate_assistant_email(faker),
    }

    # Create assistant
    with open("tests/imgs/foto_carne.jpg", "rb") as image_file:
        files = {"image": ("person.jpeg", image_file, "image/jpeg")}
        create_response = client.post(
            "/assistant/add",
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            data=person,
            files=files
        )
    
    assert create_response.status_code == status.HTTP_201_CREATED

    # Get assistant token
    assistant_token = client.post(
        "/token",
        data={
            "grant_type": "password",
            "username": person["email"],
            "password": password,
            "scope": "assistant",
            "client_id": "",
            "client_secret": ""
        }
    ).json()["access_token"]

    # Test getting registered events (should be empty initially)
    response = client.get(
        "/assistant/get-registered-events",
        headers={
            "Authorization": f"Bearer {assistant_token}",
            "accept": "application/json"
        }
    )

    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(json_response, list)
    assert len(json_response) == 0  # No events registered initially


def test_assistant_unauthorized_access(client: TestClient):
    """Test accessing assistant endpoints without authentication.

    curl -X 'GET' \\
        'http://127.0.0.1:8000/assistant/get-registered-events'
    """
    response = client.get(
        "/assistant/get-registered-events",
        headers={"accept": "application/json"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_assistant_register_to_event_without_auth(client: TestClient):
    """Test registering to an event without authentication.

    curl -X 'POST' \\
        'http://127.0.0.1:8000/assistant/register-to-event/1'
    """
    response = client.post(
        "/assistant/register-to-event/1",
        headers={"accept": "application/json"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

