# Сервис шифрования данных

## Оглавление
- [Описание](#описание)
- [Архитектура](#архитектура)
- [Установка и запуск](#установка-и-запуск)
- [API Endpoints](#api-endpoints)
- [Аутентификация](#аутентификация)
- [Шифрование](#шифрование)
- [Frontend](#frontend)
- [Безопасность](#безопасность)

## Описание
Сервис предоставляет API для шифрования и дешифрования текста и файлов с использованием алгоритма AES. Включает в себя систему аутентификации, rate limiting и мониторинг.

## Архитектура

### Компоненты системы
- Backend (FastAPI)
- Frontend (Vue.js)
- Redis (для rate limiting и кэширования)
- Docker (контейнеризация)

## Установка и запуск

### Предварительные требования
- Docker
- Docker Compose
- Python 3.10+
- Node.js 16+

## Установка

### Клонирование репозитория
git clone <repository-url>
#### Создание .env файла
Для примера возьмите .env.example, уберите .example, и замените значения на свои
#### Запуск с Docker Compose
docker-compose up --build


## Шифрование

### Поддерживаемые операции
- Шифрование текста (AES)
- Дешифрование текста (AES)
- Шифрование файлов (AES)
- Дешифрование файлов (AES)

### Требования к ключу
- Длина: 16, 24 или 32 байта
- Поддержка UTF-8 кодировки

## Frontend

### Основные функции
- Аутентификация пользователей
- Шифрование/дешифрование текста
- Загрузка и шифрование файлов
- Отображение ошибок и статуса операций

### App.vue
- Форма входа
- Форма client credentials
- Интерфейс шифрования текста
- Интерфейс шифрования файлов

# API Endpoints Documentation

## Аутентификация

### 1. Регистрация пользователя
http
POST /auth/register
Content-Type: application/json
{
"username": "string",
"password": "string"
}

**Ответ**: 
json
{
"message": "User registered successfully"
}

### 2. Вход пользователя
http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
username=string&password=string

**Ответ**:
json
{
"access_token": "string",
"token_type": "bearer"
}

### 3. Получение токена через Client Credentials
http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
client_id=string&client_secret=string&grant_type=client_credentials

http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
client_id=string&client_secret=string&grant_type=client_credentials

**Ответ**:
json
{
"access_token": "string",
"token_type": "bearer"
}

### 4. Выход пользователя
http
POST /auth/logout
Authorization: Bearer <token>

**Ответ**:
json
{
"message": "Successfully logged out"
}

## Шифрование/Дешифрование

### 1. Шифрование текста
http
POST /encrypt/aes
Authorization: Bearer <token>
Content-Type: multipart/form-data
text=string&key=string

**Ответ**:
json
{
"encrypted_text": "string"
}


### 2. Дешифрование текста
http
POST /decrypt/aes
Authorization: Bearer <token>
Content-Type: multipart/form-data
text=string&key=string

**Ответ**:
json
{
"decrypted_text": "string"
}

### 3. Шифрование файла
http
POST /encrypt/file
Authorization: Bearer <token>
Content-Type: multipart/form-data
file=binary&key=string

**Ответ**: Зашифрованный файл (application/octet-stream)

### 4. Дешифрование файла
http
POST /decrypt/file
Authorization: Bearer <token>
Content-Type: multipart/form-data
file=binary&key=string

**Ответ**: Расшифрованный файл (application/octet-stream)

## Мониторинг

### 1. Проверка здоровья сервиса
http
GET /health

**Ответ**:
json
{
"status": "healthy",
"redis": "connected"
}

## Безопасность

### Реализованные меры
- JWT аутентификация
- Rate limiting
- CORS защита
- Валидация входных данных
- Безопасное хранение ключей

### Рекомендации по развертыванию
- Использовать HTTPS
- Регулярно обновлять зависимости
- Настроить правильные CORS origins
- Использовать надежные пароли


### Метрики
- Количество запросов
- Статус Redis
- Ошибки аутентификации
- Время выполнения операций

## Дополнительные возможности

### Кэширование
- Кэширование результатов шифрования
- TTL для кэшированных данных
- Инвалидация кэша при необходимости

### Масштабирование
- Горизонтальное масштабирование через Docker Swarm/Kubernetes
- Балансировка нагрузки
- Репликация Redis

## Известные ограничения (зависит от .env файла)
1. Максимальный размер файла: 5MB
2. Ограничение rate limiting: 100 запросов/минута
3. Время жизни токена: 1 час
4. Поддерживаемые форматы файлов: все

## Решение проблем

### Частые ошибки
1. "Token has been revoked"
   - Решение: Повторная аутентификация

2. "Rate limit exceeded"
   - Решение: Подождать сброса лимита

3. "Redis connection error"
   - Решение: Проверить доступность Redis
