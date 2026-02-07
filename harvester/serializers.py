from rest_framework import serializers
from .models import Work


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ["id", "openalex_id", "title", "doi", "publication_year", "keywords", "created_at"]
