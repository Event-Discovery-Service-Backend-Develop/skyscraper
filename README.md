Scientific Data Harvester

Командный проект курса Advanced Backend & DevOps.

Сервис для сбора, хранения и анализа метаданных научных публикаций из внешнего источника OpenAlex API.

Проект собирает научные публикации, сохраняет их в базе данных и предоставляет доступ к ним через REST API.

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
docker compose exec app python manage.py collect_openalex --pages 2 --per-page 50
docker compose exec app python manage.py process_works

После запуска сервис доступен:

http://localhost:8000
Локальный запуск (режим разработки)

Используется для разработки и тестирования проекта без Docker.

python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
Основные команды проекта
Сбор данных из OpenAlex
python manage.py collect_openalex --pages 2 --per-page 50 --delay 1

Команда получает данные из OpenAlex API и сохраняет их в базе данных.

Обработка данных
python manage.py process_works

Извлекает ключевые слова из raw_json и сохраняет их в поле keywords.

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
│       ├── collect_openalex.py
│       └── process_works.py
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

OPENALEX_BASE_URL=https://api.openalex.org
## ER Diagram
+----------------------+
|        Work          |
+----------------------+
| id (PK)              |
| openalex_id (unique) |
| title                |
| doi                  |
| publication_year     |
| raw_json             |
| keywords             |
| created_at           |
+----------------------+
## License

MIT