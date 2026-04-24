import time
from django.utils.deprecation import MiddlewareMixin
from .metrics import api_requests_total, request_latency


class PrometheusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            latency = time.time() - request.start_time
            api_requests_total.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code
            ).inc()
            request_latency.labels(
                method=request.method,
                endpoint=request.path
            ).observe(latency)
        return response