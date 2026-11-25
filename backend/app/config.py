import os
import secrets
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Information & Internship Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    # Security: In production, MUST be set via environment variable (min 32 chars)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AES-256-GCM Data Encryption Key for sensitive fields (Aadhaar, PAN)
    DATA_ENCRYPTION_KEY: str = os.getenv("DATA_ENCRYPTION_KEY", "")
    
    # CORS: Allowed origins for frontend access
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ]
    
    # Trusted Reverse Proxies: IP addresses or CIDR ranges allowed to provide X-Forwarded-For / X-Real-IP
    TRUSTED_PROXY_IPS: Union[List[str], str] = [
        "127.0.0.1",
        "::1",
    ]
    
    # Database (SQLite by default; PostgreSQL supported for production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./student_portal.db")
    
    # File Storage
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MAX_FILE_SIZE_MB: int = 25
    
    # Admin Defaults
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "vignan123")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@institution.edu")

    model_config = SettingsConfigDict(case_sensitive=True)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Parse comma-separated string from environment
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        else:
            origins = list(v) if v else []
        # Security: Never permit wildcard '*' combined with credentialed sessions
        filtered = [o for o in origins if o and o != "*"]
        return filtered or ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("TRUSTED_PROXY_IPS", mode="before")
    @classmethod
    def parse_trusted_proxy_ips(cls, v: Union[str, List[str], None]) -> List[str]:
        env = os.getenv("ENVIRONMENT", "development").lower()
        if v is None:
            proxies = ["127.0.0.1", "::1"]
        elif isinstance(v, str):
            proxies = [ip.strip() for ip in v.split(",") if ip.strip()]
        elif isinstance(v, list):
            proxies = [str(ip).strip() for ip in v if str(ip).strip()]
        else:
            proxies = ["127.0.0.1", "::1"]

        # In production mode, strictly forbid 'testclient' or non-IP mock identifiers
        if env == "production":
            proxies = [ip for ip in proxies if ip.lower() != "testclient"]
        elif "testclient" not in proxies:
            proxies.append("testclient")

        return proxies or ["127.0.0.1", "::1"]

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str | None) -> str:
        env = os.getenv("ENVIRONMENT", "development").lower()
        val = (v or "").strip()
        insecure_placeholders = {
            "super-secret-production-key-change-in-env-2026",
            "changeme",
            "secret",
            "password",
            "12345678",
            "default",
        }
        
        # In production mode: enforce strict validation
        if env == "production":
            if not val or val.lower() in insecure_placeholders or len(val) < 32:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: "
                    "In production mode, an explicit, cryptographically strong SECRET_KEY "
                    "(minimum 32 characters) must be configured in environment variables. "
                    "Application startup aborted."
                )
            return val
        
        # Development / Testing fallback: Generate or retrieve persistent local dev secret
        if not val or val.lower() in insecure_placeholders:
            dev_secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dev_secret")
            if os.path.exists(dev_secret_file):
                try:
                    with open(dev_secret_file, "r", encoding="utf-8") as f:
                        cached = f.read().strip()
                        if len(cached) >= 32:
                            return cached
                except Exception:
                    pass
            new_secret = secrets.token_hex(32)
            try:
                with open(dev_secret_file, "w", encoding="utf-8") as f:
                    f.write(new_secret)
            except Exception:
                pass
            return new_secret

        return val

    @field_validator("DATA_ENCRYPTION_KEY", mode="before")
    @classmethod
    def validate_data_encryption_key(cls, v: str | None) -> str:
        env = os.getenv("ENVIRONMENT", "development").lower()
        val = (v or "").strip()
        if env == "production":
            if not val or len(val) < 32:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: "
                    "In production mode, an explicit 256-bit DATA_ENCRYPTION_KEY "
                    "(minimum 32 characters or 64 hex digits) must be configured in environment variables. "
                    "Application startup aborted."
                )
            return val

        # Development / Testing fallback: Generate or retrieve persistent local dev encryption key
        if not val:
            dev_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dev_encryption_key")
            if os.path.exists(dev_key_file):
                try:
                    with open(dev_key_file, "r", encoding="utf-8") as f:
                        cached = f.read().strip()
                        if len(cached) >= 32:
                            return cached
                except Exception:
                    pass
            new_key = secrets.token_hex(32)
            try:
                with open(dev_key_file, "w", encoding="utf-8") as f:
                    f.write(new_key)
            except Exception:
                pass
            return new_key
        return val

settings = Settings()

# Ensure upload directories exist
for folder in ["photos", "aadhaar", "certificates", "documents", "temp", "exports"]:
    os.makedirs(os.path.join(settings.UPLOAD_DIR, folder), exist_ok=True)
