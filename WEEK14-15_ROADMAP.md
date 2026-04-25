# План для Недель 14-15: Мониторинг и Финальная защита

<<<<<<< HEAD
**Статус на апрель 2026:** Недели 1-14 реализованы, неделя 15 подготовлена по сценарию демо.
=======
**Статус на март 2026:** Завершены недели 1-13 (тестирование и нагрузка)
>>>>>>> e47ba85ba22a34943990d6826680058a7a3898f6

---

## Неделя 14: Мониторинг (Prometheus + Grafana)

### Что добавить

1. **Prometheus** — сбор метрик приложения
2. **Grafana** — визуализация метрик
3. **Django middleware** для сбора метрик
4. **Health metrics** для Grafana

### Планы интеграции

#### 1. Добавить prometheus-client в requirements

```bash
pip install prometheus-client
```

#### 2. Создать metrics.py в harvester/

```python
from prometheus_client import Counter, Histogram, Gauge

# Счетчики
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint']
)

# Гистограмма латенси
request_latency = Histogram(
    'request_latency_seconds',
    'Request latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Метрики БД
db_works_count = Gauge('works_total', 'Total works in database')
```

#### 3. Middleware для Django

```python
class PrometheusMiddleware:
    @staticmethod
    def instrument_request(request):
        # Обновляем метрики
        api_requests_total.labels(
            method=request.method,
            endpoint=request.path
        ).inc()
```

#### 4. Обновить docker-compose.yml

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

#### 5. Создать prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'django_app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics/'
```

#### 6. URL для метрик в Django

```python
# config/urls.py
from prometheus_client import generate_latest
from django.http import HttpResponse

def metrics(request):
    return HttpResponse(generate_latest(), content_type='text/plain')

urlpatterns = [
    path('metrics/', metrics),
    # ...
]
```

### Использование

```bash
# Запустить с Prometheus и Grafana
docker compose up -d

# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin:admin)
# Метрики: http://localhost:8000/metrics/
```

---

## Неделя 15: Финальная защита (Demo Day)

### Подготовка к защите

#### Демонстрационная презентация (5-10 минут)

1. **Введение** (1 мин)
   - Название проекта: Scientific Data Harvester
   - Задача: Автоматизированный сбор метаданных научных работ из OpenAlex
   - Команда и роли

2. **Архитектура** (2 мин)
   - Диаграмма компонентов
   - Data Collector → Storage → Processor → API
   - Стек: Django, DRF, PostgreSQL, Docker

3. **Live Demo** (3 мин)
   - Запуск контейнеров
   - Получение JWT токена
   - Демонстрация API:
     - GET /api/works/ (пагинация)
     - Фильтрация по году
     - Поиск по ключевым словам
   - Показать админ-панель с данными

4. **Результаты тестирования** (3 мин)
   - Unit-тесты: > 40% coverage
   - Нагрузочные тесты: 200 VUs, 1000+ RPS
   - GitHub Actions: зеленая галочка при пуше
   - Метрики Grafana (если готово)

5. **Q&A** (1 мин)

#### Файлы для демо

```
Prepare:
- docker-compose.yml    ← для быстрого запуска
- sample_data.sql       ← примеры данных
- screenshots/          ← скриншоты API в Postman
- metrics_dashboard.png ← скриншот Grafana
```

#### Скрипт запуска для демо (demo.sh)

```bash
#!/bin/bash

<<<<<<< HEAD
echo "=== Event Discovery Demo ==="
=======
echo "=== Scientific Data Harvester Demo ==="
>>>>>>> e47ba85ba22a34943990d6826680058a7a3898f6
echo "1. Запуск контейнеров..."
docker compose up -d

echo "2. Создание схемы БД..."
<<<<<<< HEAD
docker compose exec web python manage.py migrate

echo "3. Загрузка примеров данных..."
docker compose exec web python manage.py collect_wikicfp --pages 2 --per-page 50

echo "4. Обработка ключевых слов..."
docker compose exec web python manage.py process_events

echo ""
echo "✅ Демо готово!"
echo "📊 API: http://localhost:8000/api/conferences/"
=======
docker compose exec app python manage.py migrate

echo "3. Загрузка примеров данных..."
docker compose exec app python manage.py collect_openalex --pages 1 --per-page 10

echo "4. Обработка ключевых слов..."
docker compose exec app python manage.py process_works --limit 5

