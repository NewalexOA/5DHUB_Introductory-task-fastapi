from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import schemas, models
from app.database import get_db
from urllib.parse import quote, unquote
import random
import string
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Get the base URL from the environment variable
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8080")

# Generate a random short ID
def generate_short_id(length: int = 8) -> str:
    """
    Generate a random string of specified length to use as a short URL ID.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# POST: Shorten a URL
@router.post("/", response_model=schemas.URLInfo, status_code=201)
async def shorten_url(request: schemas.URLRequest, db: Session = Depends(get_db)):
    """
    Shorten the given URL by generating a unique short ID and storing it in the database.
    """
    try:
        # Limit the number of attempts to generate a unique short_id
        MAX_ATTEMPTS = 10  # Maximum number of attempts

        # Generate a unique short_id
        for _ in range(MAX_ATTEMPTS):
            short_id = generate_short_id()
            existing_url = db.query(models.URL).filter(models.URL.short_id == short_id).first()
            if not existing_url:
                break
        else:
            # If a unique short_id was not found after MAX_ATTEMPTS
            raise HTTPException(status_code=500, detail="Could not generate a unique short ID after several attempts")

        # Create a new database entry
        new_url = models.URL(short_id=short_id, target_url=str(request.url))
        db.add(new_url)
        db.commit()
        db.refresh(new_url)

        # Return the shortened URL
        short_url = f"{BASE_URL}/{short_id}"
        return schemas.URLInfo(short_url=short_url)
    
    except IntegrityError:
        db.rollback()
        logger.error(f"Database integrity error when trying to save URL: {request.url}")
        raise HTTPException(status_code=500, detail="Database integrity error")
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{short_id}")
async def redirect_to_original(short_id: str, db: Session = Depends(get_db)):
    """
    Redirect to the original URL using the shortened URL ID from the database.
    """
    try:
        # Look for the entry in the database by short_id
        db_url = db.query(models.URL).filter(models.URL.short_id == short_id).first()
        if db_url:
            return RedirectResponse(url=db_url.target_url, status_code=307)
        else:
            raise HTTPException(status_code=404, detail="URL not found")
    
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving URL for short_id: {short_id}, error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    
    except Exception as e:
        # Check if the exception is an HTTPException
        if isinstance(e, HTTPException):
            raise e  # Re-raise to allow FastAPI to handle it
        logger.error(f"Unhandled error while redirecting for short_id: {short_id}, error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
