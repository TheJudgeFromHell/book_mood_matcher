import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

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

# Определяем домен Railway из переменных окружения
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', '')

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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для обслуживания статики в production
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
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()

if DATABASE_URL:
    try:
        DATABASES['default'] = dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    except Exception as e:
        print(f"ERROR: Failed to configure PostgreSQL: {e}")
        print("Falling back to SQLite")

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Если есть локальная папка static - используем её, иначе только из приложений
if os.path.exists(os.path.join(BASE_DIR, 'static')):
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    STATICFILES_DIRS = []

# Настройки WhiteNoise для статических файлов
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== АУТЕНТИФИКАЦИЯ ====================

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ==================== ПРОЧИЕ НАСТРОЙКИ ====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== НАСТРОЙКИ ДЛЯ RAILWAY (PRODUCTION) ====================

IS_PRODUCTION = RAILWAY_ENVIRONMENT == 'production' or RAILWAY_PUBLIC_DOMAIN

if IS_PRODUCTION:
    # Хосты для продакшена
    ALLOWED_HOSTS = [
        RAILWAY_PUBLIC_DOMAIN,
        '.railway.app',
        'localhost',
        '127.0.0.1',
    ]

    # CSRF доверенные источники
    CSRF_TRUSTED_ORIGINS = [
        f'https://{RAILWAY_PUBLIC_DOMAIN}',
        'https://*.railway.app',
    ]

    # Настройки безопасности для Railway
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Отключаем DEBUG в production если не указано иное
    if os.getenv('DJANGO_DEBUG', 'False') != 'True':
        DEBUG = False

    # Логирование
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

    print(f"Production mode enabled. Domain: {RAILWAY_PUBLIC_DOMAIN}")
    print(f"CSRF Trusted Origins: {CSRF_TRUSTED_ORIGINS}")
else:
    # Настройки для разработки
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
    print("Development mode enabled")