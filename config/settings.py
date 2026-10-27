"""
Django settings for StreamFlix project.
"""

import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

IS_VERCEL = os.getenv('VERCEL') == '1'

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_VERCEL:
        raise ImproperlyConfigured('SECRET_KEY must be configured in Vercel environment variables.')
    SECRET_KEY = 'django-insecure-local-development-only'

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

hosts_env = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver')
ALLOWED_HOSTS = [host.strip() for host in hosts_env.split(',') if host.strip()]
ALLOWED_HOSTS.extend(host for host in ('.vercel.app', '.now.sh') if host not in ALLOWED_HOSTS)

csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_origins_env.split(',') if origin.strip()
]
CSRF_TRUSTED_ORIGINS.extend(
    origin
    for origin in ('https://*.vercel.app', 'https://*.now.sh')
    if origin not in CSRF_TRUSTED_ORIGINS
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # StreamFlix custom applications
    'accounts.apps.AccountsConfig',
    'movies.apps.MoviesConfig',
    'support.apps.SupportConfig',
    'monitoring.apps.MonitoringConfig',
]

MIDDLEWARE = [
    'monitoring.middleware.RequestLoggingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'movies.context_processors.movie_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    parsed_database_url = urlparse(DATABASE_URL)
    if parsed_database_url.scheme not in ('postgres', 'postgresql'):
        raise ImproperlyConfigured('DATABASE_URL must be a PostgreSQL connection URL.')

    database_options = {
        key: values[-1]
        for key, values in parse_qs(parsed_database_url.query).items()
        if key == 'sslmode' and values
    }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': unquote(parsed_database_url.path.lstrip('/')),
            'USER': unquote(parsed_database_url.username or ''),
            'PASSWORD': unquote(parsed_database_url.password or ''),
            'HOST': parsed_database_url.hostname or '',
            'PORT': str(parsed_database_url.port or ''),
            'OPTIONS': database_options,
            'CONN_MAX_AGE': 60,
        }
    }
elif os.getenv('DB_ENGINE') == 'django.db.backends.postgresql' or (os.getenv('DB_NAME') and os.getenv('DB_USER')):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage for efficient static file handling in production
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
            if not DEBUG
            else 'whitenoise.storage.CompressedStaticFilesStorage'
        ),
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# MongoDB configuration (Chat logs and feedback)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'streamflix_db')

# Third-party TMDB API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_READ_ACCESS_TOKEN = os.getenv('TMDB_READ_ACCESS_TOKEN', '')
TMDB_TIMEOUT = float(os.getenv('TMDB_TIMEOUT', '5.0'))

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', str(IS_VERCEL)).lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1', 'yes')
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() in ('true', '1', 'yes')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    if IS_VERCEL:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] {levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'streamflix': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
