from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db.database import User
from app.models.Role import Role
from app.security.security import get_password_hash


def test_read_main(client: TestClient):
    """Test the root endpoint to check if returns a hello world message.

    The curl command to test this endpoint is:

    curl -X 'GET' \\
      'http://127.0.0.1:8000/' \\
      -H 'accept: application/json'
    """
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Hello World"}


def test_obtain_token(session: Session, client: TestClient):
    """Test the token endpoint with valid credentials of the admin user that is
    created by default.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=admin%40udla.edu.ec&password=admin&scope=organizer&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert len(response.json()["access_token"]) > 10
    assert response.json()["token_type"] == "bearer"


def test_obtain_token_invalid_user(session: Session, client: TestClient):
    """Test the token endpoint with invalid credentials.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=invalid_user&password=invalid_password&scope=organizer&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "invalid_user",
        "password": "invalid_password",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}


def test_obtain_token_invalid_password(session: Session, client: TestClient):
    """Test the token endpoint with invalid password.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=admin@udla.edu.ec&password=invalid_password&scope=organizer&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "invalid_password",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}


def test_obtain_token_invalid_scope(session: Session, client: TestClient):
    """Try to obtain the token with a scope that can not have that type of user.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=admin@udla.edu.ec&password=invalid_password&scope=staff&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "staff",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


def test_obtain_token_no_scope(session: Session, client: TestClient):
    """Test the token endpoint without providing scope - should use default scopes from user role.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=admin%40udla.edu.ec&password=admin&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert len(response.json()["access_token"]) > 10
    assert response.json()["token_type"] == "bearer"


def test_obtain_token_staff_user_with_staff_scope(session: Session, client: TestClient):
    """Test the token endpoint with a staff user requesting staff scope.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=staff%40udla.edu.ec&password=staff123&scope=staff&client_id=&client_secret='
    """
    session.add(
        User(
            first_name="Staff",
            last_name="User",
            email="staff@udla.edu.ec",
            hashed_password=get_password_hash("staff123"),
            role=Role.STAFF,
        )
    )
    session.commit()

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "staff@udla.edu.ec",
        "password": "staff123",
        "scope": "staff",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert len(response.json()["access_token"]) > 10
    assert response.json()["token_type"] == "bearer"


def test_info_endpoint_authenticated(session: Session, client: TestClient):
    """Test the /info endpoint with authenticated user.

    The curl command to test this endpoint is:

    curl -X 'GET' \\
      'http://127.0.0.1:8000/info' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer <access_token>'
    """
    # Create a user
    user = User(
        first_name="Test",
        last_name="User",
        email="test@udla.edu.ec",
        hashed_password=get_password_hash("testpass"),
        role=Role.ORGANIZER,
    )
    session.add(user)
    session.commit()

    # Get token
    token_response = client.post("/token", data={
        "grant_type": "password",
        "username": "test@udla.edu.ec",
        "password": "testpass",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    })
    token = token_response.json()["access_token"]

    # Test /info endpoint
    response = client.get("/info", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    
    user_data = response.json()
    assert user_data["email"] == "test@udla.edu.ec"
    assert user_data["first_name"] == "Test"
    assert user_data["last_name"] == "User"
    assert user_data["role"] == "organizer"


def test_info_endpoint_unauthenticated(client: TestClient):
    """Test the /info endpoint without authentication.

    The curl command to test this endpoint is:

    curl -X 'GET' \\
      'http://127.0.0.1:8000/info' \\
      -H 'accept: application/json'
    """
    response = client.get("/info")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_info_endpoint_invalid_token(client: TestClient):
    """Test the /info endpoint with invalid token.

    The curl command to test this endpoint is:

    curl -X 'GET' \\
      'http://127.0.0.1:8000/info' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer invalid_token'
    """
    response = client.get("/info", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


def test_middleware_process_time_header(client: TestClient):
    """Test that the custom middleware adds the X-Process-Time header.

    The curl command to test this endpoint is:

    curl -X 'GET' \\
      'http://127.0.0.1:8000/' \\
      -H 'accept: application/json' \\
      -v
    """
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "X-Process-Time" in response.headers
    # Check that the process time is a valid float
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0


def test_cors_headers(client: TestClient):
    """Test that CORS headers are present in the response.

    The curl command to test this endpoint is:

    curl -X 'OPTIONS' \\
      'http://127.0.0.1:8000/' \\
      -H 'Origin: http://127.0.0.1:8001' \\
      -H 'Access-Control-Request-Method: GET' \\
      -v
    """
    # Test preflight request
    response = client.options(
        "/",
        headers={
            "Origin": "http://127.0.0.1:8001",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers


def test_token_endpoint_missing_fields(client: TestClient):
    """Test the token endpoint with missing required fields.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password'
    """
    response = client.post("/token", data={
        "grant_type": "password",
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_token_endpoint_empty_username(session: Session, client: TestClient):
    """Test the token endpoint with empty username.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=&password=admin&scope=organizer&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "",
        "password": "admin",
        "scope": "organizer",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}


def test_multiple_scopes(session: Session, client: TestClient):
    """Test the token endpoint with multiple scopes for an organizer user.

    The curl command to test this endpoint is:

    curl -X 'POST' \\
      'http://127.0.0.1:8000/token' \\
      -H 'accept: application/json' \\
      -H 'Content-Type: application/x-www-form-urlencoded' \\
      -d 'grant_type=password&username=admin%40udla.edu.ec&password=admin&scope=organizer+assistant&client_id=&client_secret='
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

    response = client.post("/token", data={
        "grant_type": "password",
        "username": "admin@udla.edu.ec",
        "password": "admin",
        "scope": "organizer assistant",
        "client_id": "",
        "client_secret": ""
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert len(response.json()["access_token"]) > 10
    assert response.json()["token_type"] == "bearer"
