
import re
import unicodedata
import urllib.parse


def _normalize_text(text: str) -> str:
    """Normalize text: remove accents and symbols like ™."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text


def _slugify_item(title: str) -> str:
    """
    Convert full CS:GO item title into a Skinport item slug.
    Examples:
        '★ Butterfly Knife | Marble Fade (Factory New)' ->
        'butterfly-knife-marble-fade-factory-new'
        'StatTrak™ AK-47 | Redline (Field-Tested)' ->
        'stattrak-ak-47-redline-field-tested'
    """
    title = _normalize_text(title)
    title = title.replace("StatTrak", "stattrak")
    title = re.sub(r"[★™]", "", title)
    title = title.replace("|", " ")
    title = re.sub(r"[\(\)]", " ", title)
    # keep only alphanumerics and hyphens
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"\s+", "-", title.strip())
    return title.lower()


def to_item_url(title: str, item_id: str = "") -> str:
    """
    Generate Skinport item URL.
    If item_id is provided, it is appended to the URL.

    Example:
        to_item_url("StatTrak™ AK-47 | Redline (Field-Tested)", "69678360")
        -> https://skinport.com/item/stattrak-ak-47-redline-field-tested/69678360
    """
    slug = _slugify_item(title)
    base = f"https://skinport.com/item/{slug}/"
    return base + item_id if item_id else base
