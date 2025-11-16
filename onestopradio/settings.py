"""
OneStopRadio Django Settings
Production-ready configuration with environment variables
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-in-production-12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,backend-py-production-2c1b.up.railway.app', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'channels',
    # 'social_django',  # TODO: Add back with UUID-compatible migration
]

LOCAL_APPS = [
    'accounts',
    'stations',
    'streams',
    'social_media',
    'music',
    'realtime_dj',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'onestopradio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'onestopradio.wsgi.application'
ASGI_APPLICATION = 'onestopradio.asgi.application'

# Database
import dj_database_url

# Parse database URL and add PostgreSQL optimizations
default_database_config = dj_database_url.parse(
    config('DATABASE_URL', default='postgresql://postgres:JLiWeljtTNmpmimgYJVzLhgBRBQZsqcJ@metro.proxy.rlwy.net:14967/railway')
)

# Add PostgreSQL-specific optimizations
default_database_config.update({
    'ENGINE': 'django.db.backends.postgresql',
    'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),  # Connection pooling
    'CONN_HEALTH_CHECKS': config('DB_CONN_HEALTH_CHECKS', default=True, cast=bool),
    'DISABLE_SERVER_SIDE_CURSORS': config('DB_DISABLE_SERVER_SIDE_CURSORS', default=False, cast=bool),
    'OPTIONS': {
        'connect_timeout': 10,
        'keepalives_idle': 600,
        'keepalives_interval': 30,
        'keepalives_count': 3,
        'application_name': 'onestopradio_django',
        'sslmode': 'prefer',  # Use SSL if available
    },
    'TEST': {
        'NAME': 'test_' + default_database_config.get('NAME', 'railway'),
    }
})

DATABASES = {
    'default': default_database_config
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_EXPIRE_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://localhost:5000",  # Node.js signaling
    "http://127.0.0.1:3000",
    "https://onestopradio.up.railway.app",  # Production frontend
    "https://backend-py-production-2c1b.up.railway.app",  # Django backend
]

CORS_ALLOW_CREDENTIALS = True

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'OneStopRadio API',
    'DESCRIPTION': 'DJ Platform API for authentication, station management, and streaming',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File Upload Configuration  
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'onestopradio': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Django Channels Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')

if DEBUG:
    # Use in-memory for development
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
else:
    # Use Redis for production
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }

# Celery Configuration (for background tasks)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# PostgreSQL Performance Settings
if not DEBUG:
    # Production database optimizations
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': 20,
        'AUTOCOMMIT': True,
        'ATOMIC_REQUESTS': False,
        'server_side_binding': True,
    })

# Database Health Check Settings
DB_HEALTH_CHECK_ENABLED = config('DB_HEALTH_CHECK_ENABLED', default=True, cast=bool)
DB_CONNECTION_RETRY_ATTEMPTS = config('DB_CONNECTION_RETRY_ATTEMPTS', default=3, cast=int)
DB_CONNECTION_RETRY_DELAY = config('DB_CONNECTION_RETRY_DELAY', default=1, cast=int)

# Real-time DJ Configuration
DJ_AUDIO_SAMPLE_RATE = 48000
DJ_AUDIO_BUFFER_SIZE = 1024
DJ_MAX_CONCURRENT_SESSIONS = 100
DJ_SESSION_TIMEOUT_MINUTES = 60