from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from prometheus_client import generate_latest

def root(request):
    return render(request, "index.html")

def health(request):
    return JsonResponse({"status": "healthy"})

def metrics(request):
    return HttpResponse(generate_latest(), content_type='text/plain; charset=utf-8')

def api_test(request):
    return render(request, "api_test.html")

urlpatterns = [
    path("", root),
    path("health/", health),
    path("metrics/", metrics),
    path("api-test/", api_test),
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("harvester.urls")),
    path("harvester/", include("harvester.urls")),
    path("accounts/", include("allauth.urls")),
]
