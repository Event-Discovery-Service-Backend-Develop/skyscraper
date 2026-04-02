from django.core.management.base import BaseCommand
from harvester.services import ProcessingService


class Command(BaseCommand):
    help = "Normalize raw conference data and fill tags"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)

    def handle(self, *args, **options):
        service = ProcessingService()
        processed = service.process_pending(limit=options["limit"] or 200)
        self.stdout.write(self.style.SUCCESS(f"Processed: {processed}"))