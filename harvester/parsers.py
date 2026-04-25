import re
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup


WIKICFP_ID_PATTERN = re.compile(r"/cfp/program\.id/(\d+)")


@dataclass(slots=True)
class ParsedConference:
    wikicfp_id: str
    title: Optional[str]
    location: Optional[str]
    event_date_raw: Optional[str]
    deadline_raw: Optional[str]
    description_raw: Optional[str]
    detail_url: str
    raw_html: str


def extract_wikicfp_id(url: str) -> Optional[str]:
    match = WIKICFP_ID_PATTERN.search(url or "")
    return match.group(1) if match else None


def _clean_text(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    text = re.sub(r"\s+", " ", value).strip()
    return text or None


def parse_conference_html(html: str, detail_url: str) -> Optional[ParsedConference]:
    soup = BeautifulSoup(html, "html.parser")
    wikicfp_id = extract_wikicfp_id(detail_url)
    if not wikicfp_id:
        return None

    title_node = soup.find("h2") or soup.find("h1") or soup.find("title")
    title = _clean_text(title_node.get_text(" ", strip=True) if title_node else None)

    description_node = soup.select_one("div.cfp") or soup.select_one("div#cfp") or soup.find("p")
    description_raw = _clean_text(description_node.get_text(" ", strip=True) if description_node else None)

    location: Optional[str] = None
    event_date_raw: Optional[str] = None
    deadline_raw: Optional[str] = None

    # WikiCFP often stores labels inside table rows.
    for row in soup.select("table.gglu tr"):
        columns = row.find_all("td")
        if len(columns) < 2:
            continue
        label = _clean_text(columns[0].get_text(" ", strip=True))
        value = _clean_text(columns[1].get_text(" ", strip=True))
        if not label or not value:
            continue
        key = label.lower()
        if "when" in key and not event_date_raw:
            event_date_raw = value
        elif "where" in key and not location:
            location = value
        elif "deadline" in key and not deadline_raw:
            deadline_raw = value

    return ParsedConference(
        wikicfp_id=wikicfp_id,
        title=title,
        location=location,
        event_date_raw=event_date_raw,
        deadline_raw=deadline_raw,
        description_raw=description_raw,
        detail_url=detail_url,
        raw_html=html,
    )
