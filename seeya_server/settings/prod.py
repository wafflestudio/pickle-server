from .common import *

DEBUG = True

# FIXME localhost는 dev 환경 구축 후 제거
ALLOWED_HOSTS = [
    "seeya.wafflestudio.com",
    "seeya-api.wafflestudio.com",
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "https://seeya.wafflestudio.com",
    "https://seeya-api.wafflestudio.com",
    "http://localhost:5173",
    "http://localhost:8080",
]
CSRF_COOKIE_DOMAIN = ".wafflestudio.com"
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "lax"

CORS_ORIGIN_WHITELIST = [
    "https://seeya.wafflestudio.com",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("SEEYA_DB_NAME"),
        "USER": os.getenv("SEEYA_DB_USER"),
        "PASSWORD": os.getenv("SEEYA_DB_PASSWORD"),
        "HOST": os.getenv("SEEYA_DB_HOST"),
        "PORT": os.getenv("SEEYA_DB_PORT"),
    }
}
