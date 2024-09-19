from pydantic import BaseModel, HttpUrl


class URLCreate(BaseModel):
    url: HttpUrl


class URLDB(BaseModel):
    id: int
    short_url: str
    target_url: HttpUrl

    class Config:
        from_attributes = True
