from pydantic import BaseModel, HttpUrl

# Schema for incoming request
class URLRequest(BaseModel):
    url: HttpUrl  # The URL to be shortened

# Schema for response
class URLInfo(BaseModel):
    short_url: str  # The shortened URL

    class Config:
        from_attributes = True  # Allow attributes to be used as fields
