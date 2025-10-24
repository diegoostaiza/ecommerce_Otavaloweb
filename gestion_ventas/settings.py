from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
# Cargar variables de entorno
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    'ecommerceotavaloweb-production.up.railway.app',
    '.railway.app',
    '127.0.0.1', 
    'localhost',
    '0.0.0.0'
]


# Application definition
INSTALLED_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'ventas',
    'whitenoise.runserver_nostatic',  # Añadir para archivos estáticos
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Añadir esto
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestion_ventas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ventas.context_processors.carrito_context',
                'ventas.context_processors.favoritos_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_ventas.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Compatibilidad entre psycopg2 y psycopg
try:
    import psycopg2 as psycopg
    import sys
    sys.modules["psycopg"] = psycopg  # Crea alias para Django >=5
except ImportError:
    pass



DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://postgres:hwGgbwvmnyyaYTsGIrLqhuWvxDBCxwbC@interchange.proxy.rlwy.net:32268/railway",
        conn_max_age=600,
        conn_health_checks=True,
    )
}
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

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# Login/Logout redirects
LOGIN_REDIRECT_URL = 'ventas:productos'
LOGOUT_REDIRECT_URL = 'ventas:productos'

# EMAIL (usa variables de entorno para producción)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'diego17052009@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'iacn zbhn nkdm fmjw')
# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Configuración de Cloudinary ---
# --- Configuración de Cloudinary ---
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configuración principal de Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dmkqv0ypa'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '559371938858465'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', '7PKJq6i6tiBdm9r1Nsy4Vy_Vq7E'),
    secure=True
)

# Configuración para django-cloudinary-storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'dmkqv0ypa'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', '559371938858465'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', '7PKJq6i6tiBdm9r1Nsy4Vy_Vq7E'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# STRIPE
STRIPE_TEST_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

# Al final de settings.py
print("Cloudinary Config:")
print("Cloud Name:", CLOUDINARY_STORAGE['CLOUD_NAME'])
print("API Key:", CLOUDINARY_STORAGE['API_KEY'])
# No imprimas el API Secret por seguridad


# Seguridad en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')