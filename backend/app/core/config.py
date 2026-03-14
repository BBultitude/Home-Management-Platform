"""
Application Configuration
Loads settings from environment variables and Docker secrets
"""

from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


def read_secret(secret_path: str, env_fallback: str | None = None) -> str:
    """Read a Docker secret from file, fallback to environment variable for testing"""
    try:
        with open(secret_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # In test/dev environments, allow fallback to environment variable
        if env_fallback:
            import os
            value = os.getenv(env_fallback)
            if value:
                return value
        raise RuntimeError(f"Secret file not found: {secret_path}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_URL: str = "http://localhost:8000"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Database
    DATABASE_URL: str = "postgresql+psycopg://homeuser@db:5432/homedb"
    DB_PASSWORD_FILE: str = "/run/secrets/db_password"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    @property
    def database_url_with_password(self) -> str:
        """Construct full database URL with password from secret"""
        password = read_secret(self.DB_PASSWORD_FILE, "DB_PASSWORD")
        # Replace password placeholder in URL (psycopg dialect)
        # Handle both @db: and @database: for dev and prod
        if "@database:" in self.DATABASE_URL:
            return self.DATABASE_URL.replace("@database:", f":{password}@database:")
        else:
            return self.DATABASE_URL.replace("@db:", f":{password}@db:")

    # Security Secrets (loaded from Docker secrets)
    JWT_SECRET_FILE: str = "/run/secrets/jwt_secret"
    MFA_ENCRYPTION_KEY_FILE: str = "/run/secrets/mfa_encryption_key"

    @property
    def jwt_secret(self) -> str:
        """Load JWT secret from Docker secret file"""
        return read_secret(self.JWT_SECRET_FILE, "JWT_SECRET")

    @property
    def mfa_encryption_key(self) -> str:
        """Load MFA encryption key from Docker secret file"""
        return read_secret(self.MFA_ENCRYPTION_KEY_FILE, "MFA_ENCRYPTION_KEY")

    # Session Settings
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    SESSION_EXPIRY_HOURS: int = 8
    TRUSTED_DEVICE_EXPIRY_DAYS: int = 30

    # Login Throttling
    MAX_LOGIN_ATTEMPTS_PER_MINUTE: int = 10
    LOGIN_LOCKOUT_MINUTES: int = 15

    # File Upload
    MAX_FILE_SIZE_MB: int = 20
    MAX_STORAGE_PER_USER_MB: int = 200
    UPLOAD_DIR: Path = Path("/app/uploads")
    ALLOWED_FILE_TYPES: str = "application/pdf,image/jpeg,image/png,image/jpg,application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Parse ALLOWED_FILE_TYPES into a list"""
        return [ftype.strip() for ftype in self.ALLOWED_FILE_TYPES.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def max_storage_per_user_bytes(self) -> int:
        """Convert MB to bytes"""
        return self.MAX_STORAGE_PER_USER_MB * 1024 * 1024

    # Localization (fixed for v1)
    LOCALE: str = "en_AU"
    DATE_FORMAT: str = "DD/MM/YYYY"
    TIME_FORMAT: str = "12h"
    CURRENCY: str = "AUD"
    FINANCIAL_YEAR_START_MONTH: int = 7  # July

    # Audit Logging Retention (years)
    AUDIT_LOG_RETENTION_TAX_YEARS: int = 5
    AUDIT_LOG_RETENTION_AUTH_YEARS: int = 5
    AUDIT_LOG_RETENTION_OTHER_YEARS: int = 2

    # Feature Flags (v1.1+)
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_BACKUPS: bool = False
    ENABLE_MONITORING: bool = False


# Global settings instance
settings = Settings()


# Development environment helper
def is_development() -> bool:
    """Check if running in development mode"""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Check if running in production mode"""
    return settings.ENVIRONMENT == "production"
