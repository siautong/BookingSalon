"""
Django settings for bookingsalon project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2nb@9!3+x&zy^#2gzq8n=##b+=#xc*3olimd$0$sj^x8pxb%+z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'mysalon',
    "rest_framework",
    "twilio",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookingsalon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates','mysalon/templates'],
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

WSGI_APPLICATION = 'bookingsalon.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {       
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": 'bookingsalon',
        "USER" : 'root',
        "PASSWORD" : '',
        'HOST' : 'localhost',
        'PORT' : '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "static/"

STATIC_URL = 'static/'

STATICFILES_DIRS =[
    os.path.join(BASE_DIR, 'static')
]

LOGIN_REDIRECT_URL = '/booking'

LOGIN_URL = '/login'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATA_URL = '/data/'
DATA_ROOT = os.path.join(BASE_DIR,'data')

X_FRAME_OPTIONS = 'ALLOW-FROM http://127.0.0.1:8000/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'mysalon.CustomUser'  # Sesuaikan dengan nama aplikasi dan model pengguna Anda

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend
    'mysalon.auth_backends.CustomUserBackend',    # CustomUser backend
    'mysalon.auth_backends.StaffBackend',         # Staff backend
]

TWILIO_ACCOUNT_SID = os.environ.get('AC1ea71c4caa8d4a475f7d0aa263795480')
TWILIO_AUTH_TOKEN = os.environ.get('a9a4814ef063e9f78ce8d03b5f3399c3')
TWILIO_PHONE_NUMBER = os.environ.get('+62859196196283')

# settings.py
PUSHER_APP_ID = '1834311'
PUSHER_KEY = '32c4883c694ee228d47b'
PUSHER_SECRET = 'fdb39b2d6682e958ab01'
PUSHER_CLUSTER = 'ap1'
PUSHER_SSL = True





