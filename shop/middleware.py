from __future__ import annotations

from django.http import HttpResponse


class SimpleCorsMiddleware:
    """Permit cross-origin requests for the API so the WKWebView bundle can call the backend."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Short-circuit CORS preflight requests.
        if request.method == "OPTIONS":
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)

        origin = request.headers.get("Origin") or "null"
        response["Access-Control-Allow-Origin"] = "*" if origin == "null" else origin
        response["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
