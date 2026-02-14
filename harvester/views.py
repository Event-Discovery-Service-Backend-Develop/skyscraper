from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Work
from .serializers import WorkSerializer
from .pagination import StandardResultsSetPagination


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["publication_year"]
    search_fields = ["title", "keywords"]
    ordering_fields = ["publication_year", "title", "created_at", "id"]
    ordering = ["-publication_year", "-id"]

    def get_queryset(self):
        qs = Work.objects.all().order_by("-publication_year", "-id")

        year = self.request.query_params.get("year")
        if year:
            try:
                qs = qs.filter(publication_year=int(year))
            except ValueError:
                pass

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(keywords__icontains=search)
            )

        return qs
