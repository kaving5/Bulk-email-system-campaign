from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models


class Recipient(models.Model):
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Recipient email address"
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional recipient name"
    )

    is_subscribed = models.BooleanField(
        default=True,
        help_text="Whether the user is subscribed to receive emails"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recipient'
        verbose_name_plural = 'Recipients'

    # def clean(self):
    #     """
    #     Model-level validation.
    #     Runs on full_clean().
    #     """
    #     if self.email:
    #         self.email = self.email.lower().strip()

    #     if not self.is_subscribed and self.pk is None:
    #         raise ValidationError(
    #             "New recipients must be subscribed by default."
    #         )

    def __str__(self):
        return self.email
