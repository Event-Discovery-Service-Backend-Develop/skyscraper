import os
import importlib.util
from datetime import timedelta
from urllib.parse import urlparse
from celery.schedules import crontab

try:
    import environ  # type: ignore
except ImportError:
    environ = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Вспомогательные функции для работы без библиотеки django-environ
def _fallback_env(name: str, default=None):
    return os.environ.get(name, default)

def _fallback_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None: return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

def _fallback_list(name: str, default=None):
    if default is None: default = []
    value = os.environ.get(name)
    if not value: return default
    return [item.strip() for item in value.split(",") if item.strip()]

def _fallback_db(name: str):
    url = os.environ.get(name)
    if not url: raise ValueError(f"{name} is not set")
    parsed = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": (parsed.path or "/")[1:],
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "localhost",
        "PORT": parsed.port or 5432,
    }

# Инициализация настроек окружения
if environ is not None:
    env = environ.Env(DEBUG=(bool, False))
    if os.path.exists(ENV_PATH):
        environ.Env.read_env(ENV_PATH)
else:
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line: continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
    
    class _EnvAdapter:
        def __call__(self, name: str, default=None): return _fallback_env(name, default)
        @staticmethod
        def bool(name: str, default: bool = False): return _fallback_bool(name, default)
        @staticmethod
        def list(name: str, default=None): return _fallback_list(name, default)
        @staticmethod
        def db(name: str): return _fallback_db(name)
    env = _EnvAdapter()

SECRET_KEY = env("SECRET_KEY", default="change-me-in-production")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web', '0.0.0.0']

# Проверка наличия модулей
HAS_DRF_SPECTACULAR = importlib.util.find_spec("drf_spectacular") is not None
HAS_DJANGO_FILTER = importlib.util.find_spec("django_filters") is not None
HAS_ALLAUTH = importlib.util.find_spec("allauth") is not None
HAS_SIMPLEJWT = importlib.util.find_spec("rest_framework_simplejwt") is not None

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "harvester",
]

if HAS_DRF_SPECTACULAR: INSTALLED_APPS.append("drf_spectacular")
if HAS_DJANGO_FILTER: INSTALLED_APPS.append("django_filters")
if HAS_ALLAUTH:
    INSTALLED_APPS.extend(["allauth", "allauth.account", "allauth.socialaccount"])

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "harvester.middleware.PrometheusMiddleware",
]

if HAS_ALLAUTH:
    MIDDLEWARE.insert(-1, "allauth.account.middleware.AccountMiddleware")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "config", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

if env.bool("USE_POSTGRES", default=False):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WIKICFP_BASE_URL = env("WIKICFP_BASE_URL", default="https://www.wikicfp.com")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=CELERY_BROKER_URL)
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    "collect-wikicfp-daily": {
        "task": "harvester.tasks.collect_wikicfp_task",
        "schedule": crontab(minute=10, hour=2),
        "args": (3, 40),
    },
    "process-conferences-every-hour": {
        "task": "harvester.tasks.process_conferences_task",
        "schedule": crontab(minute=0),
        "args": (500,),
    },
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
}

if HAS_DJANGO_FILTER:
    REST_FRAMEWORK["DEFAULT_FILTER_BACKENDS"].insert(0, "django_filters.rest_framework.DjangoFilterBackend")
if HAS_DRF_SPECTACULAR:
    REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
if HAS_SIMPLEJWT:
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append("rest_framework_simplejwt.authentication.JWTAuthentication")

SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(hours=1)}
SITE_ID = 1

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
if HAS_ALLAUTH:
    AUTHENTICATION_BACKENDS.append("allauth.account.auth_backends.AuthenticationBackend")
    ACCOUNT_EMAIL_VERIFICATION = "none"
    ACCOUNT_LOGIN_METHODS = {"username", "email"}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'verbose': {'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s'}},
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'harvester': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
