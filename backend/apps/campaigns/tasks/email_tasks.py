import logging
from celery import shared_task
from django.core.mail import send_mail
from apps.campaigns.models import CampaignDeliveryLog, Campaign
from apps.campaigns.models.recipient import Recipient
from server.settings import EMAIL_HOST_USER

from apps.campaigns.services.campaign_report import CampaignReportService
from apps.campaigns.services.report_email_sender import CampaignReportEmailSender

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, campaign_id, recipients, subject, content):
    campaign = Campaign.objects.get(id=campaign_id)
    logs = []

    logger.info(
        f"Email task started | campaign={campaign_id} | recipients={len(recipients)}"
    )

    for email in recipients:
        try:
            send_mail(
                subject=subject,
                message=content,
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            logs.append(
                CampaignDeliveryLog(
                    campaign_id=campaign_id,
                    recipient_email=email,
                    status=CampaignDeliveryLog.Status.SENT,
                )
            )

        except Exception as exc:
            logs.append(
                CampaignDeliveryLog(
                    campaign_id=campaign_id,
                    recipient_email=email,
                    status=CampaignDeliveryLog.Status.FAILED,
                    failure_reason=str(exc),
                )
            )

            logger.error(
                f" Email failed | campaign={campaign_id} | email={email} | error={exc}"
            )

    CampaignDeliveryLog.objects.bulk_create(logs, batch_size=100)

    logger.info(
        f"Email task completed | campaign={campaign_id}"
    )


    # campaign.status = Campaign.Status.COMPLETED
    # campaign.save(update_fields=["status"])


    total_recipients = Recipient.objects.filter(is_subscribed=True).count()
    logged = CampaignDeliveryLog.objects.filter(campaign_id=campaign_id).count()

    if logged >= total_recipients:
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = Campaign.Status.COMPLETED
        campaign.save(update_fields=["status"])


        # Area of  generate & send report
        report_service = CampaignReportService()
        csv_report = report_service.generate_csv_report(campaign)

        email_sender = CampaignReportEmailSender()
        email_sender.send_report(campaign, csv_report)