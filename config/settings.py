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

# Проверка SECRET_KEY для production
if not os.getenv('DJANGO_SECRET_KEY') and os.getenv('RAILWAY_PUBLIC_DOMAIN'):
    print("⚠️ ВНИМАНИЕ: DJANGO_SECRET_KEY не установлен в production среде!")

# Определяем домен Railway из переменных окружения
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', '')

# Настройка DEBUG - с приоритетом для отладки в production
DJANGO_DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
DEBUG = os.getenv('DEBUG', 'True') == 'True' or DJANGO_DEBUG


# ==================== ОПРЕДЕЛЕНИЕ ОКРУЖЕНИЯ ====================

def is_production():
    """Определяем, находимся ли мы в production среде"""
    # Если явно указан production
    if os.getenv('ENVIRONMENT') == 'production':
        return True
    # Если есть Railway домен
    if RAILWAY_PUBLIC_DOMAIN:
        return True
    # Если явно указано через переменную
    if os.getenv('PRODUCTION', 'False') == 'True':
        return True
    return False


IS_PRODUCTION = is_production()

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
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

if DATABASE_URL:
    # Конвертируем URL для dj-database-url (Railway использует postgres://)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    try:
        DATABASES['default'] = dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
        print(f"✅ Подключено к PostgreSQL: {DATABASES['default'].get('HOST', 'localhost')}")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        if IS_PRODUCTION and not DEBUG:
            raise
        else:
            print("⚠️ Используем SQLite для разработки")
else:
    print("ℹ️ DATABASE_URL не найден, используем SQLite")

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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Убираем предупреждение о missing static directory
STATICFILES_DIRS = []

# Проверяем существование локальной папки static
local_static_dir = os.path.join(BASE_DIR, 'static')
if os.path.exists(local_static_dir):
    STATICFILES_DIRS.append(local_static_dir)
    print(f"✅ Найдена локальная папка static: {local_static_dir}")

# Настройки WhiteNoise для статических файлов
if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Конфигурация WhiteNoise
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_AUTOREFRESH = DEBUG  # Автообновление только в режиме отладки

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== АУТЕНТИФИКАЦИЯ ====================

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ==================== ПРОЧИЕ НАСТРОЙКИ ====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== НАСТРОЙКИ ДЛЯ RAILWAY ====================

# Динамическое определение ALLOWED_HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Динамическое определение CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = []

if IS_PRODUCTION:
    print("🚀 Production mode enabled")

    # Добавляем Railway домен в ALLOWED_HOSTS
    if RAILWAY_PUBLIC_DOMAIN:
        ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
        ALLOWED_HOSTS.append(f'.{RAILWAY_PUBLIC_DOMAIN}')
        print(f"🌐 Домен: {RAILWAY_PUBLIC_DOMAIN}")

    # Добавляем общий Railway домен
    ALLOWED_HOSTS.append('.railway.app')

    # Настройка CSRF_TRUSTED_ORIGINS
    if RAILWAY_PUBLIC_DOMAIN:
        CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_PUBLIC_DOMAIN}')
        CSRF_TRUSTED_ORIGINS.append(f'https://*.{RAILWAY_PUBLIC_DOMAIN}')

    CSRF_TRUSTED_ORIGINS.append('https://*.railway.app')

    # Дополнительные хосты из переменных окружения
    additional_hosts = os.getenv('ADDITIONAL_ALLOWED_HOSTS', '')
    if additional_hosts:
        for host in additional_hosts.split(','):
            host = host.strip()
            if host:
                ALLOWED_HOSTS.append(host)

    # Дополнительные CSRF origins из переменных окружения
    additional_csrf = os.getenv('ADDITIONAL_CSRF_ORIGINS', '')
    if additional_csrf:
        for origin in additional_csrf.split(','):
            origin = origin.strip()
            if origin:
                CSRF_TRUSTED_ORIGINS.append(origin)

    # ==================== НАСТРОЙКИ БЕЗОПАСНОСТИ ====================

    # Настройки прокси для Railway
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Переменные для отладки безопасности
    DISABLE_SECURE = os.getenv('DISABLE_SECURE', 'False') == 'True'

    if not DISABLE_SECURE:
        # Безопасные настройки для production
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_HSTS_SECONDS = 31536000  # 1 год
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
        SECURE_BROWSER_XSS_FILTER = True
        SECURE_CONTENT_TYPE_NOSNIFF = True
        X_FRAME_OPTIONS = 'DENY'

        print("🔒 Безопасные настройки включены")
    else:
        # Отладочные настройки (временно)
        SECURE_SSL_REDIRECT = False
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False
        print("⚠️ Безопасные настройки ОТКЛЮЧЕНЫ для отладки")

    # ==================== ЛОГИРОВАНИЕ ====================

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{asctime}] {levelname} {module} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
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
            'django.security.csrf': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'whitenoise': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

    print(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print(f"✅ CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")

else:
    print("🔧 Development mode enabled")
    # Настройки для разработки
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0'])
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost:8000', 'http://127.0.0.1:8000'])

    # Для удобства отладки
    if DEBUG:
        print("🐛 DEBUG mode enabled")
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['console'],
                    'level': 'INFO',
                    'propagate': True,
                },
            },
        }

# ==================== ФИНАЛЬНАЯ ПРОВЕРКА ====================

print(f"📊 DEBUG: {DEBUG}")
print(f"🏭 IS_PRODUCTION: {IS_PRODUCTION}")
print(f"🌐 RAILWAY_PUBLIC_DOMAIN: {RAILWAY_PUBLIC_DOMAIN}")