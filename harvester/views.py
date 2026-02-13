from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Work
from .serializers import WorkSerializer


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Work.objects.all()
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
        return qs.order_by("-created_at")
