from django.contrib.auth import get_user_model, login
from django.db.utils import OperationalError, ProgrammingError


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # login shart emas bo‘lsa darhol chiqamiz
        if request.user.is_authenticated:
            return self.get_response(request)

        try:
            User = get_user_model()

            # ❗ safe query (DB crash bo‘lmaydi)
            user = User.objects.filter(
                is_active=True,
                is_superuser=True
            ).only("id").first()

            if user:
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        except (OperationalError, ProgrammingError):
            # DB hali ready emas → ignore
            pass

        return self.get_response(request)