import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    if "pytest" not in sys.modules:
        await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
