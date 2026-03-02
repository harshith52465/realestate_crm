from django.urls import path
from .views import lead_list, lead_create, lead_update_status

urlpatterns = [
    path('leads/', lead_list, name='lead-list'),
    path('leads/add/', lead_create, name='lead-add'),
    path('leads/<int:pk>/status/', lead_update_status, name='lead-status'),
]
