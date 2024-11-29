import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("CONTENT_DB", "db_movies"),
        "USER": os.environ.get("CONTENT_DB_USER", "db_user"),
        "PASSWORD": os.environ.get("CONTENT_DB_PASSWORD", "qwerty"),
        "HOST": os.environ.get("CONTENT_DB_HOST", "db_content"),
        "PORT": os.environ.get("CONTENT_DB_PORT", 5432),
        "OPTIONS": {"options": os.environ.get("CONTENT_DB_OPTIONS")},
    }
}
