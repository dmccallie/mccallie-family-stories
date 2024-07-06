from decouple import config, Csv
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE_DIR: ", BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-x+z=e!(i*ol4+tyrw-b=!-(lz!3n3f$(h)28wpptveeatk1utw'
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
print(f"settings: DEBUG NOW SET TO:{DEBUG}")


ALLOWED_HOSTS = ['*'] # allows local LAN testing at 0.0.0.0:8000
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())
# ALLOWED_HOSTS = ['stories.davidmccallie.com', 'www.stories.davidmccallie.com']

# doesn't seem to interfere with local development, but necessary for production (caddy)
CSRF_TRUSTED_ORIGINS = [
    'https://stories.davidmccallie.com',
    'https://mccalliefamilystories.com',
]

# added this section for allauth
AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',

]

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic", # force use of WN even when debug=True
    'home',
    'stories',
    'profiles',
    'storages', # new, for aws S3 storage
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar', #new, for debugging
    "django_htmx", #new, for htmx
    
    # added for allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware", #new, for debugging
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", # static file via runserver 
    "django_htmx.middleware.HtmxMiddleware", #new, for htmx
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Add the allauth middleware:
    "allauth.account.middleware.AccountMiddleware",
]

# allauth - provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '123',
            'secret': '456',
            'key': ''
        }
    }
}


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates', # a non-app-specific directory for templates
        ],
        'APP_DIRS': True, # tells Django to look for templates in the app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.csrf',  # dpm added this for allauth???
                'django.contrib.messages.context_processors.messages',
                
                 # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

TIME_ZONE = 'US/Central'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# this is where collectstatic will copy files to
STATIC_ROOT = BASE_DIR / 'staticfiles'

# this is where collectstatic will look for files to copy to STATIC_ROOT
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# config compressor - new
# COMPRESS_ENABLED = False
# COMPRESS_ROOT = BASE_DIR / 'static'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# unify storages
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": config('AWS_ACCESS_KEY_ID'),
            "secret_key": config('AWS_SECRET_ACCESS_KEY'),
            "bucket_name": config('AWS_STORAGE_BUCKET_NAME'),
            "region_name": config('AWS_S3_REGION_NAME'),
            "querystring_auth": False,
            "file_overwrite": False,
            "object_parameters": {
                "CacheControl": "max-age=8640000",
            },
        }
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# added for whitenoise
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# added for debug_toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "0.0.0.0",
    "172.28.240.1",
]



bucket_name = config('AWS_STORAGE_BUCKET_NAME')
print("setting get os env bucket_name: ", bucket_name)
MEDIA_URL = f'https://{bucket_name}.s3.amazonaws.com/'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# auth settings
LOGIN_REDIRECT_URL = 'home:home'
LOGOUT_REDIRECT_URL = 'home:home'

# email settings
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.noip.com' # 'smtp.gmail.com' # 'mail.noip.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'admin@mccalliefamilystories.com' # 'dmccallie@gmail.com' # 'admin@mccalliefamilystories.com'
EMAIL_HOST_PASSWORD = 'mccallieclan1!' # 'njou gkea wgzz mbla' #'mccallieclan1!'

# gmail njou gkea wgzz mbla

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

