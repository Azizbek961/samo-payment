from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_page, name='reports'),
    path('export/excel/', views.export_payments_excel, name='reports-export-excel'),
    path('export/pdf/', views.export_payments_pdf, name='reports-export-pdf'),
]