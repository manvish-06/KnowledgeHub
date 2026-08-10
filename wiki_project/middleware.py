class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Request received:", request.path)
        response = self.get_response(request)
        print("Response returned")
        return response

    

