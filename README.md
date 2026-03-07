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

Локально: `bash run.sh` (создает venv, миграции и запускает сервер).

Или вручную:
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

По умолчанию используется SQLite (без PostgreSQL). Для использования PostgreSQL задайте `USE_POSTGRES=1` в `.env`.

## Команды управления

- `python manage.py collect_openalex --pages 2 --per-page 50 --delay 1` — сбор с OpenAlex (user-agent, задержка, обработка ошибок)
- `python manage.py process_works [--limit N]` — заполнение keywords из raw_json
- `python manage.py migrate` — применение миграций БД
- `python manage.py createsuperuser` — создание администратора

## API Эндпоинты

### Публичные
- `GET /` — главная страница
- `GET /health/` — проверка здоровья сервис

### Аутентификация
- `POST /api/token/` — получить JWT токен
- `POST /api/token/refresh/` — обновить токен

### Защищенные (требуют JWT)
- `GET /api/works/` — список научных работ (пагинация, фильтрация, поиск)
- `GET /admin/` — панель администратора

## Аутентификация

API защищен JWT (JSON Web Tokens).

### Получение токена

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_user", "password": "your_password"}'
```

Ответ:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLC...",
  "access": "eyJ0eXAiOiJKV1QiLC..."
}
```

### Использование токена

```bash
curl http://localhost:8000/api/works/ \
  -H "Authorization: Bearer <access_token>"
```

## Пагинация и фильтрация

### Параметры запроса

- `page` — номер страницы (default: 1)
- `page_size` — элементов на странице (default: 10, max: 100)
- `publication_year` — фильтр по году публикации
- `search` — поиск по названию и ключевым словам
- `ordering` — сортировка (-publication_year, -created_at)

### Примеры

```bash
# Первая страница, 5 элементов
GET /api/works/?page=1&page_size=5

# Работы 2024 года
GET /api/works/?publication_year=2024

# Поиск по названию
GET /api/works/?search=machine+learning

# Сортировка по году убывающая
GET /api/works/?ordering=-publication_year
```

## Тестирование

### Unit и интеграционные тесты

Установите зависимости:
```bash
pip install -r requirements.txt
```

Запустите тесты:
```bash
pytest
```

С покрытием кода:
```bash
pytest --cov=harvester --cov-report=html
```

Откройте `htmlcov/index.html` для просмотра отчета о покрытии.

**Целевое покрытие: > 40%**

Список тестов:
- `harvester/tests.py` — unit-тесты моделей и процессора
- Интеграционные тесты API с JWT
- Тесты пагинации, фильтрации и поиска

### Нагрузочное тестирование (k6)

Перейдите в папку `load-tests`:
```bash
cd load-tests
```

**Требование: установлена k6** (см. `load-tests/README.md`)

#### Дымовой тест (базовая проверка)
```bash
k6 run smoke_test.js
```

#### Стресс-тест (высокая нагрузка до 200 VUs)
```bash
k6 run stress_test.js
```

#### Soak-тест (долгая нагрузка, поиск утечек памяти)
```bash
k6 run soak_test.js
```

Результаты тестов содержат:
- **RPS** — запросов в секунду
- **Avg Latency** — среднее время ответа
- **p95/p99 Latency** — 95-й и 99-й процентили времени ответа
- **Error Rate** — процент ошибок

## CI/CD

Проект использует GitHub Actions для автоматизации:

1. **На каждый push**: `pytest` + `flake8` + сборка Docker
2. **На каждый PR**: тесты и coverage

Лог действий: `.github/workflows/`

## Структура проекта

```
skyscraper/
├── config/              # Django конфиг
│   ├── settings.py     # Основные параметры
│   ├── urls.py         # Маршруты
│   └── templates/      # HTML шаблоны
├── harvester/          # Основное приложение
│   ├── models.py       # ORM модели
│   ├── views.py        # REST API views
│   ├── serializers.py  # DRF serializers
│   ├── processor.py    # Обработка данных
│   ├── tests.py        # Тесты
│   └── management/commands/
│       ├── collect_openalex.py
│       └── process_works.py
├── load-tests/         # k6 скрипты для нагрузки
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── conftest.py
└── README.md
```

## Переменные окружения

Создайте `.env` файл (или используйте `.env.example`):

```dotenv
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# PostgreSQL
USE_POSTGRES=0
DATABASE_URL=postgresql://harvester:secret@db:5432/harvester_db

# OpenAlex API
OPENALEX_BASE_URL=https://api.openalex.org
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
Установите зависимости: `pip install -r requirements.txt`

### API возвращает 401 Unauthorized
Убедитесь что вы отправляете корректный JWT токен в заголовке `Authorization: Bearer <token>`

### Docker контейнер падает при старте
Проверьте логи: `docker compose logs app`

### pytest не находит тесты
Обновите конфиг: `pytest --collect-only`

## Лицензия

MIT