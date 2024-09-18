import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.models import URL

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the dependency override
app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """
    Fixture to create and drop database tables before and after each test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Test creating a short URL
def test_create_short_url():
    """
    Test the creation of a short URL.
    """
    data = {"url": "https://example.com"}
    response = client.post("/", json=data)
    assert response.status_code == 201
    assert "short_url" in response.json()

    # Check that short_url has the expected format
    short_url = response.json()["short_url"]
    assert short_url.startswith("http://127.0.0.1:8080/")
    short_id = short_url.split("/")[-1]
    assert len(short_id) == 8  # Default length of short_id is 8

# Test redirecting to the original URL
def test_redirect_to_original_url():
    """
    Test redirection by short URL.
    """
    # Create a short URL
    data = {"url": "https://example.com"}
    post_response = client.post("/", json=data)
    assert post_response.status_code == 201
    short_url = post_response.json()["short_url"]
    short_id = short_url.split("/")[-1]

    # Check redirection
    get_response = client.get(f"/{short_id}", allow_redirects=False)
    assert get_response.status_code == 307
    assert get_response.headers["location"] == "https://example.com/"

# Test redirection by a non-existent short URL
def test_redirect_nonexistent_url():
    """
    Test redirection by a non-existent short URL.
    """
    response = client.get("/nonexistent", allow_redirects=False)
    assert response.status_code == 404
    assert response.json() == {"detail": "URL not found"}

# Test handling of invalid URL format
def test_invalid_url_format():
    """
    Test handling of invalid URL format.
    """
    data = {"url": "not_a_valid_url"}
    response = client.post("/", json=data)
    assert response.status_code == 422  # Pydantic validation error

# Test direct database entry creation
def test_database_entry_created():
    """
    Test direct creation of a database entry.
    """
    db = TestingSessionLocal()
    try:
        new_url = URL(short_id="test1234", target_url="https://example.com")
        db.add(new_url)
        db.commit()

        # Check that the entry was created
        db_url = db.query(URL).filter(URL.short_id == "test1234").first()
        assert db_url is not None
        assert db_url.target_url == "https://example.com"
    finally:
        db.close()

# Test absence of a database entry
def test_database_entry_not_found():
    """
    Test absence of a database entry.
    """
    db = TestingSessionLocal()
    try:
        db_url = db.query(URL).filter(URL.short_id == "nonexistent").first()
        assert db_url is None
    finally:
        db.close()

# Test handling of short_id collisions
def test_short_id_collision(monkeypatch):
    """
    Test handling of short_id collisions.
    """

    # Mock the function to always return the same short_id on first call, then a unique one
    generated_ids = ["fixed_id", "fixed_id2"]  # Two different identifiers to simulate collision

    def mock_generate_short_id(length=8):
        return generated_ids.pop(0)

    # Mock the short_id generation function
    monkeypatch.setattr("app.routes.generate_short_id", mock_generate_short_id)

    # First request
    data1 = {"url": "https://example.com/1"}
    response1 = client.post("/", json=data1)
    assert response1.status_code == 201
    short_url1 = response1.json()["short_url"]

    # Second request where the system should generate a different identifier
    data2 = {"url": "https://example.com/2"}
    response2 = client.post("/", json=data2)
    assert response2.status_code == 201
    short_url2 = response2.json()["short_url"]

    # Check that the second identifier is different from the first
    assert short_url1 != short_url2  # They should be different

# Test handling of IntegrityError on short_id collision
def test_integrity_error_on_collision(monkeypatch):
    """
    Test handling of IntegrityError when attempting to add a duplicate short_id.
    """

    # Mock generate_short_id to return the same id twice, then a unique one
    generated_ids = ["fixed_id", "fixed_id", "unique_id"]

    def mock_generate_short_id(length=8):
        return generated_ids.pop(0)

    # Mock the generate_short_id function in the routes module
    monkeypatch.setattr("app.routes.generate_short_id", mock_generate_short_id)

    # First request
    data1 = {"url": "https://example.com/1"}
    response1 = client.post("/", json=data1)
    assert response1.status_code == 201

    # Second request with the same short_id, causing an IntegrityError
    data2 = {"url": "https://example.com/2"}
    response2 = client.post("/", json=data2)

    # The application should handle the IntegrityError and retry
    assert response2.status_code == 201
    assert response2.json()["short_url"] != response1.json()["short_url"]

    # Verify that the unique_id was used for the second URL
    short_url1 = response1.json()["short_url"]
    short_url2 = response2.json()["short_url"]
    assert short_url1.endswith("/fixed_id")
    assert short_url2.endswith("/unique_id")
