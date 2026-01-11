import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url  # Добавь эту строку!

# Загружаем переменные из .env файла
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== БАЗОВЫЕ НАСТРОЙКИ ====================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-key-change-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Настройка хостов для разработки
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = []

# ==================== ПРИЛОЖЕНИЯ ====================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Твои приложения
    'books.apps.BooksConfig',
    'users.apps.UsersConfig',
    'analytics.apps.AnalyticsConfig',
]

# ==================== MIDDLEWARE ====================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==================== URL И ШАБЛОНЫ ====================

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==================== БАЗА ДАННЫХ ====================

# По умолчанию SQLite (для локальной разработки)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# БЕЗОПАСНОЕ ПОДКЛЮЧЕНИЕ К RAILWAY POSTGRESQL
# Проверяем, что DATABASE_URL существует и не пустой
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()

if DATABASE_URL:
    # Дополнительная проверка, что это PostgreSQL URL
    if DATABASE_URL.startswith(('postgres://', 'postgresql://')):
        try:
            DATABASES['default'] = dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        except Exception as e:
            print(f"ERROR: Failed to configure PostgreSQL: {e}")
            print("Falling back to SQLite")
    else:
        print(f"WARNING: Invalid DATABASE_URL format (not PostgreSQL): {DATABASE_URL[:50]}...")

# ==================== ВАЛИДАЦИЯ ПАРОЛЕЙ ====================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==================== МЕЖДУНАРОДНЫЕ НАСТРОЙКИ ====================

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ==================== СТАТИЧЕСКИЕ ФАЙЛЫ ====================

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== АУТЕНТИФИКАЦИЯ ====================

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ==================== ПРОЧИЕ НАСТРОЙКИ ====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== PRODUCTION НАСТРОЙКИ ====================
# Активируются только на Railway/PythonAnywhere

IS_PRODUCTION = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('PYTHONANYWHERE_DOMAIN')

if IS_PRODUCTION or not DEBUG:
    # Безопасность
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Хосты
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '.railway.app',
        '.pythonanywhere.com',
    ]

    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if railway_domain:
        ALLOWED_HOSTS.append(railway_domain)

    pythonanywhere_domain = os.getenv('PYTHONANYWHERE_SITE')
    if pythonanywhere_domain:
        ALLOWED_HOSTS.append(pythonanywhere_domain)

    # CSRF доверенные источники (ИСПРАВЛЕНО!)
    CSRF_TRUSTED_ORIGINS = [
        'https://*.railway.app',
        'https://*.pythonanywhere.com',
    ]
    if railway_domain:
        CSRF_TRUSTED_ORIGINS.append(f'https://{railway_domain}')

    # Логирование (ИСПРАВЛЕНО!)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {'class': 'logging.StreamHandler'},
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

    # Отключаем DEBUG в production
    DEBUG = False