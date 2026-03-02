from django.urls import path
from .views import call_list, call_add

urlpatterns = [
    path("calls/", call_list, name="call-list"),
    path("calls/add/", call_add, name="call-add"),
]
