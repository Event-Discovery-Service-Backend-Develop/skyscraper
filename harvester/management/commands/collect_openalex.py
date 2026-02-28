import json
import re
import time
from django.core.management.base import BaseCommand
from django.conf import settings
import httpx
from harvester.models import Work


def openalex_id_from_url(url):
    if not url:
        return None
    m = re.search(r"/([A-Z]\d+)$", url.rstrip("/"))
    return m.group(1) if m else None


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
]


class Command(BaseCommand):
    help = "Fetch works from OpenAlex API and store in DB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=2)
        parser.add_argument("--per-page", type=int, default=50)
        parser.add_argument("--delay", type=float, default=1.0)

    def handle(self, *args, **options):
        max_pages = options["pages"]
        per_page = options["per_page"]
        delay = options["delay"]
        base_url = settings.OPENALEX_BASE_URL
        added = 0
        total = 0
        for page in range(1, max_pages + 1):
            headers = {"User-Agent": USER_AGENTS[page % len(USER_AGENTS)]}
            try:
                with httpx.Client() as client:
                    resp = client.get(
                        f"{base_url}/works",
                        params={"page": page, "per-page": per_page, "sort": "publication_date:desc"},
                        headers=headers,
                        timeout=30.0,
                    )
                    resp.raise_for_status()
            except httpx.HTTPError as e:
                self.stdout.write(self.style.WARNING(f"Page {page} error: {e}, skip"))
                continue
            try:
                data = resp.json()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Page {page} json error: {e}"))
                continue
            results = data.get("results") or []
            for item in results:
                total += 1
                oid = openalex_id_from_url(item.get("id"))
                if not oid:
                    continue
                if Work.objects.filter(openalex_id=oid).exists():
                    continue
                title = (item.get("title") or "").strip() or None
                doi = None
                if item.get("doi"):
                    d = item["doi"]
                    doi = d if isinstance(d, str) else (d.get("doi") if isinstance(d, dict) else None)
                pub_year = None
                if item.get("publication_year") is not None:
                    try:
                        pub_year = int(item["publication_year"])
                    except (ValueError, TypeError):
                        pass
                Work.objects.create(
                    openalex_id=oid,
                    title=title,
                    doi=doi,
                    publication_year=pub_year,
                    raw_json=json.dumps(item, ensure_ascii=False),
                )
                added += 1
            if page < max_pages and delay > 0:
                time.sleep(delay)
        self.stdout.write(self.style.SUCCESS(f"Processed: {total}, added: {added}"))
