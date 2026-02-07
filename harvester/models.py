from django.db import models


class Work(models.Model):
    openalex_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=1024, null=True, blank=True)
    doi = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    publication_year = models.IntegerField(null=True, blank=True, db_index=True)
    raw_json = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "works"
        ordering = ["-created_at"]
