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