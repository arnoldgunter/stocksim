from datetime import datetime, timedelta, timezone

def range_to_start(range_key: str):
    now = datetime.now(timezone.utc)
    mapping = {
        "1d": now - timedelta(days=1),
        "1w": now - timedelta(weeks=1),
        "1m": now - timedelta(days=30),
        "3m": now - timedelta(days=90),
        "1y": now - timedelta(days=365),
        "all": None,
        None: now - timedelta(days=30),  # default = 1 month
        "":  now - timedelta(days=30),
    }
    return mapping.get(range_key, mapping[None])