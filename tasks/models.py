from django.db import models
from django.contrib.auth.models import User
from leads.models import Lead
from properties.models import Property


class Task(models.Model):

    TASK_TYPE_CHOICES = (
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('site_visit', 'Site Visit'),
        ('follow_up', 'Follow Up'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='tasks')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)

    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    note = models.TextField(blank=True)

    due_date = models.DateTimeField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_type} - {self.lead.name}"

