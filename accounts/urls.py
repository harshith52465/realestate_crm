from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.customer_register, name='register'),
    path('agents/add/', views.agent_create, name='agent-create'),
    path('agents/', views.agent_list, name='agent-list'),
    path('agents/<int:agent_id>/', views.agent_detail, name='agent-detail'),
    path('agents/<int:agent_id>/assign/', views.agent_assign_property, name='agent-assign-property'),
]




