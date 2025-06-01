from datetime import datetime, timezone

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

def ensure_utc(dt: datetime) -> datetime:
    """Ensure the datetime is in UTC."""
    return_dt = datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
    if return_dt.tzinfo is None:
        return_dt = return_dt.replace(tzinfo=timezone.utc)
    return return_dt