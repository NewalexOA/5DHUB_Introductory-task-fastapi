import sys
import os
import pytest_asyncio
from sqlalchemy import text, select

if os.path.exists("./test.db"):
    os.remove("./test.db")

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
print(f"Используется тестовая база данных: {os.environ['DATABASE_URL']}")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, get_db, SessionLocal
from main import app
from app.models import URL

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from asgi_lifespan import LifespanManager

async def override_get_db():
    async with SessionLocal() as db:
        yield db

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_and_teardown():
    print("Запуск фикстуры setup_and_teardown...")

    async with engine.begin() as conn:
        print("Создание таблиц...")
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы.")

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        print(f"Таблицы в базе данных: {tables}")

    if not tables:
        raise Exception("Таблицы не были созданы в базе данных!")

    yield

    async with engine.begin() as conn:
        print("Удаление таблиц...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Таблицы успешно удалены.")

@pytest.mark.asyncio
async def test_create_short_url(client):
    print("Запуск test_create_short_url...")
    data = {"url": "https://example.com"}
    response = await client.post("/", json=data)
    print(f"Код ответа: {response.status_code}")
    print(f"Содержимое ответа: {response.text}")
    assert response.status_code == 201, f"Ожидался код ответа 201, но получен {response.status_code}"

@pytest.mark.asyncio
async def test_redirect_to_original_url(client):
    print("Запуск test_redirect_to_original_url...")
    data = {"url": "https://example.com"}
    post_response = await client.post("/", json=data)
    print(f"Код ответа POST: {post_response.status_code}")
    print(f"Содержимое ответа POST: {post_response.text}")
    assert post_response.status_code == 201, f"Ожидался код ответа 201, но получен {post_response.status_code}"
    short_url = post_response.json()["short_url"]
    short_id = short_url.split("/")[-1]
    redirect_response = await client.get(f"/{short_id}", follow_redirects=False)
    print(f"Код ответа редиректа: {redirect_response.status_code}")
    assert redirect_response.status_code == 307, f"Ожидался код ответа 307, но получен {redirect_response.status_code}"
    assert redirect_response.headers["location"].rstrip('/') == "https://example.com"
    
@pytest.mark.asyncio
async def test_database_entry_created():
    print("Запуск test_database_entry_created...")
    async with SessionLocal() as db:
        new_url = URL(short_id="test1234", target_url="https://example.com")
        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)
        result = await db.execute(select(URL).filter_by(short_id="test1234"))
        db_url = result.scalar_one_or_none()
        print(f"Запись в базе данных: {db_url}")
        assert db_url is not None, "Запись URL не была создана в базе данных"
        assert db_url.target_url == "https://example.com"

@pytest.mark.asyncio
async def test_database_entry_not_found():
    print("Запуск test_database_entry_not_found...")
    async with SessionLocal() as db:
        db_url = await db.get(URL, "nonexistent")
        print(f"Запись в базе данных для 'nonexistent': {db_url}")
        assert db_url is None, "Запись URL не должна существовать в базе данных"

@pytest.mark.asyncio
async def test_short_id_collision(client, monkeypatch):
    print("Запуск test_short_id_collision...")
    generated_ids = ["fixed_id", "fixed_id2"]

    def mock_generate_short_id(length=8):
        return generated_ids.pop(0)

    monkeypatch.setattr("app.routes.generate_short_id", mock_generate_short_id)

    data1 = {"url": "https://example.com/1"}
    response1 = await client.post("/", json=data1)
    print(f"Код ответа 1: {response1.status_code}")
    print(f"Содержимое ответа 1: {response1.text}")
    assert response1.status_code == 201, f"Ожидался код ответа 201, но получен {response1.status_code}"

@pytest.mark.asyncio
async def test_integrity_error_on_collision(client, monkeypatch):
    print("Запуск test_integrity_error_on_collision...")
    generated_ids = ["fixed_id", "fixed_id", "unique_id"]

    def mock_generate_short_id(length=8):
        return generated_ids.pop(0)

    monkeypatch.setattr("app.routes.generate_short_id", mock_generate_short_id)

    data1 = {"url": "https://example.com/1"}
    response1 = await client.post("/", json=data1)
    print(f"Код ответа 1: {response1.status_code}")
    print(f"Содержимое ответа 1: {response1.text}")
    assert response1.status_code == 201, f"Ожидался код ответа 201, но получен {response1.status_code}"
    