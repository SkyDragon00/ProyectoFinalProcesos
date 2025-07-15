from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db.database import User
from app.models.Role import Role
from app.security.security import get_password_hash


def test_add_staff(session: Session, client: TestClient, faker: Faker):
    """Test the staff add endpoint with valid token.

    The curl command to test this endpoint is:
    curl -X 'POST' \\
      'http://127.0.0.1:8000/staff/add' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB1ZGxhLmVkdS5lYyIsInNjb3BlcyI6WyJvcmdhbml6ZXIiXSwiZXhwIjoxNzQ0OTM0OTUwfQ.iEvVW1-lu1SZCmizTcvP-VRaTw8NUw9uuYLlKsYKfJc' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'email=BobEsponja%40udla.edu.ec&first_name=Bob&last_name=Esponja&password=Dinero666%40'
  """
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    response = client.post(
        "/staff/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "email": "Patricio@udla.edu.ec",
            "first_name": "Patricio",
            "last_name": "Estrella",
            "password": faker.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert json_response["email"] == "Patricio@udla.edu.ec"
    assert json_response["first_name"] == "Patricio"
    assert json_response["last_name"] == "Estrella"
    assert json_response["role"] == "staff"


def test_add_repeated_staff_email(session: Session, client: TestClient, faker: Faker):
    """Test the staff add endpoint with valid token.

    The curl command to test this endpoint is:
    curl -X 'POST' \\
  'http://127.0.0.1:8000/staff/add' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB1ZGxhLmVkdS5lYyIsInNjb3BlcyI6WyJvcmdhbml6ZXIiXSwiZXhwIjoxNzQ1Mjg1OTM5fQ.l8XXCfcEBdFCYb2yGCLjR8f8bicXDY2dmoNzXdwD0B0' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'email=Patricio%40udla.edu.ec&first_name=12345678&last_name=Estrella&password=Dinero555%40'
  """
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response1 = client.post(
        "/staff/add",
        headers=headers,
        data={
            "email": "Patricio@udla.edu.ec",
            "first_name": "Patricio",
            "last_name": "Estrella",
            "password": faker.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        }
    )

    json_response = response1.json()

    assert response1.status_code == status.HTTP_201_CREATED
    assert json_response["email"] == "Patricio@udla.edu.ec"
    assert json_response["first_name"] == "Patricio"
    assert json_response["last_name"] == "Estrella"
    assert json_response["role"] == "staff"

    response2 = client.post(
        "/staff/add",
        headers=headers,
        data={
            "email": "Patricio@udla.edu.ec",
            "first_name": "Team",
            "last_name": "Rocket",
            "password": faker.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        }
    )

    json_response = response2.json()

    assert response2.status_code == status.HTTP_409_CONFLICT
    assert json_response["detail"] == "User with this email already exists"


def test_add_staff_wrong_password(session: Session, client: TestClient):
    """Test the staff add endpoint with valid token.

    The curl command to test this endpoint is:
    curl -X 'POST' \\
  'http://127.0.0.1:8000/staff/add' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB1ZGxhLmVkdS5lYyIsInNjb3BlcyI6WyJvcmdhbml6ZXIiXSwiZXhwIjoxNzQ1MTgwNzYwfQ.SqmQmCb9LwVHbnbzdMU-Pt-dkyKJFezlaxBVIygNyDo' \
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'email=Patricio%40udla.edu.ec&first_name=Patricio&last_name=Estrella&password=6666666'
  """
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    response = client.post(
        "/staff/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "email": "Patricio@udla.edu.ec",
            "first_name": "Patricio",
            "last_name": "Estrella",
            "password": "6666666"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", "password"]
    assert json_response["detail"][0]["msg"] == "Value error, Password must have at least 9 characters, 1 lowercase letters, 1 uppercase letters, 1 digit, and 1 special character."


def test_add_staff_wrong_email(session: Session, client: TestClient):
    """Test the staff add endpoint with valid token.

    The curl command to test this endpoint is:
    curl -X 'POST' \\
  'http://127.0.0.1:8000/staff/add' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB1ZGxhLmVkdS5lYyIsInNjb3BlcyI6WyJvcmdhbml6ZXIiXSwiZXhwIjoxNzQ1Mjg1OTM5fQ.l8XXCfcEBdFCYb2yGCLjR8f8bicXDY2dmoNzXdwD0B0' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'email=Patriciodelocos&first_name=Patricio&last_name=Estrella&password=Dinero555%40'
  """
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    response = client.post(
        "/staff/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "email": "Patriciodelocos",
            "first_name": "Patricio",
            "last_name": "Estrella",
            "password": "Dinero555@"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", "email"]
    assert json_response["detail"][0]["msg"] == "value is not a valid email address: An email address must have an @-sign."


def test_add_staff_wrong_first_name(session: Session, client: TestClient):
    """Test the staff add endpoint with valid token.

    curl -X 'POST' \\
    'http://127.0.0.1:8000/staff/add' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB1ZGxhLmVkdS5lYyIsInNjb3BlcyI6WyJvcmdhbml6ZXIiXSwiZXhwIjoxNzQ1MzY5MzYzfQ.n7tn03hrkN3MiID9G6W7gCbD8xQxFfx1ARP8pZp6-tU' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'email=Patricio%40udla.edu.ec&first_name=777777&last_name=Estrella&password=Dinero555%40'
  """
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    response = client.post(
        "/staff/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "email": "Patricio@udla.edu.ec",
            "first_name": "777777",
            "last_name": "Estrella",
            "password": "Dinero555@"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", "first_name"]
    assert json_response["detail"][0]["msg"] == "Value error, Name cannot consist of only numbers."


def test_add_staff_wrong_last_name(session: Session, client: TestClient):
    """Test the staff add endpoint with valid token.

    curl -X 'POST' \\
    'http://127.0.0.1:8000/staff/add' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB1ZGxhLmVkdS5lYyIsInNjb3BlcyI6WyJvcmdhbml6ZXIiXSwiZXhwIjoxNzQ1MzY5MzYzfQ.n7tn03hrkN3MiID9G6W7gCbD8xQxFfx1ARP8pZp6-tU' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'email=Patricio%40udla.edu.ec&first_name=Patricio&last_name=d8372846%23&password=Dinero555%40'
  """
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    response = client.post(
        "/staff/add",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "email": "Patricio@udla.edu.ec",
            "first_name": "Patricio",
            "last_name": "d8372846#",
            "password": "Dinero555@"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["detail"][0]["loc"] == ["body", "last_name"]
    assert json_response["detail"][0]["msg"] == "Value error, Name must begin with a capital letter."


def test_update_staff_success(session: Session, client: TestClient, faker: Faker):
    """Test updating a staff member successfully."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create staff user to update
    staff_user = User(
        first_name="Old",
        last_name="Name",
        email="oldstaff@udla.edu.ec",
        hashed_password=get_password_hash("oldpassword"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Update staff
    response = client.patch(
        f"/staff/{staff_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Updated",
            "last_name": "Staff",
            "email": "updatedstaff@udla.edu.ec"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["first_name"] == "Updated"
    assert json_response["last_name"] == "Staff"
    assert json_response["email"] == "updatedstaff@udla.edu.ec"
    assert json_response["role"] == "staff"


def test_update_staff_password(session: Session, client: TestClient):
    """Test updating a staff member's password."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create staff user to update
    staff_user = User(
        first_name="Staff",
        last_name="User",
        email="staff@udla.edu.ec",
        hashed_password=get_password_hash("oldpassword"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Update staff password
    response = client.patch(
        f"/staff/{staff_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password": "NewPassword123@"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["first_name"] == "Staff"
    assert json_response["last_name"] == "User"
    assert json_response["email"] == "staff@udla.edu.ec"


def test_update_staff_not_found(session: Session, client: TestClient):
    """Test updating a non-existent staff member."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Try to update non-existent staff
    response = client.patch(
        "/staff/99999",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Updated"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Staff member not found"


def test_update_staff_wrong_role(session: Session, client: TestClient):
    """Test updating a user who is not staff."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create organizer user (not staff)
    organizer_user = User(
        first_name="Other",
        last_name="Organizer",
        email="other@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.ORGANIZER,
    )
    session.add(organizer_user)
    session.commit()
    session.refresh(organizer_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Try to update organizer as if they were staff
    response = client.patch(
        f"/staff/{organizer_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Updated"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"] == "User is not a staff member"


def test_update_staff_duplicate_email(session: Session, client: TestClient):
    """Test updating staff with an email that already exists."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create two staff users
    staff_user1 = User(
        first_name="Staff",
        last_name="One",
        email="staff1@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    staff_user2 = User(
        first_name="Staff",
        last_name="Two",
        email="staff2@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    session.add(staff_user1)
    session.add(staff_user2)
    session.commit()
    session.refresh(staff_user1)
    session.refresh(staff_user2)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Try to update staff2 with staff1's email
    response = client.patch(
        f"/staff/{staff_user2.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "staff1@udla.edu.ec"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert json_response["detail"] == "Email already exists or data conflict"


def test_update_staff_unauthorized(session: Session, client: TestClient):
    """Test updating staff without proper authorization."""
    # Create staff user
    staff_user = User(
        first_name="Staff",
        last_name="User",
        email="staff@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Try to update without token
    response = client.patch(
        f"/staff/{staff_user.id}",
        json={
            "first_name": "Updated"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_staff_success(session: Session, client: TestClient):
    """Test deleting a staff member successfully."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create staff user to delete
    staff_user = User(
        first_name="Staff",
        last_name="ToDelete",
        email="stafftodelete@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Delete staff
    response = client.delete(
        f"/staff/{staff_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify staff is deleted
    deleted_user = session.get(User, staff_user.id)
    assert deleted_user is None


def test_delete_staff_not_found(session: Session, client: TestClient):
    """Test deleting a non-existent staff member."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Try to delete non-existent staff
    response = client.delete(
        "/staff/99999",
        headers={"Authorization": f"Bearer {token}"}
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json_response["detail"] == "Staff member not found"


def test_delete_staff_wrong_role(session: Session, client: TestClient):
    """Test deleting a user who is not staff."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create organizer user (not staff)
    organizer_user = User(
        first_name="Other",
        last_name="Organizer",
        email="other@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.ORGANIZER,
    )
    session.add(organizer_user)
    session.commit()
    session.refresh(organizer_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Try to delete organizer as if they were staff
    response = client.delete(
        f"/staff/{organizer_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_response["detail"] == "User is not a staff member"


def test_delete_staff_unauthorized(session: Session, client: TestClient):
    """Test deleting staff without proper authorization."""
    # Create staff user
    staff_user = User(
        first_name="Staff",
        last_name="User",
        email="staff@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Try to delete without token
    response = client.delete(f"/staff/{staff_user.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_all_staff(session: Session, client: TestClient):
    """Test listing all staff members."""
    # Create staff users
    staff_users = []
    for i in range(3):
        staff_user = User(
            first_name=f"Staff{i}",
            last_name=f"User{i}",
            email=f"staff{i}@udla.edu.ec",
            hashed_password=get_password_hash("password"),
            role=Role.STAFF,
        )
        staff_users.append(staff_user)
        session.add(staff_user)
    
    # Create non-staff user
    session.add(
        User(
            first_name="Organizer",
            last_name="User",
            email="organizer@udla.edu.ec",
            hashed_password=get_password_hash("password"),
            role=Role.ORGANIZER,
        )
    )
    session.commit()

    # Get all staff
    response = client.get("/staff/all")

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(json_response) == 3
    
    # Verify all returned users are staff
    for staff_data in json_response:
        assert staff_data["role"] == "staff"
        assert staff_data["email"].endswith("@udla.edu.ec")


def test_update_staff_partial_update(session: Session, client: TestClient):
    """Test updating only some fields of a staff member."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create staff user to update
    staff_user = User(
        first_name="Original",
        last_name="Name",
        email="original@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Update only first name
    response = client.patch(
        f"/staff/{staff_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Updated"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["first_name"] == "Updated"
    assert json_response["last_name"] == "Name"  # Should remain unchanged
    assert json_response["email"] == "original@udla.edu.ec"  # Should remain unchanged


def test_update_staff_invalid_email_format(session: Session, client: TestClient):
    """Test updating staff with invalid email format."""
    # Create admin user
    session.add(
        User(
            first_name="Admin",
            last_name="User",
            email="admin@udla.edu.ec",
            hashed_password=get_password_hash("admin"),
            role=Role.ORGANIZER,
        )
    )
    
    # Create staff user to update
    staff_user = User(
        first_name="Staff",
        last_name="User",
        email="staff@udla.edu.ec",
        hashed_password=get_password_hash("password"),
        role=Role.STAFF,
    )
    session.add(staff_user)
    session.commit()
    session.refresh(staff_user)

    # Get token
    token = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    }).json()["access_token"]

    # Try to update with invalid email
    response = client.patch(
        f"/staff/{staff_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "invalid-email"
        }
    )

    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "email" in str(json_response["detail"])
