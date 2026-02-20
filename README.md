# 🐦 Corporate Microblog

Бэкенд корпоративного сервиса микроблогов — упрощённый аналог Twitter для внутреннего использования.

---

## 📋 Содержание

- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [Переменные окружения](#-переменные-окружения)
- [API документация](#-api-документация)
- [Эндпоинты](#-эндпоинты)
- [Аутентификация](#-аутентификация)
- [Запуск тестов](#-запуск-тестов)

---

## ✨ Возможности

- 📝 Создание и удаление твитов
- 🖼️ Загрузка изображений к твитам
- ❤️ Лайки на твиты
- 👥 Подписка на других пользователей
- 📰 Персональная лента из твитов подписок, отсортированная по популярности
- 👤 Просмотр профилей пользователей
- 📖 Swagger UI документация

---

## 🛠 Технологии

| Технология | Назначение |
|---|---|
| **FastAPI** | Асинхронный веб-фреймворк |
| **SQLAlchemy 2.0** | ORM (async) |
| **PostgreSQL** | База данных |
| **asyncpg** | Async-драйвер PostgreSQL |
| **Pydantic v2** | Валидация данных |
| **Uvicorn** | ASGI-сервер |
| **Nginx** | Раздача статики и проксирование |
| **Docker / Docker Compose** | Контейнеризация |
| **pytest + httpx** | Тестирование |

---

## 📁 Структура проекта

```
twit_clone/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tweets.py       # Эндпоинты твитов
│   │   │   ├── users.py        # Эндпоинты пользователей
│   │   │   ├── likes.py        # Эндпоинты лайков
│   │   │   ├── follows.py      # Эндпоинты подписок
│   │   │   └── medias.py       # Эндпоинты загрузки медиа
│   │   ├── deps.py             # Зависимости (авторизация)
│   │   └── router.py           # Сборка роутеров
│   ├── core/
│   │   └── database.py         # Настройка БД
│   ├── models/                 # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── tweet.py
│   │   ├── like.py
│   │   ├── follow.py
│   │   └── media.py
│   ├── schemas/                # Pydantic схемы
│   │   ├── tweet.py
│   │   ├── user.py
│   │   ├── media.py
│   │   ├── error.py
│   │   └── response.py
│   └── main.py                 # Точка входа, lifespan
├── tests/
│   ├── conftest.py             # Фикстуры
│   ├── test_tweets.py
│   ├── test_users.py
│   ├── test_likes.py
│   ├── test_follows.py
│   └── test_feed_following.py
├── nginx/
│   └── default.conf            # Конфиг nginx
├── frontend/
│   └── dist/                   # Готовый билд фронтенда
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

## 🚀 Быстрый старт

### Требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd twit_clone
```

### 2. Создать файл `.env`

```bash
cp .env.example .env
```

Или создать вручную (см. раздел [Переменные окружения](#-переменные-окружения)).

### 3. Запустить приложение

```bash
docker-compose up --build
```

После запуска:

| Адрес | Описание |
|---|---|
| `http://localhost/` | Фронтенд приложения |
| `http://localhost/docs` | Swagger UI документация |
| `http://localhost/redoc` | ReDoc документация |
| `http://localhost/api/...` | API эндпоинты |

### 4. Тестовые пользователи

При первом запуске автоматически создаются два пользователя:

| Имя | API-ключ |
|---|---|
| Test | `test` |
| Admin | `admin` |

---

## ⚙️ Переменные окружения

Создайте файл `.env` в корне проекта:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=microblog

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/microblog
```

---

## 📖 API документация

Swagger UI доступен по адресу `http://localhost/docs` после запуска приложения.

---

## 🔌 Эндпоинты

### Твиты

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/tweets` | Создать твит |
| `DELETE` | `/api/tweets/{id}` | Удалить свой твит |
| `GET` | `/api/tweets` | Получить ленту твитов |

### Медиа

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/medias` | Загрузить изображение |

### Лайки

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/tweets/{id}/likes` | Поставить лайк |
| `DELETE` | `/api/tweets/{id}/likes` | Убрать лайк |

### Подписки

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/users/{id}/follow` | Подписаться на пользователя |
| `DELETE` | `/api/users/{id}/follow` | Отписаться от пользователя |

### Пользователи

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/users/me` | Получить свой профиль |
| `GET` | `/api/users/{id}` | Получить профиль по id |

### Формат ответов

**Успех:**
```json
{
  "result": true,
  ...
}
```

**Ошибка:**
```json
{
  "result": false,
  "error_type": "string",
  "error_message": "string"
}
```

---

## 🔐 Аутентификация

Сервис использует аутентификацию по API-ключу через HTTP-заголовок `api-key`.

Все защищённые эндпоинты ожидают заголовок:

```
api-key: <ваш-ключ>
```

Регистрация пользователей не предусмотрена — это корпоративный сервис, пользователи управляются отдельно.

---

## 🧪 Запуск тестов

Тесты используют SQLite in-memory базу данных и не требуют запущенного Docker.

### Установить зависимости

```bash
pip install -r requirements.txt
```

### Запустить все тесты

```bash
pytest
```

### Запустить с подробным выводом

```bash
pytest -v
```

### Запустить конкретный файл

```bash
pytest tests/test_tweets.py
```
