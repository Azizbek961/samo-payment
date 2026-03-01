from django_select2.views import AutoResponseView
from django.http import Http404
from students.models import Student  # adjust import to your real Student model

class StudentAutoComplete(AutoResponseView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise Http404

        qs = Student.objects.all()

        term = self.q  # typed text
        if term:
            # Adjust fields to match your Student model fields
            qs = qs.filter(
                # example: search by full_name or phone
                # If you don't have full_name, use first_name/last_name/etc.
                # You can combine multiple OR conditions via Q if needed
            )

        return qs