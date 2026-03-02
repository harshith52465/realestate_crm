from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_type', 'lead', 'assigned_to', 'due_date', 'is_completed')
    list_filter = ('task_type', 'is_completed')

