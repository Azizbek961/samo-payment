from django.urls import path
from . import views
from .autocomplete import StudentAutoComplete

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('yangi/', views.PaymentCreateView.as_view(), name='payment-create'),

    # AUTOCOMPLETE
    path("student-autocomplete/", StudentAutoComplete.as_view(), name="student-autocomplete"),

    path("<int:pk>/print/", views.payment_print_receipt, name="payment-print-receipt"),
    path('<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment-delete'),
]