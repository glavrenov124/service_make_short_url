URL Shortener

Описание проекта

Проект представляет собой сервис для сокращения ссылок. Пользователи могут создать короткие ссылки, получить статистику по ним, а также удалять их. Система поддерживает аутентификацию пользователей с использованием JWT-токенов, Redis для кэширования и PostgreSQL в качестве основной базы данных.

API

1. Регистрация пользователя

POST /register

Создание нового пользователя.

Тело запроса:

{
  "email": "example@example.com",
  "password": "password123"
}

Ответ:

{
  "message": "User registered successfully"
}

2. Вход пользователя

POST /login

Получение JWT-токена для аутентифицированного пользователя.

Тело запроса:

{
  "email": "example@example.com",
  "password": "password123"
}

Ответ:

{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}

3. Создание короткой ссылки

POST /links/shorten

Создание короткой ссылки. Для аутентифицированных пользователей будет назначен идентификатор владельца.

Тело запроса:

{
  "original_url": "https://example.com",
  "custom_alias": "example",
  "expires_at": "2025-03-27T12:00:00"
}

Ответ:

{
  "short_code": "123abc",
  "original_url": "https://example.com",
  "custom_alias": "example",
  "created_at": "2025-03-26T12:00:00",
  "expires_at": "2025-03-27T12:00:00"
}

4. Перенаправление на оригинальную ссылку

GET /{short_code}

Перенаправление на оригинальный URL по короткому коду. Если ссылка кэширована в Redis, будет выполнено перенаправление без обращения к базе данных.

Ответ: Перенаправление на оригинальный URL.

5. Удаление короткой ссылки

DELETE /links/{short_code}

Удаление короткой ссылки. Доступно только владельцу ссылки.

Ответ:

{
  "message": "Link deleted successfully"
}

Инструкция по запуску

1. Клонируй репозиторий:

git clone <URL>
cd <project-directory>

2. Установи зависимости:

pip install -r requirements.txt

3. Настрой окружение:

Создай файл .env в корне проекта и добавь следующие переменные:

DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<dbname>
REDIS_URL=redis://localhost:6380
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

4. Запусти сервер:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Сервер будет доступен по адресу: http://localhost:8000.

Описание БД

Проект использует PostgreSQL для хранения данных. Основные таблицы:

Таблица users

id (PK) — уникальный идентификатор пользователя.

email — уникальный email пользователя.

hashed_password — хешированный пароль пользователя.

Таблица links

id (PK) — уникальный идентификатор ссылки.

original_url — оригинальный URL.

short_code — короткий код для ссылки.

custom_alias — пользовательский псевдоним (опционально).

created_at — дата создания.

expires_at — дата истечения срока действия.

owner_id (FK) — идентификатор владельца (ссылается на users).

Используемые технологии

FastAPI — для построения REST API.

PostgreSQL — для хранения данных.

Redis — для кэширования коротких ссылок.

SQLAlchemy — ORM для взаимодействия с базой данных.

JWT — для аутентификации пользователей.

bcrypt — для хеширования паролей.

Лицензия

Этот проект лицензирован под MIT License - см. файл LICENSE для подробностей.

