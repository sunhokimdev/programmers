class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/swagger"):
            if not request.META.get("HTTP_AUTHORIZATION"):
                request.META["HTTP_AUTHORIZATION"] = (
                    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MjU3OTMzOTN9.8g5lgHvs-cyfe1037uW_rLwhAhE_nCyGIIqFn73PN8I"
                )
            return self.get_response(request)

        response = self.get_response(request)
        return response
