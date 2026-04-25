# Defense Day Package (Week 15)

Этот документ нужен для финальной защиты: что показать, в каком порядке и какие артефакты приложить.

## 1) Структура артефактов

Сложите материалы в эти папки:

- `artifacts/screenshots/`
  - `01_home.png`
  - `02_swagger.png`
  - `03_api_auth.png`
  - `04_api_filters.png`
  - `05_grafana_dashboard.png`
  - `06_prometheus_targets.png`
  - `07_ci_green_pipeline.png`
- `artifacts/reports/`
  - `k6_stress_results.json`
  - `k6_stress_report.json`
  - `coverage_summary.txt`
  - `performance_summary.md`

## 2) Сценарий демо (5-10 минут)

1. Коротко про цель проекта и источник данных (WikiCFP).
2. Запуск `bash demo.sh`.
3. Проверка `GET /health/`.
4. Показ Swagger и защищенных эндпоинтов.
5. Получение JWT и запрос к защищенному API.
6. Показ наполненной БД в admin.
7. Показ Grafana и Prometheus.
8. Краткие выводы по нагрузке (RPS, latency, error rate).

## 3) Чеклист перед выступлением

- [ ] `docker compose up -d` проходит на чистом окружении.
- [ ] `docker compose exec web python manage.py migrate` успешно.
- [ ] В базе есть минимум 50 записей.
- [ ] Работают URL: `/`, `/health/`, `/api/conferences/`, `/api/schema/swagger-ui/`, `/metrics/`.
- [ ] Prometheus и Grafana доступны.
- [ ] Есть готовый JWT токен для быстрого показа.
- [ ] Есть скриншоты и отчеты в `artifacts/`.

## 4) Что показывать в отчете

- Архитектура: Collector -> Processing -> DB -> API -> Monitoring.
- Безопасность: JWT и секреты через `.env`.
- Качество: тесты + coverage.
- Производительность: k6 результаты.
- Наблюдаемость: dashboard и метрики.
