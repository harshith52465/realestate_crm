from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property-list'),
    path('add/', views.property_add, name='property-add'),
    path('<int:pk>/', views.property_detail, name='property-detail'),
    path('<int:pk>/edit/', views.property_edit, name='property-edit'),
    path('<int:pk>/delete/', views.property_delete, name='property-delete'),
    path('<int:pk>/enquiry/', views.property_enquiry, name='property-enquiry'),
]
