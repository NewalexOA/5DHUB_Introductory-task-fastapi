import logging
import os
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, crud
from app.database import get_db
from app.utils import generate_short_id
from app.constants import MAX_ATTEMPTS

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8080")


@router.post("/", response_model=schemas.URLDB, status_code=HTTPStatus.CREATED)
async def create_short_url(request: schemas.URLCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_url = await crud.get_url_by_target(db, str(request.url))
        if existing_url:
            return schemas.URLDB(
                id=existing_url.id,
                short_url=f"{BASE_URL}/{existing_url.short_id}",
                target_url=existing_url.target_url
            )

        for _ in range(MAX_ATTEMPTS):
            short_id = generate_short_id()
            if not await crud.get_url_by_short_id(db, short_id):
                break
        else:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Failed to generate a unique short identifier after several attempts"
            )

        new_url = await crud.create_url(db, short_id, str(request.url))
        return schemas.URLDB(
            id=new_url.id,
            short_url=f"{BASE_URL}/{new_url.short_id}",
            target_url=new_url.target_url
        )

    except IntegrityError:
        logger.error(f"Database integrity error when saving URL: {request.url}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database integrity error")

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error")

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{short_id}")
async def redirect_to_original(short_id: str, db: AsyncSession = Depends(get_db)):
    try:
        db_url = await crud.get_url_by_short_id(db, short_id)
        if db_url:
            return RedirectResponse(url=db_url.target_url, status_code=HTTPStatus.TEMPORARY_REDIRECT)
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="URL not found")

    except SQLAlchemyError as e:
        logger.error(f"Database error when retrieving URL for short_id: {short_id}, error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database error")

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Unhandled error during redirection for short_id: {short_id}, error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal server error")
    