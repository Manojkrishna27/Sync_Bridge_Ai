import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASS', 'root')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'ai_gateway')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 900 # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 604800 # 7 days
    
    # Redis configuration for token blocklist and caching
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
