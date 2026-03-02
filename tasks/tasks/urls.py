from django.urls import path
from .views import task_list, task_add, task_edit, task_delete

urlpatterns = [
    path('tasks/', task_list, name='task-list'),
    path('tasks/add/', task_add, name='task-add'),
    path('tasks/<int:pk>/edit/', task_edit, name='task-edit'),
    path('tasks/<int:pk>/delete/', task_delete, name='task-delete'),
]

