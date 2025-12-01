from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # Pydantic v2 way to allow ORM objects

class UserBase(BaseModel):
    email: EmailStr


class UserLogin(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

