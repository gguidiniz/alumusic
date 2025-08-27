import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "default_secret_key_for_dev")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    CACHE_TYPE = 'FileSystemCache'
    CACHE_DIR = 'instance/cache'
    CACHE_DEFAULT_TIMEOUT = 300

    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", 'redis://redis:6379/0')
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND", 'redis://redis:6379/0')
settings = Settings()