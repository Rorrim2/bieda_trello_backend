"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import django_heroku

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BaseDir: {BASE_DIR}")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hi_$qs%7hn0mbrs(kixt$@%*x9#qxg0v7qro#-_a$*+*241qa8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#IMPORTAAANT!!!!!!!!!!!!!!!!!!!!!!!
#The 5 constants placed below should be used only in production mode ~ Kamil :) 

#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True
#SECURE_BROWSER_XSS_FILTER = True
#SECURE_SSL_REDIRECT = True
#SECURE_HSTS_SECONDS = 600 #value of that parameter should be increased as soon as current value work on heroku
 
ALLOWED_HOSTS = [
    'bieda-trello-backend.herokuapp.com', '127.0.0.1'
]

AUTH_USER_MODEL = 'skeleton.UserModel'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'skeleton.apps.SkeletonConfig',
    "django_filters",
    'corsheaders',
    'backend',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig'
]

GRAPHENE = {
    'SCHEMA': 'skeleton.schema.schema', # Where your Graphene schema lives
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

GRAPHQL_JWT = {
    # ...
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_DECODE_HANDLER': 'skeleton.utils.jwt_utils.decode_token',
    'JWT_PAYLOAD_HANDLER': 'skeleton.utils.jwt_utils.get_payload',
    'JWT_CSRF_ROTATION': True,
    'JWT_HIDE_TOKEN_FIELDS': True,
    'JWT_COOKIE_NAME': 'JWT',
    'JWT_REFRESH_TOKEN_COOKIE_NAME': 'JWT-refresh-token',
    'JWT_COOKIE_SECURE': True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'skeleton.utils.middleware.JWTAuthenticationMiddleware',
    'skeleton.utils.middleware.UpdateLastActivityMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
MAX_QUERY_DEPTH = 10

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
CORS_ALLOWED_ORIGINS = [
    "https://bieda-trello.herokuapp.com",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]
CORS_ORIGIN_ALLOW_ALL = True
import os
FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'exemplaryData\\'), 
    )
django_heroku.settings(locals())