from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class TextData(BaseModel):
    text: str
    key: str

class Token(BaseModel):
    access_token: str
    token_type: str