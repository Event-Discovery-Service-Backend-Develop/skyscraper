from django.db import models
from django.contrib.auth.models import User


class Conference(models.Model):
    wikicfp_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=1024, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True, db_index=True)
    location = models.CharField(max_length=256, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True, db_index=True)
    url = models.URLField(null=True, blank=True)
    raw_html = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conferences"
        ordering = ["-created_at"]


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'conference')
