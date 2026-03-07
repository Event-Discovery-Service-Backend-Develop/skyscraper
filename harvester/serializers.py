from rest_framework import serializers
from .models import Conference


class ConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        fields = ["id", "wikicfp_id", "title", "event_date", "location", "deadline", "url", "keywords", "created_at"]
