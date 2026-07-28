import os
from dotenv import load_dotenv

load_dotenv()

def _get_database_uri():
    """
    Resolve database URI with automatic local-dev fallback.
    Priority:
      1. DATABASE_URL env var (explicit override)
      2. MySQL if DB_HOST is NOT 'mysql' (i.e. a real host like 127.0.0.1)
      3. SQLite fallback if DB_HOST is 'mysql' (Docker-only hostname) and we're
         not inside Docker
    """
    # Explicit full override
    explicit = os.getenv('DATABASE_URL')
    if explicit:
        return explicit

    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASS', 'root')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'ai_gateway')

    # If host is 'mysql' we're reading a Docker .env on the host → use SQLite
    if db_host == 'mysql':
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'syncbridge_local.db')
        db_path = os.path.abspath(db_path)
        print(f"[config] DB_HOST=mysql detected outside Docker → using SQLite: {db_path}")
        return f"sqlite:///{db_path}"

    return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-local-dev')
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-local-dev')
    JWT_ACCESS_TOKEN_EXPIRES = 900   # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days

    # Redis: fall back gracefully if Redis uses Docker hostname
    _redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_URL = 'redis://localhost:6379/0' if 'redis:' in _redis_url else _redis_url
