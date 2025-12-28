from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Campaign(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    name = models.CharField(
        max_length=255,
        help_text="Internal name for the campaign"
    )

    subject = models.CharField(
        max_length=255,
        help_text="Email subject line"
    )

    content = models.TextField(
        help_text="Email content (plain text or HTML)"
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the campaign should be executed"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campaigns'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    # def clean(self):
    #     if self.status == self.Status.SCHEDULED:
    #         if not self.scheduled_at:
    #             raise ValidationError({
    #                 "scheduled_at": "Scheduled time is required when status is SCHEDULED."
    #             })

    #         if self.scheduled_at <= timezone.now():
    #             raise ValidationError({
    #                 "scheduled_at": "Scheduled time must be in the future."
    #             })

    def __str__(self):
        return f"{self.name} ({self.status})"
