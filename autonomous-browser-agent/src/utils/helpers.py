import re


def sanitize_selector(raw: str) -> str:
    return re.sub(r'[^\w\-#\[\].:=>()\s]', "", raw).strip()
