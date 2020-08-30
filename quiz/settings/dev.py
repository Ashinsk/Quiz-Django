from quiz.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = []

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Override log level
DJANGO_LOG_LEVEL = 'INFO'
LOGGING['root']['level'] = DJANGO_LOG_LEVEL
LOGGING['loggers']['django']['level'] = DJANGO_LOG_LEVEL
LOGGING['loggers']['django.request']['level'] = DJANGO_LOG_LEVEL