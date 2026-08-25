from playwright.sync_api import APIRequestContext, APIResponse


class StorefrontApi:
    """Client object that keeps API endpoints out of BDD glue code."""

    def __init__(self, request_context: APIRequestContext):
        self.request_context = request_context

    def get(self, path: str) -> APIResponse:
        return self.request_context.get(path)

    def post(self, path: str, data: dict[str, object]) -> APIResponse:
        return self.request_context.post(path, data=data)

    def delete(self, path: str) -> APIResponse:
        return self.request_context.delete(path)
