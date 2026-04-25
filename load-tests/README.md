# Нагрузочное тестирование с k6

Здесь находятся скрипты для нагрузочного тестирования API с помощью **k6**.

## Установка k6

### На Windows (через Chocolatey):
```bash
choco install k6
```

### На macOS (через Homebrew):
```bash
brew install k6
```

### На Linux (Ubuntu/Debian):
```bash
sudo apt-get install k6
```

Или скачать с https://k6.io/docs/getting-started/installation/

## Запуск тестов

### 1. Убедитесь что сервер запущен
Docker:
```bash
docker compose up -d
docker compose exec web python manage.py migrate
```

Локально:
```bash
python manage.py migrate
python manage.py runserver
```

### 2. Создайте тестового пользователя
```bash
python manage.py createsuperuser --username testuser --email test@test.com  
# или используйте существующего с паролем testpass12345
```

### 3. Запустите дымовой тест (базовая проверка)
```bash
k6 run smoke_test.js
```

Или с кастомными параметрами:
```bash
BASE_URL=http://localhost:8000 USERNAME=testuser PASSWORD=testpass12345 k6 run smoke_test.js
```

### 4. Запустите стресс-тест (высокая нагрузка)
```bash
k6 run stress_test.js
```

Этот тест рамп-ит нагрузку до 200 конкурентных юзеров.

### 5. Запустите soak-тест (долгая нагрузка)
```bash
k6 run soak_test.js
```

Этот тест проверяет стабильность при долгой работе.

## Интерпретация результатов

После каждого теста k6 выводит результаты:

- **http_req_duration**: время ответа от сервера (нам нужно p95 < 1000ms)
- **http_reqs**: общее количество произведенных запросов
- **http_req_failed**: количество ошибок (5xx, таймауты, и т.д.)

Пример нормального вывода:
```
     data_received..................: 2.5 MB   12 kB/s
     data_sent........................: 1.3 MB    6 kB/s
     http_req_duration................: avg=245ms   min=54ms    med=189ms   max=1.2s    p(90)=523ms   p(95)=621ms
     http_req_failed..................: 0.00%    ✓ 0 out of 2850
     http_reqs........................: 2850     14.246/s
```

## Сохранение результатов в JSON

По умолчанию stress_test.js сохраняет результаты в `stress_test_results.json`.

Для других тестов:
```bash
k6 run stress_test.js --out json=results.json
k6 run smoke_test.js --out json=results.json
```

Потом можно анализировать результаты:
```bash
python3 analyze_k6_results.py results.json
```

## Базовые метрики для отчета

Когда будете создавать отчет, обратите внимание на:

1. **RPS (Requests Per Second)**: сколько запросов в секунду пережил сервер
2. **Average Latency**: среднее время ответа
3. **p95 Latency**: 95-й процентиль времени ответа
4. **p99 Latency**: 99-й процентиль  
5. **Error Rate**: процент ошибок
6. **Total Requests**: всего запросов за тест
7. **Total Duration**: продолжительность теста

## Примеры сценариев

### Быстрый check перед комитом
```bash
k6 run smoke_test.js
```

### Проверка перед продакшн-релизом
```bash
k6 run smoke_test.js && k6 run stress_test.js
```

### Поиск узких мест
```bash
k6 run stress_test.js --vus 150 --duration 5m
```

## Troubleshooting

**"Connection refused"** - сервер не запущен, проверьте `http://localhost:8000/health/`

**"Unauthorized"** - неправильное имя пользователя/пароль, проверьте переменные окружения

**"Too many connections"** - k6 открывает много соединений, может быть ограничение ОС, используйте меньше VUs или увеличьте лимит
