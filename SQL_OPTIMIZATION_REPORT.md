# SQL Optimization Report (Week 10)

Цель: уменьшить время ответа API при фильтрации/сортировке и повысить стабильность под нагрузкой.

## Что оптимизировано

### 1) Индексы под реальные запросы API
Добавлены индексы в `Conference`:
- `conf_proc_event_idx` на `("is_processed", "-event_date")`
- `conf_event_id_idx` на `("-event_date", "-id")`
- `conf_deadline_proc_idx` на `("deadline", "is_processed")`

Файлы:
- `harvester/models.py`
- `harvester/migrations/0006_conference_performance_indexes.py`

### 2) Full-text для PostgreSQL
В API-поиске используется `SearchVector + SearchRank` для PostgreSQL, с fallback на `icontains` для SQLite.

Файл:
- `harvester/views.py`

## Как проверить (EXPLAIN ANALYZE)

После миграций:
```bash
docker compose exec web python manage.py migrate
```

Подключиться к PostgreSQL:
```bash
docker compose exec db psql -U postgres -d skyscraper
```

Проверка сортировки списка:
```sql
EXPLAIN ANALYZE
SELECT id, title, event_date
FROM conferences
ORDER BY event_date DESC, id DESC
LIMIT 20;
```

Проверка фильтра обработанных:
```sql
EXPLAIN ANALYZE
SELECT id, title, event_date
FROM conferences
WHERE is_processed = true
ORDER BY event_date DESC
LIMIT 20;
```

Проверка дедлайнов:
```sql
EXPLAIN ANALYZE
SELECT id, title, deadline
FROM conferences
WHERE is_processed = false
  AND deadline IS NOT NULL
ORDER BY deadline ASC
LIMIT 20;
```

## Ожидаемый результат
- Для частых API-запросов планировщик выбирает `Index Scan`/`Bitmap Index Scan`.
- Меньше чтения с диска и ниже latency на пагинации/сортировке.
- Более стабильный p95/p99 на k6-сценариях.

## Примечание
Для больших объемов данных рекомендуется:
- регулярный `VACUUM ANALYZE`,
- контроль bloat индексов,
- периодическая ревизия индексов на основе `pg_stat_statements`.
