from django.contrib.auth import get_user_model, login


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            User = get_user_model()
            user = (
                User.objects.filter(is_active=True, is_superuser=True).order_by("id").first()
                or User.objects.filter(is_active=True).order_by("id").first()
            )
            if user:
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return self.get_response(request)
