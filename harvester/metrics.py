try:
    from prometheus_client import Counter, Histogram, Gauge  # type: ignore
except ImportError:  # pragma: no cover
    # Заглушки на случай, если библиотека prometheus_client не установлена
    class _NoopMetric:
        def labels(self, **kwargs):
            return self

        def inc(self, value=1):
            return None

        def observe(self, value):
            return None

        def set(self, value):
            return None

    def Counter(*args, **kwargs):  # type: ignore
        return _NoopMetric()

    def Histogram(*args, **kwargs):  # type: ignore
        return _NoopMetric()

    def Gauge(*args, **kwargs):  # type: ignore
        return _NoopMetric()

# Счетчики API запросов
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# Гистограмма латенси запросов
request_latency = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Метрики БД
conferences_total = Gauge('conferences_total', 'Total conferences in database')
processed_conferences = Gauge('processed_conferences_total', 'Total processed conferences')

# Метрики Celery задач
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'state']
)