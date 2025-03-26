# URL Shortener API

API-сервис для сокращения ссылок. Поддерживает регистрацию пользователей, генерацию коротких ссылок, статистику по переходам и управление своими ссылками.

## Демо


## Описание API

### Аутентификация
- `POST /register` — регистрация пользователя.
- `POST /login` — получение JWT токена.

### Работа со ссылками
- `POST /links/shorten` — создание короткой ссылки.
- `GET /{short_code}` — переход по короткой ссылке.
- `GET /links/{short_code}/stats` — получение статистики по ссылке.
- `PUT /links/{short_code}` — обновление оригинального URL.
- `DELETE /links/{short_code}` — удаление ссылки.
- `GET /links/search` — поиск ссылки по оригинальному URL.
- `GET /links/expired` — просмотр всех истёкших ссылок.
- `DELETE /links/cleanup` — удаление истекших ссылок

### Авторизация
Для защищённых эндпоинтов используется JWT токен (Bearer).
Полученный токен необходимо указать в Swagger UI через кнопку "Authorize" или передавать в заголовке:

```
Authorization: Bearer <your_token>
```

---

## Примеры запросов

### Регистрация пользователя
```json
POST /register
{
  "email": "example@example.com",
  "password": "1234"
}
```

### Логин
```json
POST /login
username: example@example.com
password: 1234
```

### Создание ссылки
```json
POST /links/shorten
{
  "original_url": "https://example.com/",
  "custom_alias": "string",
  "expires_at": "2025-03-27T13:56:31"
}
```

---

## Инструкция по запуску локально

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/url-shortener.git
cd url-shortener
```

### 2. Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # или Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настройка окружения

Создайте `.env` файл в корне и укажите:

```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

### 4. Инициализация БД
```bash
alembic upgrade head
```

### 5. Запуск приложения
```bash
uvicorn app.main:app --reload
```

Документация будет доступна по адресу:
```
http://127.0.0.1:8000/docs
```

---

## Структура базы данных

## Структура базы данных

### Таблица `users`
Хранит информацию о зарегистрированных пользователях.

| Поле            | Тип          | Описание                     |
|----------------|-------------|------------------------------|
| `id`          | `SERIAL` (PK) | Уникальный идентификатор пользователя |
| `email`       | `VARCHAR(255) UNIQUE NOT NULL` | Email пользователя |
| `hashed_password` | `TEXT NOT NULL` | Хешированный пароль |

### Таблица `links`
Хранит сокращенные ссылки.

| Поле            | Тип          | Описание                     |
|----------------|-------------|------------------------------|
| `id`          | `SERIAL` (PK) | Уникальный идентификатор ссылки |
| `original_url` | `TEXT NOT NULL` | Оригинальный URL |
| `short_code`  | `VARCHAR(20) UNIQUE NOT NULL` | Короткий код ссылки |
| `custom_alias` | `VARCHAR(50) UNIQUE` | Пользовательский псевдоним (опционально) |
| `created_at`  | `TIMESTAMP DEFAULT NOW()` | Дата создания |
| `expires_at`  | `TIMESTAMP` | Дата истечения (если указана) |
| `owner_id`    | `INTEGER` (FK) | Владелец ссылки (если зарегистрирован) |

### Индексы
- `users.email` — уникальный индекс для email пользователей.
- `links.short_code` — уникальный индекс для коротких кодов ссылок.
- `links.custom_alias` — уникальный индекс для пользовательских алиасов.

### Внешние ключи
- `links.owner_id → users.id` — связь ссылок с их владельцами.
