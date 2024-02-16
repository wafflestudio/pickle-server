from .common import *

DEBUG = False

# FIXME localhost는 dev 환경 구축 후 제거
ALLOWED_HOSTS = ["seeya.wafflestudio.com", "localhost"]

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
