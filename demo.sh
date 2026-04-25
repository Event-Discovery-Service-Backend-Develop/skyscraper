#!/usr/bin/env bash

set -euo pipefail

echo "=== Event Discovery Demo ==="
echo "1) Запускаем контейнеры..."
docker compose up -d --build

echo "2) Применяем миграции..."
docker compose exec web python manage.py migrate

echo "3) Собираем данные (минимум 50 записей)..."
docker compose exec web python manage.py collect_wikicfp --pages 2 --per-page 50
docker compose exec web python manage.py process_events

echo "4) Проверяем состояние сервиса..."
curl -fsS http://localhost:8000/health/ && echo

echo "5) Точки входа:"
echo "   Web:        http://localhost:8000/"
echo "   API:        http://localhost:8000/api/conferences/"
echo "   Swagger:    http://localhost:8000/api/schema/swagger-ui/"
echo "   Prometheus: http://localhost:9090/"
echo "   Grafana:    http://localhost:3000/  (admin/admin)"

echo "✅ Демо-сценарий готов."
