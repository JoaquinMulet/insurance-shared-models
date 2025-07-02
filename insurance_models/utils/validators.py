import re

def normalize_rut(rut: str) -> str:
    """Normalize a Chilean RUT."""
    if not rut:
        return ""
    return re.sub(r'[^0-9kK]', '', str(rut)).upper()
