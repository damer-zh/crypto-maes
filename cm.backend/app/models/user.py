from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ClientCredentials(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str = "client_credentials"