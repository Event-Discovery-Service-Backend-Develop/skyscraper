import re
import time
from django.core.management.base import BaseCommand
from django.conf import settings
import httpx
from bs4 import BeautifulSoup
from harvester.models import Conference
from harvester.processor import extract_conference_data


def wikicfp_id_from_url(url):
    if not url:
        return None
    m = re.search(r'/cfp/program\.id/(\d+)', url)
    return m.group(1) if m else None


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
]


class Command(BaseCommand):
    help = "Fetch conferences from WikiCFP and store in DB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=2)
        parser.add_argument("--per-page", type=int, default=50)
        parser.add_argument("--delay", type=float, default=1.0)

    def handle(self, *args, **options):
        max_pages = options["pages"]
        per_page = options["per_page"]
        delay = options["delay"]
        base_url = settings.WIKICFP_BASE_URL
        added = 0
        total = 0
        for page in range(1, max_pages + 1):
            headers = {"User-Agent": USER_AGENTS[page % len(USER_AGENTS)]}
            try:
                with httpx.Client() as client:
                    resp = client.get(
                        f"{base_url}/cfp/allcfp",
                        params={"page": page},
                        headers=headers,
                        timeout=30.0,
                    )
                    resp.raise_for_status()
            except httpx.HTTPError as e:
                self.stdout.write(self.style.WARNING(f"Page {page} error: {e}, skip"))
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.find_all('a', href=re.compile(r'/cfp/program\.id/\d+'))
            
            for link in links[:per_page]:
                total += 1
                url = link['href']
                wid = wikicfp_id_from_url(url)
                if not wid:
                    continue
                if Conference.objects.filter(wikicfp_id=wid).exists():
                    continue
                
                # Fetch detailed page
                try:
                    detail_resp = client.get(f"{base_url}{url}", headers=headers, timeout=30.0)
                    detail_resp.raise_for_status()
                    detail_html = detail_resp.text
                except httpx.HTTPError:
                    continue
                
                data = extract_conference_data(detail_html)
                
                Conference.objects.create(
                    wikicfp_id=wid,
                    title=data.get('title'),
                    event_date=data.get('event_date'),
                    location=data.get('location'),
                    deadline=data.get('deadline'),
                    url=data.get('url') or f"{base_url}{url}",
                    raw_html=detail_html,
                )
                added += 1
                
                if delay > 0:
                    time.sleep(delay)
            
            if page < max_pages and delay > 0:
                time.sleep(delay)
        
        self.stdout.write(self.style.SUCCESS(f"Processed: {total}, added: {added}"))