import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_encrypt_file_size_limit():
    # Попробуем загрузить большой файл (например, 6 MB)
    large_content = b"A" * (6 * 1024 * 1024)
    response = client.post(
        "/encrypt/file",
        files={"file": ("large_file.txt", large_content)},
        data={"key": "16_byte_key_1234", "method": "aes"},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "File size exceeds the allowed limit (5 MB)"


def test_encrypt_file_invalid_key_length():
    # Проверка на слишком короткий ключ
    content = b"Secret content"
    response = client.post(
        "/encrypt/file",
        files={"file": ("test.txt", content)},
        data={"key": "short", "method": "aes"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Key must be 16, 24, or 32 bytes long"


def test_valid_file_encryption():
    # Тестируем успешное шифрование файла
    content = b"Simple file content"
    response = client.post(
        "/encrypt/file",
        files={"file": ("test.txt", content)},
        data={"key": "16_byte_key_1234", "method": "aes"},
    )
    assert response.status_code == 200
    assert "encrypted_file" in response.json()


def test_valid_file_decryption():
    # Тестируем успешное дешифрование файла
    content = b"Simple file content"
    encrypted_response = client.post(
        "/encrypt/file",
        files={"file": ("test.txt", content)},
        data={"key": "16_byte_key_1234", "method": "aes"},
    )

    encrypted_file = encrypted_response.json()["encrypted_file"]
    with open(encrypted_file, "rb") as encrypted_data:
        decrypted_response = client.post(
            "/decrypt/file",
            files={"file": ("test.txt.enc", encrypted_data.read())},
            data={"key": "16_byte_key_1234", "method": "aes"},
        )
        assert decrypted_response.status_code == 200