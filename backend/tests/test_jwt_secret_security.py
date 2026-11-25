import os
import pytest
from app.config import Settings

def test_production_missing_secret_fails(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValueError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        Settings()

def test_production_weak_secret_fails(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "short-weak-key")
    with pytest.raises(ValueError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        Settings()

def test_production_insecure_placeholder_fails(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "super-secret-production-key-change-in-env-2026")
    with pytest.raises(ValueError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        Settings()

def test_production_valid_secret_succeeds(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    strong_secret = "a" * 32
    monkeypatch.setenv("SECRET_KEY", strong_secret)
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "b" * 32)
    s = Settings()
    assert s.SECRET_KEY == strong_secret
    assert s.ENVIRONMENT == "production"

def test_development_fallback_generates_strong_secret(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    s = Settings()
    assert len(s.SECRET_KEY) >= 32
    assert s.ENVIRONMENT == "development"

def test_cors_origins_parsing(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://portal.univ.edu, https://admin.univ.edu")
    s = Settings()
    assert "https://portal.univ.edu" in s.CORS_ORIGINS
    assert "https://admin.univ.edu" in s.CORS_ORIGINS
