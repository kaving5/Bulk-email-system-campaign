import logging
from celery import shared_task
from django.utils import timezone

from apps.campaigns.models import Campaign, Recipient
from apps.campaigns.tasks.email_tasks import send_email_task

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def execute_campaign_task(self, campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        logger.error(f"Campaign not found | campaign_id={campaign_id}")
        return

    logger.info(
        f"Campaign execution started | campaign_id={campaign_id} | time={timezone.now()}"
    )

    try:
        campaign.status = Campaign.Status.IN_PROGRESS
        campaign.save(update_fields=["status"])

        recipients = list(
            Recipient.objects
            .filter(is_subscribed=True)
            .values_list("email", flat=True)
        )

        if not recipients:
            logger.warning(
                f"No subscribed recipients | campaign_id={campaign_id}"
            )
            campaign.status = Campaign.Status.COMPLETED
            campaign.save(update_fields=["status"])
            return

        send_email_task.delay(
            campaign_id=campaign.id,
            recipients=recipients,
            subject=campaign.subject,
            content=campaign.content,
        )

        logger.info(
            f"Campaign email task triggered | campaign_id={campaign_id} | recipients={len(recipients)}"
        )

    except Exception as exc:
        logger.exception(
            f"Campaign execution failed | campaign_id={campaign_id} | error={exc}"
        )
        campaign.status = Campaign.Status.FAILED  # optional enum
        campaign.save(update_fields=["status"])
