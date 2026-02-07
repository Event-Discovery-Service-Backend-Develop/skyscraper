from django.core.management.base import BaseCommand
from harvester.models import Work
from harvester.processor import extract_keywords_from_raw


class Command(BaseCommand):
    help = "Prohodit po rabotam i zapolnyaet keywords iz raw_json"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)

    def handle(self, *args, **options):
        qs = Work.objects.filter(keywords__isnull=True).exclude(raw_json="")
        if options["limit"]:
            qs = qs[: options["limit"]]
        cnt = 0
        for w in qs:
            kw = extract_keywords_from_raw(w.raw_json)
            if kw:
                w.keywords = kw
                w.save(update_fields=["keywords"])
                cnt += 1
        self.stdout.write(self.style.SUCCESS(f"Obrabotano: {cnt}"))
