import os
from pathlib import Path
import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-salaars-furniture-key-change-in-production-12345'),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', 'testserver', '.vercel.app', '*'])


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'store.apps.StoreConfig',
]

MIDDLEWARE = [
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
                'store.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
# Production needs a persistent database. Vercel's filesystem is read-only and every
# function instance gets its own throwaway /tmp, so SQLite there silently loses carts,
# orders and signups as requests move between instances.
default_db_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

DATABASES = {
    'default': env.db(default=default_db_url)
}

if DATABASES['default']['ENGINE'].endswith('postgresql'):
    # Supabase's transaction pooler multiplexes connections, so prepared statements and
    # server-side cursors must be off and connections must not be held open.
    DATABASES['default']['CONN_MAX_AGE'] = 0
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS'].update({
        'prepare_threshold': None,
        'sslmode': 'require',
    })

if 'VERCEL' in os.environ and DATABASES['default']['ENGINE'].endswith('sqlite3'):
    raise ImproperlyConfigured(
        'DATABASE_URL must point at a managed Postgres on Vercel. SQLite cannot work '
        'there: each serverless instance gets a private, ephemeral /tmp, so carts and '
        'orders disappear between requests.'
    )

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Vercel's CDN caches these responses, so a moderate max-age keeps swapped product
# images fresh within a day instead of pinning them for a year.
WHITENOISE_MAX_AGE = env.int('WHITENOISE_MAX_AGE', default=0)

# Index static from STATICFILES_DIRS and installed apps at startup rather than from
# STATIC_ROOT, so a deployment never depends on collectstatic output being present.
WHITENOISE_USE_FINDERS = env.bool('WHITENOISE_USE_FINDERS', default=True)
WHITENOISE_AUTOREFRESH = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Business details (override via environment in production)
SITE_URL = env('SITE_URL', default='https://salaars-home-omega.vercel.app')
SITE_PHONE_DISPLAY = env('SITE_PHONE_DISPLAY', default='+91 98000 00000')
SITE_PHONE_INTL = env('SITE_PHONE_INTL', default='919800000000')
SITE_WHATSAPP_NUMBER = env('SITE_WHATSAPP_NUMBER', default='917986307281')
SITE_ADDRESS = env('SITE_ADDRESS', default='Furniture Showroom, Kirti Nagar, New Delhi, India')
SITE_HOURS = env('SITE_HOURS', default='Every day · 8:00 AM – 9:00 PM')
SITE_FACEBOOK = env('SITE_FACEBOOK', default='https://www.facebook.com')
SITE_TIKTOK = env('SITE_TIKTOK', default='https://www.tiktok.com')
# Paste the owner's own Google Search Console token here; empty omits the meta tag.
SITE_GOOGLE_VERIFICATION = env('SITE_GOOGLE_VERIFICATION', default='')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/account/'
LOGOUT_REDIRECT_URL = '/'

# Email Configuration (SMTP / Gmail / Console fallback)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='marketinghome672@gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='sjhwipbjkmbjimsz')
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default="SALAAR's HOME <marketinghome672@gmail.com>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Session configuration
# Use signed cookie session backend on serverless to maintain sessions across ephemeral lambda instances
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

# Deployment security – enable the HTTPS options in production via environment
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['https://*.vercel.app', 'https://*.now.sh'])
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)
