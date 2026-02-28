from django.urls import path
from . import views

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student-list'),
    path('create/', views.StudentCreateView.as_view(), name='student-create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('<int:pk>/update/', views.StudentUpdateView.as_view(), name='student-update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('import/', views.import_students, name='student-import'),
    path('export/', views.export_students, name='student-export'),
    path('debts/', views.DebtListView.as_view(), name='student-debts'),
    path('debts/add/', views.DebtCreateView.as_view(), name='debt-add'),
    path('debts/<int:pk>/', views.DebtDetailView.as_view(), name='debt-detail'),
    path('debts/<int:pk>/edit/', views.DebtUpdateView.as_view(), name='debt-update'),
    path('debts/<int:pk>/delete/', views.DebtDeleteView.as_view(), name='debt-delete'),
]