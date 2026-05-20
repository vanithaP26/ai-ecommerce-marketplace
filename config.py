import os

class Config:
    # Flask Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'antigravity-secret-key-1337-ecommerce')
    
    # Session Configuration
    SESSION_COOKIE_NAME = 'marketplace_session'
    PERMANENT_SESSION_LIFETIME = 86400  # 1 day in seconds
    
    # Upload Configurations
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Database Configurations
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')  # 'mysql' or 'sqlite'
    
    # MySQL configurations
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'multi_vendor_marketplace')
    
    # SQLite configurations
    SQLITE_DB = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
    
    @classmethod
    def get_upload_path(cls):
        if not os.path.exists(cls.UPLOAD_FOLDER):
            os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        return cls.UPLOAD_FOLDER
