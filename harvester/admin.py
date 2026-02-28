from django.contrib import admin
from .models import Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ("openalex_id", "title", "publication_year", "created_at")
    list_filter = ("publication_year",)
    search_fields = ("openalex_id", "title", "doi")
