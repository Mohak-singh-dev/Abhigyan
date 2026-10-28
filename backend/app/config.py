import os
from typing import List
from urllib.parse import urlsplit
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
from sqlalchemy.engine import URL, make_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="", description="PostgreSQL connection URL")
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:4173",
        description="Comma-separated allowed CORS origins"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Application Environment"
    )
    API_PREFIX: str = Field(
        default="/api",
        description="Base API path prefix"
    )
    JWT_SECRET_KEY: str = Field(default="", description="Secret key for JWT token signing")
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT hashing algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=120,
        description="Token lifetime in minutes"
    )
    DEMO_AUTH_ENABLED: bool = Field(
        default=True,
        description="Enable development-only demo-login flow. Must be False in production."
    )
    DEFAULT_SEED_PASSWORD: str = Field(default="", description="Initial password for local demo seed accounts")

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(ROOT_DIR, ".env"),
            os.path.join(BASE_DIR, ".env"),
            ".env",
            "backend/.env",
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.ENVIRONMENT.strip().lower() != "production":
            return self

        errors = []
        if len(self.JWT_SECRET_KEY) < 32 or self.JWT_SECRET_KEY.lower() in {
            "change-me", "changeme", "secret", "your-secret-key"
        }:
            errors.append("JWT_SECRET_KEY must contain at least 32 characters")
        if self.DEMO_AUTH_ENABLED:
            errors.append("DEMO_AUTH_ENABLED must be false")
        if not self.DATABASE_URL.strip() or "YOUR-" in self.DATABASE_URL.upper():
            errors.append("DATABASE_URL must be configured")
        try:
            database_url = make_url(self.DATABASE_URL)
            if database_url.drivername not in {"postgres", "postgresql", "postgresql+psycopg2"}:
                errors.append("DATABASE_URL must use PostgreSQL")
        except Exception:
            errors.append("DATABASE_URL must be a valid PostgreSQL URL")
        origins = self.cors_origin_list
        if not origins or any("*" in origin for origin in origins):
            errors.append("CORS_ORIGINS must contain exact frontend origins and no wildcards")
        parsed_origins = [urlsplit(origin) for origin in origins]
        if any(
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.hostname.lower() in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
            or parsed.username
            or parsed.password
            for parsed in parsed_origins
        ):
            errors.append("Production CORS_ORIGINS must use HTTPS origins")
        if errors:
            raise ValueError("Invalid production configuration: " + "; ".join(errors))
        return self

    @property
    def sqlalchemy_database_url(self) -> URL:
        """Return a SQLAlchemy URL using psycopg2 and encrypted PostgreSQL transport."""
        if not self.DATABASE_URL.strip():
            raise ValueError("DATABASE_URL must be configured before using the database.")
        url = make_url(self.DATABASE_URL)
        if url.drivername in {"postgres", "postgresql"}:
            url = url.set(drivername="postgresql+psycopg2")
        elif url.drivername != "postgresql+psycopg2":
            raise ValueError("DATABASE_URL must use PostgreSQL (postgresql:// or postgresql+psycopg2://).")

        query = dict(url.query)
        query.setdefault("sslmode", "require")
        return url.set(query=query)

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