echo ""
echo "✅ Демо готово!"
echo "📊 API: http://localhost:8000/api/works/"
>>>>>>> e47ba85ba22a34943990d6826680058a7a3898f6
echo "🔐 Получить токен: POST http://localhost:8000/api/token/"
echo "📈 Метрики: http://localhost:9090"
echo "🎨 Grafana: http://localhost:3000"
```

### Чек-лист для защиты

**День перед защитой:**
- [ ] Протестировать docker compose up на чистой машине
- [ ] Подготовить учетные данные для входа
- [ ] Записать поэтапно все команды для demo
- [ ] Убедиться что данные в БД есть (50+ работ)
- [ ] Запустить k6 тесты и получить результаты

**В день защиты:**
- [ ] Запустить контейнеры за 5 минут до презентации
- [ ] Открыть API, админку и Grafana в браузере
- [ ] Проверить интернет для оригинального OpenAlex API
- [ ] Иметь заготовку JWT токена для быстрого запроса
- [ ] Показать GitHub репозиторий и коммиты

### Отчеты и артефакты

Представить:

1. **GitHub репозиторий link**
   - Все коммиты видны
   - CI/CD статус зеленый
   - PR history и code reviews

2. **Результаты тестов**
   - `pytest --cov` отчет (htmlcov/index.html)
   - Скриншоты: > 40% coverage

3. **Результаты нагрузочных тестов**
   - `k6 run stress_test.js` вывод
   - Полученный JSON файл
   - Графики RPS и Latency

4. **Логи GitHub Actions**
   - Успешные прогоны при пуше
   - Зеленые check marks

5. **Metrics и Monitoring**
   - Скриншоты Prometheus
   - Grafana дашборд со статистикой

### Примеры отчетов для представления

#### Отчет по производительности

```
Performance Report - Stress Test Results

Duration: 12 minutes
Peak Load: 200 concurrent users
Total Requests: 28,500

Metrics:
  Average Response Time: 245ms
  95th Percentile: 580ms
  99th Percentile: 920ms
  Error Rate: 0.0%
  Requests Per Second: 750 RPS (peak)

Conclusion: System handles production load with 99.9% success rate
```

#### Отчет по покрытию кода

```
Coverage Report

Total Coverage: 42%

By Component:
  - harvester.models: 100%
  - harvester.views: 85%
  - harvester.processor: 95%
  - harvester.serializers: 70%

Tests Run: 42
Passed: 42
Failed: 0
Errors: 0
```

---

## После защиты: CI/CD Polish (Опционально)

### Улучшения для Production

1. **Auto-deployment на VPS**
   ```yaml
   # .github/workflows/deploy.yml
   - Deploy приложения при пуше в main
   ```

2. **Auto-scaling с Docker Swarm/Kubernetes**
   - Horizontal Pod Autoscaler для k8s
   - Service mesh (Istio) для мониторинга

3. **Security scanning**
   - OWASP ZAP
   - Dependabot для обновлений

4. **Rate limiting**
   - django-ratelimit
   - nginx reverse proxy

---

## Финальный чек-лист всего проекта

- [x] Неделя 1-2: GitHub + Docker
- [x] Неделя 3: БД и модели (Work)
- [x] Неделя 4-5: Data Collector (OpenAlex парсер)
- [x] Неделя 6: Data Processor (keywords extraction)
- [x] Неделя 7-8: REST API (GET, фильтрация, поиск)
- [x] Неделя 9: JWT Authentication
- [x] Неделя 10: Unit & Integration тесты + GitHub Actions
- [x] Неделя 11-13: k6 нагрузочные тесты (smoke, stress, soak)
<<<<<<< HEAD
- [x] Неделя 14: Prometheus + Grafana мониторинг
- [~] Неделя 15: Demo Day и защита проекта (нужны финальные скриншоты/артефакты)
=======
- [ ] Неделя 14: Prometheus + Grafana мониторинг
- [ ] Неделя 15: Demo Day и защита проекта
>>>>>>> e47ba85ba22a34943990d6826680058a7a3898f6

---

## Контакты и поддержка

При проблемах с тестированием:
<<<<<<< HEAD
1. Проверить логи: `docker compose logs web`
=======
1. Проверить логи: `docker compose logs app`
>>>>>>> e47ba85ba22a34943990d6826680058a7a3898f6
2. Убедиться что PostgreSQL запущен: `docker ps`
3. Очистить кэш pytest: `pytest --cache-clear`
4. Переустановить зависимости: `pip install -r requirements.txt --force-reinstall`
