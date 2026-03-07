from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def root(request):
    return render(request, "index.html")

def health(request):
    return JsonResponse({"status": "healthy"})

def api_test(request):
    return render(request, "api_test.html")

urlpatterns = [
    path("", root),
    path("health/", health),
    path("api-test/", api_test),
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("harvester.urls")),
    path("harvester/", include("harvester.urls")),
    path("accounts/", include("allauth.urls")),
]
