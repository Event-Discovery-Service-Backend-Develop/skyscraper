from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConferenceViewSet, conference_list, conference_detail, add_to_favorites, remove_from_favorites, favorites_list

router = DefaultRouter()
router.register(r"conferences", ConferenceViewSet, basename="conference")

urlpatterns = [
    path("", include(router.urls)),
    path("web/", conference_list, name="conference_list"),
    path("web/<int:pk>/", conference_detail, name="conference_detail"),
    path("web/<int:pk>/add_favorite/", add_to_favorites, name="add_favorite"),
    path("web/<int:pk>/remove_favorite/", remove_from_favorites, name="remove_favorite"),
    path("favorites/", favorites_list, name="favorites_list"),
]
