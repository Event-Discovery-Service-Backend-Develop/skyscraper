from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def root(request):
    return render(request, "index.html")

def health(request):
    return JsonResponse({"status": "healthy"})

urlpatterns = [
    path("", root),
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/", include("harvester.urls")),
]
