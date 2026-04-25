from django.contrib import admin
from .models import Conference


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ("wikicfp_id", "title", "event_date", "location", "deadline", "created_at")
    list_filter = ("event_date", "deadline")
    search_fields = ("wikicfp_id", "title", "location")
