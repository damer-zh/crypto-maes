import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import UserCreate, Token

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Простая имитация базы данных (можно заменить на реальную)
fake_db = {}

# Настройка шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
def register_user(user: UserCreate):
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    hashed_password = pwd_context.hash(user.password)
    fake_db[user.username] = hashed_password
    print(fake_db)
    return {"message": "User registered successfully"}

# Логин и получение токена
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    
    if username not in fake_db or not pwd_context.verify(password, fake_db[username]):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    access_token = create_access_token(data={"sub": username})
    print({"access_token": access_token, "token_type": "bearer"})
    return {"access_token": access_token, "token_type": "bearer"}