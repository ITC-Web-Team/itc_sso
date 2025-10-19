import environ
from pathlib import Path
import os


env = environ.Env(
    DEBUG=(bool, False) 
)

BASE_DIR = Path(__file__).resolve().parent.parent


environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY') 
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS') 

CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=True) 
CORS_ORIGIN_ALLOW = env.list('CORS_ORIGIN_ALLOW', default=[])

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
CSRF_TRUSTED_ORIGINS_ALL = True
CSRF_COOKIE_SECURE = True  
CSRF_COOKIE_SAMESITE = 'None'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # For SEO sitemap
    'django.contrib.sites',  # Required for sitemap
    'accounts',
    'corsheaders',
    'widget_tweaks',
    'rest_framework',
    'gunicorn',
    'minio_storage',
]

# Site ID for django.contrib.sites
SITE_ID = 1

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise for serving static files (including admin CSS)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Dynamically load email configurations from environment variables
EMAIL_CONFIGS = []
EMAIL_CONFIG_COUNT = int(env('EMAIL_CONFIG_COUNT', default=1))

for i in range(1, EMAIL_CONFIG_COUNT + 1):
    config = {
        'EMAIL_HOST': env(f'EMAIL_HOST_{i}', default='smtp.gmail.com'),
        'EMAIL_PORT': env.int(f'EMAIL_PORT_{i}', default=587),
        'EMAIL_USE_TLS': env.bool(f'EMAIL_USE_TLS_{i}', default=True),
        'EMAIL_HOST_USER': env(f'EMAIL_HOST_USER_{i}', default=env('EMAIL_HOST_USER', default='')),
        'EMAIL_HOST_PASSWORD': env(f'EMAIL_HOST_PASSWORD_{i}', default=env('EMAIL_HOST_PASSWORD', default='')),
    }
    
    # Only add configuration if user and password are provided
    if config['EMAIL_HOST_USER'] and config['EMAIL_HOST_PASSWORD']:
        EMAIL_CONFIGS.append(config)

# Fallback to default configuration if no email configs are found
if not EMAIL_CONFIGS:
    EMAIL_CONFIGS = [{
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_HOST_USER': '',
        'EMAIL_HOST_PASSWORD': '',
    }]

# Default to the first configuration
EMAIL_HOST = EMAIL_CONFIGS[0]['EMAIL_HOST']
EMAIL_PORT = EMAIL_CONFIGS[0]['EMAIL_PORT']
EMAIL_USE_TLS = EMAIL_CONFIGS[0]['EMAIL_USE_TLS']
EMAIL_HOST_USER = EMAIL_CONFIGS[0]['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = EMAIL_CONFIGS[0]['EMAIL_HOST_PASSWORD']

# Add a check to warn about missing email configuration
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    import warnings
    warnings.warn("Email configuration is missing. Email sending will be disabled.", UserWarning)

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  
SESSION_COOKIE_SECURE = True  
SESSION_COOKIE_HTTPONLY = True 

# Storage backends
DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"

# Optional: Set public policies for buckets
MINIO_STORAGE_AUTO_CREATE_MEDIA_POLICY = 'READ_WRITE'
MINIO_STORAGE_AUTO_CREATE_STATIC_POLICY = 'READ_ONLY'

# Remove duplicate setting definitions
# STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"  # We're using WhiteNoise instead

# MinIO configuration
MINIO_STORAGE_ENDPOINT = env('MINIO_STORAGE_ENDPOINT')  # Should be just the hostname
MINIO_STORAGE_ACCESS_KEY = env('MINIO_STORAGE_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = env('MINIO_STORAGE_SECRET_KEY')
MINIO_STORAGE_USE_HTTPS = env.bool('MINIO_STORAGE_USE_HTTPS', default=True)
MINIO_STORAGE_PORT = env.int('MINIO_STORAGE_PORT', default=443)

# Media files configuration
MINIO_STORAGE_MEDIA_BUCKET_NAME = env('MINIO_STORAGE_MEDIA_BUCKET_NAME')
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_MEDIA_OBJECT_METADATA = {"Cache-Control": "max-age=1000"}

# Static files configuration
MINIO_STORAGE_STATIC_BUCKET_NAME = env('MINIO_STORAGE_STATIC_BUCKET_NAME')
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True

# ============================================================================
# SEO OPTIMIZATION SETTINGS
# ============================================================================

# Security headers for SEO and best practices
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (enable in production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Prepend www to URLs (optional - set to False if not using www)
PREPEND_WWW = False

# Append slash to URLs
APPEND_SLASH = True
