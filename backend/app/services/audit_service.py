import json
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit(
    db: Session,
    user_id: int | None,
    username: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    details: dict | str | None = None,
    ip_address: str | None = None,
):
    details_str = json.dumps(details, default=str) if isinstance(details, (dict, list)) else (details or "")
    audit = AuditLog(
        user_id=user_id,
        username=username or "system",
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details_str,
        ip_address=ip_address,
    )
    db.add(audit)
    try:
        db.commit()
    except Exception:
        db.rollback()
