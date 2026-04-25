from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import path, include
import importlib.util
from harvester.models import Conference
from harvester.metrics import conferences_total, processed_conferences

try:
    from prometheus_client import generate_latest  # type: ignore
except ImportError:  # pragma: no cover
    generate_latest = None

HAS_DRF_SPECTACULAR = importlib.util.find_spec("drf_spectacular") is not None
HAS_ALLAUTH = importlib.util.find_spec("allauth") is not None
HAS_SIMPLEJWT = importlib.util.find_spec("rest_framework_simplejwt") is not None
if HAS_DRF_SPECTACULAR:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
if HAS_SIMPLEJWT:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def root(request):
    return render(request, "index.html")

def health(request):
    return JsonResponse({"status": "healthy"})

def metrics(request):
    if generate_latest is None:
        return JsonResponse({"metrics": "prometheus_client is not installed"}, status=503)
    conferences_total.set(Conference.objects.count())
    processed_conferences.set(Conference.objects.filter(is_processed=True).count())
    return HttpResponse(generate_latest(), content_type='text/plain; charset=utf-8')

def api_test(request):
    return render(request, "api_test.html")

urlpatterns = [
    path("", root),
    path("health/", health),
    path("metrics/", metrics),
    path("api-test/", api_test),
    path("admin/", admin.site.urls),
    path("api/", include("harvester.urls")),
    path("harvester/", include("harvester.urls")),
]
if HAS_SIMPLEJWT:
    urlpatterns += [
        path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    ]
if HAS_DRF_SPECTACULAR:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ]
if HAS_ALLAUTH:
    urlpatterns += [path("accounts/", include("allauth.urls"))]
