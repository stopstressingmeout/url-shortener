from pydantic import BaseModel, HttpUrl

class UrlCreate(BaseModel):
    original_url:HttpUrl

class UrlResponse(BaseModel):
    slug:str
    original_url:str
    short_url:str