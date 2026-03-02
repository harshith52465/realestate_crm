from django.urls import path

from dashboard.views import dashboard_home, activity_list


urlpatterns = [
    path('dashboard/', dashboard_home,
     name='dashboard'),
    path('activities/', activity_list, name='activity-list'),
]
