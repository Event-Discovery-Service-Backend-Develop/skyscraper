import json
import re


def clean_title(s):
    if not s or not isinstance(s, str):
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s[:500] if len(s) > 500 else s


def extract_keywords_from_raw(raw_json_str, max_words=10):
    if not raw_json_str:
        return None
    try:
        data = json.loads(raw_json_str)
    except (json.JSONDecodeError, TypeError):
        return None
    words = []
    if data.get("title"):
        t = clean_title(data["title"])
        for w in t.split():
            w = re.sub(r"[^\w\-]", "", w)
            if len(w) > 2 and w.lower() not in ("the", "and", "for", "with", "from"):
                words.append(w[:50])
                if len(words) >= max_words:
                    break
    concepts = data.get("keywords") or data.get("concepts") or []
    if isinstance(concepts, list):
        for c in concepts[:5]:
            if isinstance(c, dict) and c.get("display_name"):
                words.append(c["display_name"][:50])
            elif isinstance(c, str):
                words.append(c[:50])
            if len(words) >= max_words:
                break
    return ", ".join(words[:max_words]) if words else None
