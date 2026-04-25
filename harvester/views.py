from datetime import date
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Conference, Favorite
from .serializers import ConferenceSerializer
from .pagination import StandardResultsSetPagination


class ConferenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConferenceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["event_date", "deadline"]
    search_fields = ["title", "keywords", "location"]
    ordering_fields = ["event_date", "deadline", "title", "created_at", "id"]
    ordering = ["-event_date", "-id"]

    def get_queryset(self):
        qs = Conference.objects.all().order_by("-event_date", "-id")

        year = self.request.query_params.get("year")
        if year:
            try:
                qs = qs.filter(event_date__year=int(year))
            except ValueError:
                pass

        search = self.request.query_params.get("search")
        if search:
            # Используем полнотекстовый поиск, если база — PostgreSQL
            if connection.vendor == "postgresql":
                vector = (
                    SearchVector("title", weight="A")
                    + SearchVector("keywords", weight="B")
                    + SearchVector("location", weight="C")
                )
                query = SearchQuery(search)
                qs = (
                    qs.annotate(search_rank=SearchRank(vector, query))
                    .filter(search_rank__gt=0)
                    .order_by("-search_rank", "-event_date", "-id")
                )
            else:
                qs = qs.filter(
                    Q(title__icontains=search) | 
                    Q(keywords__icontains=search) | 
                    Q(location__icontains=search)
                )

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(keywords__icontains=tag)

        processed = self.request.query_params.get("processed")
        if processed in {"true", "false"}:
            qs = qs.filter(is_processed=(processed == "true"))

        return qs


class DiscoveryMetaAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "filters": {
                    "supported_tags": ["AI", "Security", "Physics", "Data Science", "Software Engineering"],
                    "query_params": ["page", "page_size", "search", "year", "tag", "ordering", "processed"],
                }
            }
        )


def conference_list(request):
    """Веб-страница со списком конференций"""
    conferences = Conference.objects.all().order_by("-event_date")
    
    search = request.GET.get('search')
    if search:
        conferences = conferences.filter(
            Q(title__icontains=search) | Q(keywords__icontains=search) | Q(location__icontains=search)
        )
    
    year = request.GET.get('year')
    if year:
        conferences = conferences.filter(event_date__year=year)
    
    paginator = Paginator(conferences, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'conferences.html', {
        'page_obj': page_obj,
        'search': search,
        'year': year,
    })


def conference_detail(request, pk):
    """Детальная страница конференции"""
    conference = get_object_or_404(Conference, pk=pk)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, conference=conference).exists()
    
    keywords_list = []
    if conference.keywords:
        keywords_list = [keyword.strip() for keyword in conference.keywords.split(",") if keyword.strip()]

    deadline_status = None
    if conference.deadline:
        today = date.today()
        if conference.deadline < today:
            deadline_status = "expired"
        elif (conference.deadline - today).days <= 30:
            deadline_status = "soon"
        else:
            deadline_status = "active"

    return render(
        request,
        "conference_detail.html",
        {
            "conference": conference,
            "is_favorite": is_favorite,
            "keywords_list": keywords_list,
            "deadline_status": deadline_status,
        },
    )


@login_required
def add_to_favorites(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    Favorite.objects.get_or_create(user=request.user, conference=conference)
    messages.success(request, 'Конференция добавлена в избранное.')
    return redirect('conference_detail', pk=pk)


@login_required
def remove_from_favorites(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    Favorite.objects.filter(user=request.user, conference=conference).delete()
    messages.success(request, 'Конференция удалена из избранного.')
    return redirect('conference_detail', pk=pk)


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('conference')
    conferences = [f.conference for f in favorites]
    
    paginator = Paginator(conferences, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'favorites.html', {'page_obj': page_obj})
