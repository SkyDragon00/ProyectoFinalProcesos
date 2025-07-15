from typing import Any
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session
from faker import Faker

from app.db.database import User
from app.models.Role import Role
from app.models.FaceRecognitionAiModel import FaceRecognitionAiModel
from app.security.security import get_password_hash


def test_get_organizer_info(client: TestClient, token: str, admin_user: tuple[User, str]):
    """Test the organizer info endpoint with valid token.

    The curl command to test this endpoint is:

    curl -X 'GET' \\
      'http://127.0.0.1:8000/info' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer {token}'
    """
    response = client.get("/info", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["email"] == admin_user[0].email
    assert json_response["first_name"] == admin_user[0].first_name
    assert json_response["last_name"] == admin_user[0].last_name
    assert json_response["role"] == admin_user[0].role


class TestAddOrganizer:
    """Test cases for adding new organizers."""

    def test_add_organizer_success(self, client: TestClient, token: str, faker: Faker):
        """Test successfully adding a new organizer."""
        new_organizer_data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(domain="udla.edu.ec"),
            "password": faker.password(length=12),
        }

        response = client.post(
            "/organizer/add",
            data=new_organizer_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        json_response = response.json()
        assert json_response["email"] == new_organizer_data["email"]
        assert json_response["first_name"] == new_organizer_data["first_name"]
        assert json_response["last_name"] == new_organizer_data["last_name"]
        assert json_response["role"] == Role.ORGANIZER.value
        assert "password" not in json_response
        assert "hashed_password" not in json_response

    def test_add_organizer_duplicate_email(self, client: TestClient, token: str, admin_user: tuple[User, str], faker: Faker):
        """Test adding organizer with duplicate email returns conflict error."""
        duplicate_organizer_data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": admin_user[0].email,  # Using existing email
            "password": faker.password(length=12),
        }

        response = client.post(
            "/organizer/add",
            data=duplicate_organizer_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]

    def test_add_organizer_unauthorized(self, client: TestClient, faker: Faker):
        """Test adding organizer without authentication returns unauthorized error."""
        new_organizer_data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(domain="udla.edu.ec"),
            "password": faker.password(length=12),
        }

        response = client.post("/organizer/add", data=new_organizer_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_organizer_invalid_data(self, client: TestClient, token: str):
        """Test adding organizer with invalid data returns validation error."""
        invalid_organizer_data = {
            "first_name": "",  # Empty first name
            "last_name": "",   # Empty last name
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short password
        }

        response = client.post(
            "/organizer/add",
            data=invalid_organizer_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListOrganizers:
    """Test cases for listing organizers."""

    def test_list_organizers_success(self, client: TestClient, token: str, session: Session, faker: Faker):
        """Test successfully retrieving all organizers."""
        # Add additional organizers to the session
        organizer1 = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        organizer2 = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        # Add a staff member (should not appear in results)
        staff_member = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.STAFF,
        )

        session.add_all([organizer1, organizer2, staff_member])
        session.commit()

        response = client.get("/organizer/all")

        assert response.status_code == status.HTTP_200_OK
        json_response: list[dict[str, Any]] = response.json()
        assert isinstance(json_response, list)
        # Should include admin_user + 2 additional organizers = 3 total
        organizers_count = len(json_response)
        assert organizers_count == 3
        # Verify all returned users are organizers
        for user in json_response:
            assert user["role"] == Role.ORGANIZER.value

    def test_list_organizers_empty(self, client: TestClient, session: Session):
        """Test listing organizers when no organizers exist."""
        response = client.get("/organizer/all")

        assert response.status_code == status.HTTP_200_OK
        json_response: list[dict[str, Any]] = response.json()
        assert isinstance(json_response, list)
        organizers_count = len(json_response)
        assert organizers_count == 0


class TestUpdateOrganizer:
    """Test cases for updating organizers."""

    def test_update_organizer_success(self, client: TestClient, token: str, session: Session, faker: Faker):
        """Test successfully updating an organizer."""
        # Create an organizer to update
        organizer = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

        update_data = {
            "first_name": "Updated Name",
            "last_name": "Updated LastName",
        }

        response = client.patch(
            f"/organizer/{organizer.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert json_response["first_name"] == update_data["first_name"]
        assert json_response["last_name"] == update_data["last_name"]
        assert json_response["email"] == organizer.email  # Should remain unchanged

    def test_update_organizer_password(self, client: TestClient, token: str, session: Session, faker: Faker):
        """Test updating organizer password."""
        organizer = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

        old_password_hash = organizer.hashed_password
        new_password = faker.password(length=12)
        update_data = {"password": new_password}

        response = client.patch(
            f"/organizer/{organizer.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        # Refresh from database to check password was updated
        session.refresh(organizer)
        assert organizer.hashed_password != old_password_hash

    def test_update_organizer_not_found(self, client: TestClient, token: str):
        """Test updating non-existent organizer returns not found error."""
        update_data = {"first_name": "Updated Name"}

        response = client.patch(
            "/organizer/99999",  # Non-existent ID
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrado" in response.json()["detail"]

    def test_update_non_organizer_user(self, client: TestClient, token: str, session: Session, faker: Faker):
        """Test updating a user who is not an organizer returns bad request."""
        # Create a staff member
        staff_member = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.STAFF,
        )
        session.add(staff_member)
        session.commit()
        session.refresh(staff_member)

        update_data = {"first_name": "Updated Name"}

        response = client.patch(
            f"/organizer/{staff_member.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no es un organizador" in response.json()["detail"]

    def test_update_organizer_duplicate_email(self, client: TestClient, token: str, session: Session, faker: Faker, admin_user: tuple[User, str]):
        """Test updating organizer with duplicate email returns conflict error."""
        organizer = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

        update_data = {"email": admin_user[0].email}  # Try to use existing email

        response = client.patch(
            f"/organizer/{organizer.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "ya existe" in response.json()["detail"]

    def test_update_organizer_unauthorized(self, client: TestClient, session: Session, faker: Faker):
        """Test updating organizer without authentication returns unauthorized error."""
        organizer = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

        update_data = {"first_name": "Updated Name"}

        response = client.patch(f"/organizer/{organizer.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteOrganizer:
    """Test cases for deleting organizers."""

    def test_delete_organizer_success(self, client: TestClient, token: str, session: Session, faker: Faker):
        """Test successfully deleting an organizer."""
        organizer = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

        response = client.delete(
            f"/organizer/{organizer.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Verify the organizer was deleted
        deleted_organizer = session.get(User, organizer.id)
        assert deleted_organizer is None

    def test_delete_organizer_not_found(self, client: TestClient, token: str):
        """Test deleting non-existent organizer returns not found error."""
        response = client.delete(
            "/organizer/99999",  # Non-existent ID
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrado" in response.json()["detail"]

    def test_delete_non_organizer_user(self, client: TestClient, token: str, session: Session, faker: Faker):
        """Test deleting a user who is not an organizer returns bad request."""
        staff_member = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.STAFF,
        )
        session.add(staff_member)
        session.commit()
        session.refresh(staff_member)

        response = client.delete(
            f"/organizer/{staff_member.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no es un organizador" in response.json()["detail"]

    def test_delete_self_organizer(self, client: TestClient, token: str, admin_user: tuple[User, str]):
        """Test organizer cannot delete themselves."""
        response = client.delete(
            f"/organizer/{admin_user[0].id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "eliminarte a ti mismo" in response.json()["detail"]

    def test_delete_organizer_unauthorized(self, client: TestClient, session: Session, faker: Faker):
        """Test deleting organizer without authentication returns unauthorized error."""
        organizer = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(domain="udla.edu.ec"),
            hashed_password=get_password_hash(faker.password()),
            role=Role.ORGANIZER,
        )
        session.add(organizer)
        session.commit()
        session.refresh(organizer)

        response = client.delete(f"/organizer/{organizer.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestFaceRecognitionSettings:
    """Test cases for face recognition AI model settings."""

    def test_get_face_recognition_settings(self, client: TestClient):
        """Test retrieving current face recognition settings."""
        response = client.get("/organizer/get-settings")

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert "model" in json_response
        assert "threshold" in json_response

    def test_change_face_recognition_model(self, client: TestClient):
        """Test changing face recognition AI model."""
        response = client.patch(
            "/organizer/change-settings",
            params={"model_name": FaceRecognitionAiModel.FACENET.value}
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert json_response["model"] == FaceRecognitionAiModel.FACENET.value

    def test_change_face_recognition_threshold(self, client: TestClient):
        """Test changing face recognition threshold."""
        test_threshold = 0.7
        response = client.patch(
            "/organizer/change-settings",
            params={"threshold": test_threshold}
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert abs(json_response["threshold"] - test_threshold) < 0.01

    def test_reset_face_recognition_threshold(self, client: TestClient):
        """Test resetting face recognition threshold to default."""
        # First set a threshold
        client.patch("/organizer/change-settings", params={"threshold": 0.8})
        
        # Then reset it
        response = client.patch(
            "/organizer/change-settings",
            params={"threshold": 0}
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        # After reset, threshold should be default value
        assert "threshold" in json_response

    def test_change_both_model_and_threshold(self, client: TestClient):
        """Test changing both model and threshold simultaneously."""
        test_threshold = 0.9
        response = client.patch(
            "/organizer/change-settings",
            params={
                "model_name": FaceRecognitionAiModel.VGG_FACE.value,
                "threshold": test_threshold
            }
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert json_response["model"] == FaceRecognitionAiModel.VGG_FACE.value
        assert abs(json_response["threshold"] - test_threshold) < 0.01

    def test_change_settings_no_params(self, client: TestClient):
        """Test calling change settings endpoint without parameters."""
        response = client.patch("/organizer/change-settings")

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert "model" in json_response
        assert "threshold" in json_response
