from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Conference, Favorite
from .serializers import ConferenceSerializer
from .pagination import StandardResultsSetPagination


class ConferenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConferenceSerializer
    # permission_classes = [IsAuthenticated]  # Временно отключено для демонстрации
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
            qs = qs.filter(
                Q(title__icontains=search) | Q(keywords__icontains=search) | Q(location__icontains=search)
            )

        return qs


def conference_list(request):
    """Веб-страница со списком конференций"""
    conferences = Conference.objects.all().order_by("-event_date")
    
    # Фильтры
    search = request.GET.get('search')
    if search:
        conferences = conferences.filter(
            Q(title__icontains=search) | Q(keywords__icontains=search) | Q(location__icontains=search)
        )
    
    year = request.GET.get('year')
    if year:
        conferences = conferences.filter(event_date__year=year)
    
    # Пагинация
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
    return render(request, 'conference_detail.html', {'conference': conference, 'is_favorite': is_favorite})


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
    
    # Пагинация
    paginator = Paginator(conferences, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'favorites.html', {'page_obj': page_obj})
