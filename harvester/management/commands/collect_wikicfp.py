from django.core.management.base import BaseCommand
from harvester.services import CrawlerService


class Command(BaseCommand):
    help = "Fetch conferences from WikiCFP and upsert into DB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=2)
        parser.add_argument("--per-page", type=int, default=50)

    def handle(self, *args, **options):
        service = CrawlerService()
        result = service.collect(pages=options["pages"], per_page=options["per_page"])
        self.stdout.write(self.style.SUCCESS(f"Processed: {result['collected']}, created: {result['created']}, updated: {result['updated']}"))