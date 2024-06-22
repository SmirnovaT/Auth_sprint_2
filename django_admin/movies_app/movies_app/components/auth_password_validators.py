AUTH_USER_MODEL = "movies.User"

AUTHENTICATION_BACKENDS = [
    'movies_app.auth.CustomBackend',
]

AUTH_API_LOGIN_URL = "http://auth_service:8010/api/v1/login/"

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
