# Scientific Data Harvester (Django)

Командный проект Advanced Backend & DevOps. Микросервис сбора и анализа метаданных научных публикаций (OpenAlex).

Репозиторий: [Event-Discovery-Service-Backend-Develop/skyscraper](https://github.com/Event-Discovery-Service-Backend-Develop/skyscraper)

## Стек

Django 5, DRF, JWT (Simple JWT), PostgreSQL, Docker.

## Запуск

```bash
docker compose up --build -d
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
docker compose exec app python manage.py collect_openalex --pages 2 --per-page 50
docker compose exec app python manage.py process_works
```

Локально: `bash run.sh` (sdelat migracii i zapustit server). Ili vruchnuyu:
  .venv/bin/python manage.py migrate
  .venv/bin/python manage.py runserver
По umolchaniyu ispolzuetsya SQLite (bez PostgreSQL).

## Команды

- `collect_openalex --pages 2 --per-page 50 --delay 1` — сбор с OpenAlex (user-agent, задержка, обработка ошибок)
- `process_works [--limit N]` — заполнение keywords из raw_json

## Эндпоинты

- GET / — статус
- GET /health/ — healthcheck
- POST /api/token/ — выдать JWT (body: username, password)
- POST /api/token/refresh/ — обновить токен (body: refresh)
- GET /api/works/ — список работ (нужен заголовок Authorization: Bearer <access>), фильтры: ?year=2024&search=... 
- GET /admin/ — админка
