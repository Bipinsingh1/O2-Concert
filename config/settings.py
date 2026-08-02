from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-in-production')

# Refuse to start in production with the insecure default key
if not config('DEBUG', default=True, cast=bool) and 'django-insecure' in SECRET_KEY:
    raise RuntimeError(
        'SECRET_KEY must be set to a strong random value in production. '
        'Set the SECRET_KEY environment variable before deploying.'
    )

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'crispy_forms',
    'crispy_bootstrap5',

    # Core shared app
    'core',

    # Customer-facing apps
    'frontend.home',
    'frontend.accounts',
    'frontend.ticket_sales',
    'frontend.checkout',
    'frontend.my_tickets',

    # Admin-facing apps
    'backend.dashboard',
    'backend.ticket_admin',
    'backend.reports',
    'backend.qr_scanner',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Allow preview iframe to load the app
X_FRAME_OPTIONS = 'ALLOWALL'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

ROOT_URLCONF = 'config.urls'

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
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='o2concert_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_USER_MODEL = 'accounts.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} — {message}',
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
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'frontend': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'backend': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/my-tickets/'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='tickets@o2arena.com')

# Stripe
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='pk_test_placeholder')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_placeholder')

# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours

# ── O2 Arena Event Configuration ──────────────────────────────────────────────
EVENT_NAME = 'Dua Lipa Live at The O2'
EVENT_DATE = '2026-11-30'
TICKET_SALES_START = '2026-07-01'
TOTAL_VIP_TICKETS = 100
TOTAL_OTHER_TICKETS = 900

# Discount percentages by month (month number → discount %)
DISCOUNT_BY_MONTH = {
    7: 10,   # July
    8: 5,    # August
    9: 10,   # September
}

# Cancellation window in hours before the event
CANCELLATION_WINDOW_HOURS = 72

# Amendment fee percentage
REFUND_FEE_PERCENT = 20