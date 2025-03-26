# URL Shortener API

API-сервис для сокращения ссылок. Поддерживает регистрацию пользователей, генерацию коротких ссылок, статистику по переходам и управление своими ссылками.

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
Необходимо ввести логин и пароль по кнопе authorize 


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
git clone 
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
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
### 6. Запусти redis

```bash
redis-server
```
Документация будет доступна по адресу:
```
http://0.0.0.0:8000/docs
```

---

## Структура базы данных

### Таблица `users`
Хранит информацию о зарегистрированных пользователях.

| Поле             | Описание                                  |
|-----------------|------------------------------------------|
| `id`           | Уникальный идентификатор пользователя (PK) |
| `email`        | Email пользователя (уникальный)           |
| `hashed_password` | Хешированный пароль                      |

### Таблица `links`
Хранит сокращенные ссылки.

| Поле            | Описание                                  |
|----------------|------------------------------------------|
| `id`          | Уникальный идентификатор ссылки (PK)       |
| `original_url` | Оригинальный URL                          |
| `short_code`  | Короткий код ссылки (уникальный)          |
| `custom_alias` | Пользовательский псевдоним (уникальный, опционально) |
| `created_at`  | Дата создания                              |
| `last_accessed` | Дата последнего использования           |
| `access_count` | Количество переходов по ссылке           |
| `expires_at`  | Дата истечения (если указана)             |
| `owner_id`    | Владелец ссылки (ссылается на `users.id`) |

### Индексы
- `users.email` — уникальный индекс для email пользователей.
- `links.short_code` — уникальный индекс для коротких кодов ссылок.
- `links.custom_alias` — уникальный индекс для пользовательских алиасов.

### Внешние ключи
- `links.owner_id → users.id` — связь ссылок с их владельцами.

