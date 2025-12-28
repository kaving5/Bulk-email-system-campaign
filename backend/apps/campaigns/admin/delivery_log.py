from django.contrib import admin
from apps.campaigns.models import CampaignDeliveryLog


@admin.register(CampaignDeliveryLog)
class CampaignDeliveryLogAdmin(admin.ModelAdmin):
    list_display = (
        "campaign",
        "recipient_email",
        "status",
        "created_at",
    )

    list_filter = ("status", "campaign")
    search_fields = ("recipient_email",)
    ordering = ("-created_at",)
