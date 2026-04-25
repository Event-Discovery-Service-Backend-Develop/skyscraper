from django.core.management.base import BaseCommand
from harvester.services import CrawlerService


class Command(BaseCommand):
    help = "Fetch conferences from WikiCFP and upsert into DB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=2)
        parser.add_argument("--per-page", type=int, default=50)
        parser.add_argument("--delay-min", type=float, default=0.6)
        parser.add_argument("--delay-max", type=float, default=2.4)
        parser.add_argument("--proxy", type=str, default=None, help="Optional proxy URL, e.g. http://user:pass@host:port")

    def handle(self, *args, **options):
        service = CrawlerService(
            delay_min=options["delay_min"],
            delay_max=options["delay_max"],
            proxy=options["proxy"],
        )
        result = service.collect(pages=options["pages"], per_page=options["per_page"])
        self.stdout.write(self.style.SUCCESS(f"Processed: {result['collected']}, created: {result['created']}, updated: {result['updated']}"))