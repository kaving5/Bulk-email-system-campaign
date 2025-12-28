from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.campaigns.models import Campaign
from apps.campaigns.tasks.campaign_tasks import execute_campaign_task


class CampaignSchedulerService:

    @staticmethod
    def schedule(campaign: Campaign):
        if campaign.status != Campaign.Status.DRAFT:
            raise ValidationError(
                "Only campaigns in DRAFT status can be scheduled."
            )

        if not campaign.scheduled_at:
            raise ValidationError(
                "Scheduled time must be set before scheduling."
            )

        if campaign.scheduled_at <= timezone.now():
            raise ValidationError(
                "Scheduled time must be in the future."
            )

        
        campaign.status = Campaign.Status.SCHEDULED
        campaign.save(update_fields=["status"])

        execute_campaign_task.apply_async(
            args=[campaign.id],
            eta=campaign.scheduled_at
        )
