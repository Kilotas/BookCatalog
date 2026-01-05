Описание проекта

Library Catalog API — это асинхронный REST API сервис для управления библиотечным каталогом.
Проект реализован с использованием современной архитектуры, разделенной на независимые слои:

API Layer — обработка HTTP запросов

Domain Layer — бизнес-логика

Data Layer — работа с базой данных

External Layer — взаимодействие с внешними API (OpenLibrary)

Сервис поддерживает:

CRUD операции над книгами

Поиск, фильтрацию, сортировку

Пагинацию

Обогащение данных из Open Library

Хранение данных в PostgreSQL

Корректную обработку ошибок

Асинхронную работу на SQLAlchemy 2.0

Проект полностью типизирован, использует Pydantic v2, настроенный DI и логирование.

Архитектура проекта

Проект построен на принципах многослойной архитектуры (4-tier architecture):


┌───────────────────────────┐
│  API Layer (FastAPI)      │  ← роутеры, схемы, HTTP
└──────────────┬────────────┘
               │ вызывает
┌──────────────▼────────────┐
│ Domain Layer (Services)    │  ← бизнес-логика, правила
└──────────────┬────────────┘
               │ использует
┌──────────────▼────────────┐
│ Data Layer (Repository)    │  ← CRUD, SQL запросы
└──────────────┬────────────┘
               │ использует
┌──────────────▼────────────┐
│ External Layer (Clients)   │  ← OpenLibrary API
└────────────────────────────┘


Принципы:

✔ Разделение ответственности
✔ Чистая архитектура
✔ Тонкие роутеры — толстые сервисы
✔ Никакой бизнес-логики в API
✔ Репозитории только для работы с БД
✔ Клиенты только для HTTP запросов

library_catalog/
│
├── README.md
├── pyproject.toml
├── .env.example
├── docker-compose.yml
├── alembic.ini
│
├── src/
│   └── library_catalog/
│       ├── main.py
│       │
│       ├── api/
│       │   ├── dependencies.py
│       │   └── v1/
│       │       ├── routers/
│       │       │   ├── books.py
│       │       │   └── health.py
│       │       └── schemas/
│       │           ├── book.py
│       │           └── common.py
│       │
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── logging_config.py
│       │   └── exceptions.py
│       │
│       ├── data/
│       │   ├── models/book.py
│       │   └── repositories/
│       │       ├── base_repository.py
│       │       └── book_repository.py
│       │
│       ├── domain/
│       │   ├── services/book_service.py
│       │   ├── exceptions.py
│       │   └── mappers/book_mapper.py
│       │
│       └── external/
│           ├── base/base_client.py
│           └── openlibrary/
│               ├── client.py
│               └── schemas.py
│
└── tests/

| Компонент          | Технология | Версия | Назначение               |
| ------------------ | ---------- | ------ | ------------------------ |
| Backend Framework  | FastAPI    | 0.109+ | Основной web-фреймворк   |
| ASGI Server        | Uvicorn    | 0.27+  | Запуск API               |
| ORM                | SQLAlchemy | 2.0+   | Async ORM                |
| DB                 | PostgreSQL | 15/16  | Хранение данных          |
| Migrations         | Alembic    | 1.13+  | Версионирование схемы    |
| Validation         | Pydantic   | 2.5+   | Типизация и валидация    |
| HTTP Client        | httpx      | 0.26+  | Асинхронные запросы      |
| Dependency Manager | Poetry     | Latest | Управление зависимостями |

Установка и запуск

Установка зависимостей
poetry install


Настроить окружение
cp .env.example .env


DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/library
OPENLIBRARY_BASE_URL=https://openlibrary.org

Запуск PostgreSQL (Docker)

docker-compose up -d

Применить миграции

alembic upgrade head

Запуск приложения

poetry run uvicorn src.library_catalog.main:app --reload





