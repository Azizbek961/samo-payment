from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('yangi/', views.PaymentCreateView.as_view(), name='payment-create'),
    path("<int:pk>/print/", views.payment_print_receipt, name="payment-print-receipt"),
    # path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    # path('<int:pk>/chek/', views.print_receipt_view, name='payment-print-receipt'),
    path('<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment-delete'),
]