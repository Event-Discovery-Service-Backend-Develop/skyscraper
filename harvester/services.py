import logging
import random
import re
import time
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Conference
from .parsers import ParsedConference, parse_conference_html

logger = logging.getLogger(__name__)


class CrawlerService:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; rv:124.0) Gecko/20100101 Firefox/124.0",
    ]

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 25.0,
        delay_min: float = 0.6,
        delay_max: float = 2.4,
        proxy: Optional[str] = None,
    ) -> None:
        self.base_url = base_url or settings.WIKICFP_BASE_URL
        self.timeout = timeout
        self.delay_min = max(0.1, delay_min)
        self.delay_max = max(self.delay_min, delay_max)
        self.proxy = proxy or getattr(settings, "WIKICFP_PROXY_URL", None)

    def _random_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8"]),
        }

    def _human_delay(self, minimum: Optional[float] = None, maximum: Optional[float] = None) -> None:
        min_delay = self.delay_min if minimum is None else minimum
        max_delay = self.delay_max if maximum is None else maximum
        time.sleep(random.uniform(min_delay, max(max_delay, min_delay)))

    def _fetch_with_retry(self, client: httpx.Client, url: str, params: Optional[dict] = None) -> Optional[str]:
        for attempt in range(1, 5):
            try:
                response = client.get(url, params=params, headers=self._random_headers(), timeout=self.timeout)
                if response.status_code in (403, 429):
                    wait_seconds = min(2**attempt + random.uniform(0.1, 1.0), 20)
                    logger.warning("HTTP %s from %s. Sleeping %.1fs", response.status_code, url, wait_seconds)
                    time.sleep(wait_seconds)
                    continue
                response.raise_for_status()
                return response.text
            except httpx.RequestError as exc:
                wait_seconds = min(attempt * 1.5, 6.0)
                logger.warning("Network error for %s (%s). Retry in %.1fs", url, exc, wait_seconds)
                time.sleep(wait_seconds)
            except httpx.HTTPStatusError as exc:
                logger.warning("HTTP error for %s: %s", url, exc)
                break
        return None

    def _collect_detail_urls(self, listing_html: str) -> list[str]:
        soup = BeautifulSoup(listing_html, "html.parser")
        urls: list[str] = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if not re.search(r"/cfp/program\.id/\d+", href):
                continue
            urls.append(urljoin(self.base_url, href))
        return list(dict.fromkeys(urls))

    def collect(self, pages: int = 2, per_page: int = 30) -> dict[str, int]:
        collected = 0
        created = 0
        updated = 0

        with self._build_client() as client:
            for page in range(1, pages + 1):
                listing_html = self._fetch_with_retry(client, f"{self.base_url}/cfp/allcfp", params={"page": page})
                if not listing_html:
                    continue

                detail_urls = self._collect_detail_urls(listing_html)[:per_page]
                for detail_url in detail_urls:
                    self._human_delay()
                    detail_html = self._fetch_with_retry(client, detail_url)
                    if not detail_html:
                        continue

                    parsed = parse_conference_html(detail_html, detail_url)
                    if not parsed:
                        continue

                    is_created = self._upsert_conference(parsed)
                    collected += 1
                    if is_created:
                        created += 1
                    else:
                        updated += 1

                self._human_delay(1.2, 3.5)

        return {"collected": collected, "created": created, "updated": updated}

    def _build_client(self) -> httpx.Client:
        if not self.proxy:
            return httpx.Client(follow_redirects=True)
        try:
            return httpx.Client(follow_redirects=True, proxy=self.proxy)
        except TypeError:
            return httpx.Client(follow_redirects=True, proxies=self.proxy)

    @staticmethod
    @transaction.atomic
    def _upsert_conference(parsed: ParsedConference) -> bool:
        _, created = Conference.objects.update_or_create(
            wikicfp_id=parsed.wikicfp_id,
            defaults={
                "title": parsed.title,
                "location": parsed.location,
                "url": parsed.detail_url,
                "raw_html": parsed.raw_html,
                "raw_description": parsed.description_raw,
                "event_date_raw": parsed.event_date_raw,
                "deadline_raw": parsed.deadline_raw,
                "is_processed": False,
                "last_collected_at": timezone.now(),
            },
        )
        return created


class ProcessingService:
    KEYWORD_RULES = {
        "AI": ("ai", "artificial intelligence", "machine learning", "deep learning", "llm"),
        "Security": ("security", "cyber", "cryptography", "privacy", "forensics"),
        "Physics": ("physics", "quantum", "particle", "astrophysics"),
        "Data Science": ("data mining", "data science", "analytics", "big data"),
        "Software Engineering": ("software", "architecture", "testing", "devops", "microservice"),
    }

    DATE_FORMATS = (
        "%Y-%m-%d",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%d %B %Y",
    )

    def process_pending(self, limit: int = 200) -> int:
        queryset = Conference.objects.filter(is_processed=False).order_by("id")[:limit]
        processed = 0
        for conference in queryset:
            self._process_one(conference)
            processed += 1
        return processed

    def _process_one(self, conference: Conference) -> None:
        conference.event_date = self._parse_date(conference.event_date_raw)
        conference.deadline = self._parse_date(conference.deadline_raw)
        conference.clean_description = self._clean_description(conference.raw_description or conference.raw_html or "")
        conference.keywords = self._extract_tags(conference)
        conference.is_processed = True
        conference.save(
            update_fields=[
                "event_date",
                "deadline",
                "clean_description",
                "keywords",
                "is_processed",
                "updated_at",
            ]
        )

    def _parse_date(self, raw_value: Optional[str]) -> Optional[datetime.date]:
        if not raw_value:
            return None
        candidate = raw_value.replace("TBD", "").replace("-", " - ").strip()
        chunks = [part.strip() for part in candidate.split(" - ") if part.strip()]
        for chunk in chunks:
            parsed = self._try_parse_date_chunk(chunk)
            if parsed:
                return parsed
        return self._try_parse_date_chunk(candidate)

    def _try_parse_date_chunk(self, text: str) -> Optional[datetime.date]:
        normalized = re.sub(r"\s+", " ", text).strip(", ")
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(normalized, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _clean_description(raw_value: str) -> str:
        if not raw_value:
            return ""
        soup = BeautifulSoup(raw_value, "html.parser")
        text = soup.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_tags(self, conference: Conference) -> str:
        source = " ".join(
            [
                conference.title or "",
                conference.clean_description or "",
                conference.location or "",
            ]
        ).lower()

        found: list[str] = []
        for tag, markers in self.KEYWORD_RULES.items():
            if any(marker in source for marker in markers):
                found.append(tag)

        if conference.keywords:
            existing = [item.strip() for item in conference.keywords.split(",") if item.strip()]
            for item in existing:
                if item not in found:
                    found.append(item)

        return ", ".join(found)
