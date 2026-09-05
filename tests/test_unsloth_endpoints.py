"""Seed Unsloth Studio nodes into model_endpoints so Added Models is not empty."""
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, ModelEndpoint


def _mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False)


def test_ensure_unsloth_endpoints_creates_shared_rows(monkeypatch):
    from src.unsloth_endpoints import ensure_unsloth_endpoints

    monkeypatch.setenv("UNSLOTH_BASE_URL", "http://192.168.1.2:8888/v1")
    monkeypatch.setenv("UNSLOTH_M2_BASE_URL", "http://192.168.1.191:8888/v1")
    monkeypatch.setenv("UNSLOTH_API_KEY", "sk-unsloth-m1")
    monkeypatch.setenv("UNSLOTH_M2_API_KEY", "sk-unsloth-m2")
    monkeypatch.delenv("UNSLOTH_EXTRA_BASE_URLS", raising=False)
    monkeypatch.delenv("LLM_HOSTS", raising=False)
    monkeypatch.delenv("UNSLOTH_A1_BASE_URL", raising=False)

    SessionLocal = _mem_db()
    db = SessionLocal()
    try:
        created = ensure_unsloth_endpoints(
            db,
            catalog_loader=lambda base, key: ["unsloth/Qwen3.5-9B-GGUF"] if "192.168.1.2" in base else [],
        )
        assert created >= 1
        rows = db.query(ModelEndpoint).order_by(ModelEndpoint.name).all()
        urls = {r.base_url for r in rows}
        assert "http://192.168.1.2:8888/v1" in urls
        assert "http://192.168.1.191:8888/v1" in urls
        m1 = next(r for r in rows if "192.168.1.2" in r.base_url)
        assert m1.owner is None
        assert m1.is_enabled is True
        assert m1.endpoint_kind == "local"
        assert json.loads(m1.cached_models) == ["unsloth/Qwen3.5-9B-GGUF"]
        assert m1.api_key == "sk-unsloth-m1"
        again = ensure_unsloth_endpoints(db, catalog_loader=lambda base, key: [])
        assert again == 0
        assert db.query(ModelEndpoint).count() == len(rows)
    finally:
        db.close()
