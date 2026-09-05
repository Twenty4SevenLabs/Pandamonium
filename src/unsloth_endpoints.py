"""Register configured Unsloth Studio nodes as shared model endpoints."""
from __future__ import annotations

import json
import logging
from typing import Callable, List, Optional

from core.database import ModelEndpoint

logger = logging.getLogger(__name__)

CatalogLoader = Callable[[str, str], List[str]]


def ensure_unsloth_endpoints(
    db,
    *,
    catalog_loader: Optional[CatalogLoader] = None,
) -> int:
    """Insert missing Unsloth Studio endpoints. Returns count of new rows."""
    from src.unsloth_client import (
        list_studio_model_ids,
        normalize_openai_base,
        resolve_unsloth_api_key,
        unsloth_studio_targets,
    )

    loader = catalog_loader or (
        lambda base, key: list_studio_model_ids(base, key, timeout=12)
    )
    existing = {}
    for row in db.query(ModelEndpoint).all():
        existing[normalize_openai_base(row.base_url or "").lower()] = row
        existing[row.id] = row

    created = 0
    for spec in unsloth_studio_targets():
        base = spec["base_url"]
        key = resolve_unsloth_api_key(None, base)
        row = existing.get(base.lower()) or existing.get(spec["id"])
        models: List[str] = []
        try:
            models = [m for m in (loader(base, key) or []) if isinstance(m, str) and m]
        except Exception as exc:  # noqa: BLE001 — seed must not fail startup
            logger.debug("Unsloth catalog for %s failed: %s", spec["name"], exc)
        if row is None:
            row = ModelEndpoint(
                id=spec["id"],
                name=spec["name"],
                base_url=base,
                api_key=key or None,
                is_enabled=True,
                owner=None,
                endpoint_kind="local",
                model_type="llm",
                cached_models=json.dumps(models) if models else None,
            )
            db.add(row)
            existing[base.lower()] = row
            existing[spec["id"]] = row
            created += 1
            continue
        if key:
            row.api_key = key
        row.is_enabled = True
        if not (row.endpoint_kind or "").strip() or row.endpoint_kind == "auto":
            row.endpoint_kind = "local"
        if models:
            row.cached_models = json.dumps(models)
    db.commit()
    return created
