from django.core.management.base import BaseCommand
from harvester.models import Conference
from harvester.processor import extract_keywords_from_html


class Command(BaseCommand):
    help = "Process conferences and fill keywords from raw_html"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)

    def handle(self, *args, **options):
        qs = Conference.objects.filter(keywords__isnull=True).exclude(raw_html="")
        if options["limit"]:
            qs = qs[: options["limit"]]
        cnt = 0
        for conf in qs:
            kw = extract_keywords_from_html(conf.raw_html)
            if kw:
                conf.keywords = kw
                conf.save(update_fields=["keywords"])
                cnt += 1
        self.stdout.write(self.style.SUCCESS(f"Processed: {cnt}"))