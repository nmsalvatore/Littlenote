class BackButtonMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            included_paths = ["/notes/"]
            if any(request.path.startswith(path) for path in included_paths):
                current_url = request.get_full_path()
                previous_url = request.session.get("current_url")

                if previous_url and previous_url != current_url:
                    request.session["previous_url"] = previous_url

                request.session["current_url"] = current_url

        response = self.get_response(request)
        return response
