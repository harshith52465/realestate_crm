from django.urls import path
from .views import export_reports_excel, reports_home

urlpatterns = [
    path('reports/', reports_home, name='reports-home'),
    path('export/', export_reports_excel, name='export-reports'),

]
