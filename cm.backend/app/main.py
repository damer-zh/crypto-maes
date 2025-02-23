import logging
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from app.auth import create_access_token, verify_token
from app.encryption.aes import encrypt_file_aes, decrypt_file_aes, encrypt_aes, decrypt_aes
from app.auth import router as auth_router
from fastapi.responses import StreamingResponse
from io import BytesIO


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),               # Лог в консоль
        logging.FileHandler("app.log"),        # Лог в файл
    ],
)

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 5
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # или порт Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.get("/")
def read_root():
    logger.info("Проверка работы сервера")
    return {"message": "Сервер работает!"}

# Ловим ошибки на уровне middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Получен запрос: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP-ошибка: {exc.detail} (статус {exc.status_code})")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.post("/encrypt/aes")
def encrypt_text_aes(
    text: str = Form(...),
    key: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    verify_token(token)

    if len(key) not in [16, 24, 32]:
        logger.warning("Неверная длина ключа")
        raise HTTPException(status_code=400, detail="Key must be 16, 24, or 32 bytes long")
    
    try:
        encrypted_text = encrypt_aes(text.encode(), key)
        logger.info("Текст успешно зашифрован")
        return {"encrypted_text": encrypted_text}
    except Exception as e:
        logger.error(f"Ошибка шифрования текста: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt/aes")
def decrypt_text_aes(
    text: str = Form(...),
    key: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    try:
        verify_token(token)
        decrypted_text = decrypt_aes(text, key)
        logger.info("Сообщение успешно расшифровано")
        return {"decrypted_text": decrypted_text}
    except Exception as e:
        logger.error(f"Ошибка дешифрования сообщения: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/encrypt/file")
def encrypt_file(
    file: UploadFile = File(...),
    key: str = Form(...),
    method: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    logger.info(f"Начато шифрование файла: {file.filename}")
    verify_token(token)

    if len(key) not in [16, 24, 32]:
        logger.warning("Неверная длина ключа")
        raise HTTPException(status_code=400, detail="Key must be 16, 24, or 32 bytes long")

    try:
        content = file.file.read()
        logger.info(f"Файл {file.filename} загружен, размер: {len(content)} байт")

        if method == "aes":
            encrypted_content = encrypt_file_aes(content, key)
        else:
            logger.warning("Неподдерживаемый метод шифрования")
            raise HTTPException(status_code=400, detail="Unsupported encryption method")

        output_file = f"{UPLOAD_DIR}/{file.filename}.enc"
        filename_enc = f"{file.filename}.enc"
        with open(output_file, "wb") as f:
            f.write(encrypted_content)

        logger.info(f"Файл успешно зашифрован и сохранен как {output_file}")
        return StreamingResponse(
            BytesIO(encrypted_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename_enc}.enc"}
        )

    except Exception as e:
        logger.error(f"Ошибка шифрования файла: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt/file")
def decrypt_file(
    file: UploadFile = File(...),
    key: str = Form(...),
    method: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    logger.info(f"Начато расшифрование файла: {file.filename}")
    verify_token(token)

    try:
        content = file.file.read()
        logger.info(f"Файл {file.filename} загружен, размер: {len(content)} байт")

        if method == "aes":
            decrypted_content = decrypt_file_aes(content, key)
        else:
            logger.warning("Неподдерживаемый метод дешифрования")
            raise HTTPException(status_code=400, detail="Unsupported decryption method")
        
        filename, ext = os.path.splitext(file.filename)

        output_file = f"{UPLOAD_DIR}/{filename}_decrypted{ext}"
        with open(output_file, "wb") as f:
            f.write(decrypted_content)

        logger.info(f"Файл успешно расшифрован и сохранен как {output_file}")
        return StreamingResponse(
            BytesIO(decrypted_content), 
            headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.enc', '')}"}
            )

    except Exception as e:
        logger.error(f"Ошибка расшифрования файла: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
