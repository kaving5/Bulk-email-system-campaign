


from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from .campaign import Campaign

class CampaignDeliveryLog(models.Model):
    class Status(models.TextChoices):
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="delivery_logs"
    )

    recipient_email = models.EmailField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices
    )

    failure_reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["campaign", "status"]),
        ]
        verbose_name = "Campaign Delivery Log"
        verbose_name_plural = "Campaign Delivery Logs"

    def __str__(self):
        return f"{self.recipient_email} - {self.status}"