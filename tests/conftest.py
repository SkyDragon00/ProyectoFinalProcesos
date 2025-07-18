import pytest
import shutil
from pathlib import Path
from faker import Faker
from faker.providers import BaseProvider
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.database import User, get_session
from app.main import app
from app.models.Role import Role
from app.security.security import get_password_hash


class EcuadorProvider(BaseProvider):
    def ecuadorian_id_number(self) -> str:
        # Genera una cédula ecuatoriana válida (10 dígitos, con verificación simple)
        from random import randint

        def calculate_verifier(digits: str) -> int:
            coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            total = 0
            for i in range(9):
                val = int(digits[i]) * coef[i]
                if val > 9:
                    val -= 9
                total += val
            verifier = 10 - (total % 10)
            return 0 if verifier == 10 else verifier

        province = f"{randint(1,24):02d}"
        middle = f"{randint(1000000, 9999999)}"
        base = province + middle[:7]
        verifier = calculate_verifier(base)
        return base + str(verifier)


@pytest.fixture(name="faker")
def faker():
    fake = Faker()
    fake.add_provider(EcuadorProvider)
    return fake


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="clean_face_db")
def clean_face_db_fixture():
    """Clean up face recognition database before each test."""
    people_imgs_path = Path("./data/people_imgs")
    if people_imgs_path.exists() and people_imgs_path.is_dir():
        try:
            shutil.rmtree(people_imgs_path)
        except OSError:
            # Handle permission errors on Windows
            import time
            time.sleep(0.1)
            try:
                shutil.rmtree(people_imgs_path)
            except OSError:
                pass  # Ignore if we can't clean up
    people_imgs_path.mkdir(parents=True, exist_ok=True)
    yield
    # Cleanup after test as well
    if people_imgs_path.exists() and people_imgs_path.is_dir():
        try:
            shutil.rmtree(people_imgs_path)
        except OSError:
            pass  # Ignore cleanup errors


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        return session

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session, faker: Faker):
    password = faker.password()
    user = User(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(domain="udla.edu.ec"),
        hashed_password=get_password_hash(password),
        role=Role.ORGANIZER,
    )

    session.add(user)
    session.commit()

    return user, password


@pytest.fixture(name="token")
def token_fixture(client: TestClient, admin_user: tuple[User, str]):
    token = client.post(
        "/token",
        data={
            "grant_type": "password",
            "username": admin_user[0].email,
            "password": admin_user[1],
            "scope": "organizer",
            "client_id": "",
            "client_secret": ""
        }
    ).json()["access_token"]

    return token
