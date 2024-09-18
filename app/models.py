from sqlalchemy import Column, Integer, String
from app.database import Base

class URL(Base):
    """
    Represents a URL model for the database.
    
    Attributes:
        id (int): The primary key of the URL.
        short_id (str): The unique short identifier for the URL.
        target_url (str): The original URL that is being shortened.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)  # The primary key of the URL
    short_id = Column(String(length=8), unique=True, index=True)  # The unique short identifier
    target_url = Column(String)  # The original URL
