from sqlalchemy import Column, Integer, String
from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String(length=8), unique=True, index=True)
    target_url = Column(String, unique=True, index=True)
