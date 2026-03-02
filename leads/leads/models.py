from django.db import models

from django.db import models
from django.contrib.auth.models import User

from properties.models import Property


class Lead(models.Model):

    STATUS_CHOICES = (
        ('fresh', 'Fresh'),
        ('returning', 'Returning'),
        ('untouched', 'Untouched'),
        ('closed', 'Closed'),
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, default="")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='fresh'
    )

    source = models.CharField(
        max_length=100,
        help_text="Website, Walk-in, Referral, Ads"
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    property = models.ForeignKey(
    Property,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


# Create your models here.
