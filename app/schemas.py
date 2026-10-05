from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class UrlCreate(BaseModel):
    original_url: HttpUrl


class UrlResponse(BaseModel):
    slug: str
    original_url: str
    short_url: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    # Lets Pydantic read data straight from a database object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    # Note: no password field here, so it can never leak in a response.


class Token(BaseModel):
    access_token: str
    token_type: str