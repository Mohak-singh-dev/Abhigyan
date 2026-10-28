import pytest
from pydantic import ValidationError

from app.config import Settings


def production_settings(**overrides):
    values = {
        "_env_file": None,
        "ENVIRONMENT": "production",
        "DATABASE_URL": "postgresql://postgres.project:password@pooler.example.com:5432/postgres?sslmode=require",
        "JWT_SECRET_KEY": "a-long-random-production-secret-value-123456",
        "CORS_ORIGINS": "https://abhigyan.example.com",
        "DEMO_AUTH_ENABLED": False,
    }
    values.update(overrides)
    return Settings(**values)


def test_valid_production_configuration_requires_exact_https_origin():
    settings = production_settings()
    assert settings.cors_origin_list == ["https://abhigyan.example.com"]
    assert settings.sqlalchemy_database_url.drivername == "postgresql+psycopg2"
    assert settings.sqlalchemy_database_url.query["sslmode"] == "require"


@pytest.mark.parametrize(
    "overrides",
    [
        {"JWT_SECRET_KEY": "short"},
        {"DATABASE_URL": ""},
        {"DEMO_AUTH_ENABLED": True},
        {"CORS_ORIGINS": "*"},
        {"CORS_ORIGINS": "http://localhost:5173"},
    ],
)
def test_unsafe_production_configuration_is_rejected(overrides):
    with pytest.raises(ValidationError, match="Invalid production configuration"):
        production_settings(**overrides)
