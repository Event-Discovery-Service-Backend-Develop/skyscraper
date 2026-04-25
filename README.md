<<<<<<< HEAD
# Event Discovery Service

Командный проект курса Advanced Backend & DevOps.  
Сервис собирает данные научных конференций из WikiCFP, сохраняет в БД и отдает через REST API.

## Командные роли
- Backend Dev: API, авторизация, бизнес-логика, веб-страницы.
- Data Engineer: парсер, очистка/нормализация данных, контроль качества.
- DevOps: Docker, CI/CD, мониторинг, production-профиль.

## Технологии
- Django 5, DRF, Simple JWT
- PostgreSQL / SQLite
- Celery + Redis
- Docker / Docker Compose
- Prometheus + Grafana
- Pytest + k6

## Быстрый запуск (Docker, dev)
```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collect_wikicfp --pages 2 --per-page 50
docker compose exec web python manage.py process_events
curl http://localhost:8000/health/
```

## Запуск production-профиля
```bash
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## Demo Day (готовый сценарий)
```bash
bash demo.sh
```

## Доступные URL
- Главная: `http://localhost:8000/`
- API: `http://localhost:8000/api/conferences/` (alias: `/api/works/`)
- Swagger: `http://localhost:8000/api/schema/swagger-ui/`
- Метрики: `http://localhost:8000/metrics/`
- Prometheus: `http://localhost:9090/`
- Grafana: `http://localhost:3000/` (`admin/admin` по умолчанию)

## Основные команды
```bash
# Сбор конференций (антиблокировка + опциональный proxy)
python manage.py collect_wikicfp --pages 2 --per-page 50 --delay-min 0.8 --delay-max 2.5 --proxy http://user:pass@host:port

# Обработка сырых данных
python manage.py process_events

# Тесты
pytest
pytest --cov=harvester --cov-report=html

# Нагрузочные тесты
cd load-tests && k6 run smoke_test.js
```

## REST API

### Публичные
- `GET /`
- `GET /health/`

### JWT
- `POST /api/token/`
- `POST /api/token/refresh/`

Пример:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_password"}'
```

### Защищенные
- `GET /api/conferences/` (alias: `/api/works/`)
- `GET /admin/`

Параметры:
- `page`, `page_size`
- `search`
- `year`
- `tag`
- `processed`
- `ordering`

## Monitoring
- Prometheus scrape: `prometheus.yml`
- Grafana datasource provisioning: `grafana/provisioning/datasources/datasource.yml`
- Grafana dashboard provisioning: `grafana/provisioning/dashboards/dashboard.yml`
- Готовый dashboard: `grafana/dashboards/skyscraper-overview.json`

## CI/CD
GitHub Actions в `.github/workflows/`:
- запуск тестов и coverage
- lint
- сборка Docker-образа

## Переменные окружения
Скопируй `.env.example` в `.env` и при необходимости настрой:
- `USE_POSTGRES`, `DATABASE_URL`
- `WIKICFP_PROXY_URL` (опционально)
- `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`

## Соответствие этапам проекта
Актуальный аудит по неделям 1-15 находится в `PROJECT_WEEKLY_AUDIT.md`.

## Финальная защита (Week 15)
- План и чеклист: `DEFENSE_DAY_PACKAGE.md`
- Папка скриншотов: `artifacts/screenshots/`
- Папка отчетов: `artifacts/reports/`
=======
Event Discovery Service

Командный проект курса Advanced Backend & DevOps.

Сервис для сбора, хранения и анализа метаданных научных конференций из внешнего источника WikiCFP.

Проект собирает научные конференции, сохраняет их в базе данных и предоставляет доступ к ним через REST API.

Технологический стек

Django 5

Django REST Framework

JWT Authentication (Simple JWT)

PostgreSQL / SQLite

Docker

Pytest

k6 (нагрузочное тестирование)

Запуск проекта
Запуск через Docker
docker compose up --build -d
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
docker compose exec app python manage.py collect_wikicfp --pages 2 --per-page 50
docker compose exec app python manage.py process_events

После запуска сервис доступен:

http://localhost:8000
API Документация (Swagger): http://localhost:8000/api/schema/swagger-ui/
Метрики Prometheus: http://localhost:8000/metrics/
Локальный запуск (режим разработки)

Используется для разработки и тестирования проекта без Docker.

python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
Основные команды проекта
Сбор данных из WikiCFP
python manage.py collect_wikicfp --pages 2 --per-page 50 --delay 1

Команда получает данные из WikiCFP и сохраняет их в базе данных.

Обработка данных
python manage.py process_events

Извлекает ключевые слова и нормализует данные конференции.

Миграции базы данных
python manage.py migrate
Создание администратора
python manage.py createsuperuser
API Endpoints
Публичные эндпоинты
GET /
GET /health/
Аутентификация
POST /api/token/
POST /api/token/refresh/

Получение JWT токена:

curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_user", "password": "your_password"}'
Защищенные эндпоинты
GET /api/works/
GET /admin/

Эндпоинт /api/works/ поддерживает:

пагинацию

поиск

фильтрацию

сортировку

Параметры API
параметр	описание
page	номер страницы
page_size	количество элементов
publication_year	фильтр по году
search	поиск по названию
ordering	сортировка

Примеры запросов:

GET /api/works/?page=1&page_size=5
GET /api/works/?publication_year=2024
GET /api/works/?search=machine+learning
GET /api/works/?ordering=-publication_year
Тестирование

Установка зависимостей:

pip install -r requirements.txt

Запуск тестов:

pytest

Покрытие кода:

pytest --cov=harvester --cov-report=html

Целевое покрытие:

> 40%
Нагрузочное тестирование

Для нагрузочного тестирования используется k6.

Пример запуска:

cd load-tests
k6 run smoke_test.js

Тесты измеряют:

RPS (requests per second)

latency

error rate

CI/CD

Проект использует GitHub Actions.

## Pipeline выполняет:

запуск тестов (pytest)

проверку стиля (flake8)

сборку Docker образа

## Конфигурация:

.github/workflows/
## Структура проекта
skyscraper/
│
├── config/                 # Django конфигурация
│   ├── settings.py
│   ├── urls.py
│   └── templates/
│
├── harvester/              # Основное приложение
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── processor.py
│   ├── tests.py
│   └── management/commands/
│       ├── collect_wikicfp.py
│       └── process_events.py
│
├── load-tests/             # нагрузочные тесты
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── conftest.py
└── README.md
Переменные окружения

## Создайте файл .env:

DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

USE_POSTGRES=0
DATABASE_URL=postgresql://harvester:secret@db:5432/harvester_db

## ER Diagram
+----------------------------+
|       Conference           |
+----------------------------+
| id (PK)                    |
| wikicfp_id (unique)        |
| title                      |
| event_date                 |
| location                   |
| deadline                   |
| url                        |
| raw_html                   |
| clean_description          |
| keywords                   |
| is_processed               |
| created_at                 |
| updated_at                 |
+----------------------------+

## Monitoring
Prometheus: http://localhost:9090
Grafana: http://localhost:3000 (admin/admin)

MIT
>>>>>>> e47ba85ba22a34943990d6826680058a7a3898f6
