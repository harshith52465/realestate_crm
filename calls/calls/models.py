from django.db import models
from django.contrib.auth.models import User
from leads.models import Lead


class Call(models.Model):
    TYPE_CHOICES = (
        ("ivr", "IVR"),
        ("incoming", "Incoming"),
        ("outgoing", "Outgoing"),
        ("missed", "Missed"),
    )

    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    call_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    duration_seconds = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.lead.name if self.lead else "Unknown Lead"
        return f"{who} - {self.call_type}"
