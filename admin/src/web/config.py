import os
from os import environ

from src.core.database import db as main_db


class Config:
    TESTING = False
    SECRET_KEY = "your_secret_key"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_FILE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'flask_sessions')


class ProductionConfig(Config):
    SECRET_KEY = environ.get("SECRET_KEY", "change-me-in-production")
    SESSION_TYPE = "cookie"

    STORAGE_ENDPOINT_URL = environ.get("STORAGE_ENDPOINT_URL")
    MINIO_ACCESS_KEY = environ.get("STORAGE_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("STORAGE_SECRET_KEY")
    MINIO_BUCKET = environ.get("STORAGE_BUCKET", "grupo19")

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")

    # Comma-separated list of allowed CORS origins, e.g. https://mi-portal.vercel.app
    CORS_ORIGINS = [o.strip() for o in environ.get("CORS_ORIGINS", "").split(",") if o.strip()]


class DevelopmentConfig(Config):
    STORAGE_ENDPOINT_URL = "http://localhost:9000"
    MINIO_ACCESS_KEY = "grupo19admin"
    MINIO_SECRET_KEY = "grupo19secret"
    MINIO_BUCKET = "grupo19"

    SECRET_KEY = "your_dev_secret_key"
    DB_USER = "postgres"
    DB_PASSWORD = "admin"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "grupo19"
    DB_SCHEME = "postgresql+psycopg2"

    SQLALCHEMY_DATABASE_URI = (
        f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
