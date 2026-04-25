from rest_framework import serializers
from .models import Conference


class ConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        fields = [
            "id",
            "wikicfp_id",
            "title",
            "event_date",
            "location",
            "deadline",
            "url",
            "clean_description",
            "keywords",
            "is_processed",
            "created_at",
            "updated_at",
        ]
