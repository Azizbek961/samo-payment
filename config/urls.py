from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
    path('students/', include('apps.students.urls')),
    path('payments/', include('apps.payments.urls')),
    path('reports/', include('apps.reports.urls')),
    path('printers/', include('apps.printers.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('', RedirectView.as_view(url='/dashboard/')),
    path("select2/", include("django_select2.urls")),
]