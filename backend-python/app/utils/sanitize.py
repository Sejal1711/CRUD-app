import bleach


def sanitize(value):
    """Recursively strip all HTML tags and attributes from strings."""
    if isinstance(value, str):
        return bleach.clean(value, tags=[], attributes={}, strip=True).strip()
    if isinstance(value, dict):
        return {k: sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    return value
