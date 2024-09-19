from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models


async def get_url_by_short_id(db: AsyncSession, short_id: str):
    result = await db.execute(select(models.URL).filter(models.URL.short_id == short_id))
    return result.scalars().first()


async def get_url_by_target(db: AsyncSession, target_url: str):
    result = await db.execute(select(models.URL).filter(models.URL.target_url == target_url))
    return result.scalars().first()


async def create_url(db: AsyncSession, short_id: str, target_url: str):
    new_url = models.URL(short_id=short_id, target_url=target_url)
    db.add(new_url)
    try:
        await db.commit()
        await db.refresh(new_url)
        return new_url
    except IntegrityError:
        await db.rollback()
        raise
