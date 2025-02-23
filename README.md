# Crypto MAES - Сервис шифрования и дешифрования

## Описание
Веб-приложение для шифрования и дешифрования текста и файлов с использованием алгоритма AES. Состоит из бэкенд-части на FastAPI и фронтенд-части на Vue.js.

## Требования
- Python 3.10+
- Node.js 20+
- Docker и Docker Compose

## Структура проекта
├── cm.backend/ # Бэкенд на FastAPI
├── cm.frontend/ # Фронтенд на Vue.js
└── docker-compose.yml # Конфигурация Docker

## Установка и запуск

### 1. Клонирование репозитория
bash
git clone <repository-url>
cd crypto-maes


### 2. Настройка переменных окружения
Создайте файл `.env` в корневой директории:
plaintext
BACKEND_PORT=8000
FRONTEND_PORT=5173


### 3. Запуск с помощью Docker
bash
docker-compose up --build


После запуска:
- Фронтенд: http://localhost:5173
- Бэкенд: http://localhost:8000
- API документация: http://localhost:8000/docs

### 4. Запуск без Docker

#### Бэкенд
bash
cd cm.backend
python -m venv env
source env/bin/activate # для Linux/MacOS
env\Scripts\activate # для Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


#### Фронтенд
bash
cd cm.frontend
npm install
npm run dev


## API Endpoints

### Аутентификация
- POST `/auth/login` - Вход в систему

### Шифрование/Дешифрование
- POST `/encrypt/aes` - Шифрование текста

- POST `/decrypt/aes` - Дешифрование текста

- POST `/encrypt/file` - Шифрование файла

- POST `/decrypt/file` - Дешифрование файла

## Фронтенд компоненты

### Основной компонент (App.vue)

## Логирование
Логи бэкенда сохраняются в файл `app.log`. Для просмотра логов в Docker:
bash
docker-compose logs -f backend


## Безопасность
- Все API-эндпоинты (кроме регистрации и входа) требуют JWT-токен
- Поддерживается CORS
- Безопасное хранение паролей (bcrypt)
- Валидация входных данных

## Известные проблемы
1. Предупреждение bcrypt при регистрации (не влияет на функциональность)
2. Необходимо правильно настроить CORS для продакшена
3. Ошибка при дешифровании файлов: "Data must be aligned to block boundary in ECB mode"

## Рекомендации по развертыванию
1. Измените секретный ключ для JWT
2. Настройте CORS для вашего домена
3. Используйте HTTPS в продакшене
4. Настройте правильные заголовки безопасности