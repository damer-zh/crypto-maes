import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Form
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.models.user import UserCreate, Token

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

router = APIRouter()

# Простая имитация базы данных (заменить на реальную)
fake_db = {}
revoked_tokens = set()

# Настройка шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    if token in revoked_tokens:
        raise HTTPException(status_code=401, detail="Token has been revoked")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
def register_user(user: UserCreate):
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    hashed_password = pwd_context.hash(user.password)
    fake_db[user.username] = hashed_password
    return {"message": "User registered successfully"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    
    if username not in fake_db or not pwd_context.verify(password, fake_db[username]):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    revoked_tokens.add(token)
    return {"message": "Successfully logged out"}

@router.post("/token")
def get_client_token(
    client_id: str = Form(...),
    client_secret: str = Form(...),
    grant_type: str = Form(...)
):
    # В реальном приложении эти данные должны храниться в безопасном месте
    valid_clients = {
        CLIENT_ID: CLIENT_SECRET
    }
    
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="Unsupported grant type")
        
    if client_id not in valid_clients or valid_clients[client_id] != client_secret:
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    
    access_token = create_access_token(data={"sub": client_id, "type": "client_credentials"})
    return {"access_token": access_token, "token_type": "bearer"}