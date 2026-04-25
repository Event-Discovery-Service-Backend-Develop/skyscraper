from django.conf import settings
from django.db import models


class Conference(models.Model):
    wikicfp_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=1024, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True, db_index=True)
    location = models.CharField(max_length=256, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True, db_index=True)
    url = models.URLField(null=True, blank=True)
    raw_html = models.TextField(null=True, blank=True)
    raw_description = models.TextField(null=True, blank=True)
    clean_description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=512, null=True, blank=True)
    event_date_raw = models.CharField(max_length=128, null=True, blank=True)
    deadline_raw = models.CharField(max_length=128, null=True, blank=True)
    is_processed = models.BooleanField(default=False, db_index=True)
    last_collected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conferences"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_processed", "-event_date"], name="conf_proc_event_idx"),
            models.Index(fields=["-event_date", "-id"], name="conf_event_id_idx"),
            models.Index(fields=["deadline", "is_processed"], name="conf_deadline_proc_idx"),
        ]

    def __str__(self) -> str:
        return self.title or self.wikicfp_id


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "conference")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.conference_id}"
