from django_select2.views import AutoResponseView
from django.db.models import Q
from apps.students.models import Student   # TO'G'RISI

class StudentAutoComplete(AutoResponseView):

    def get_queryset(self):
        qs = Student.objects.all()

        if self.q:
            qs = qs.filter(
                Q(full_name__icontains=self.q) |
                Q(phone__icontains=self.q)
            )

        return qs