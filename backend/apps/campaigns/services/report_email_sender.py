from django.core.mail import EmailMessage
from django.conf import settings

from server.settings import EMAIL_HOST_USER


class CampaignReportEmailSender:

    def send_report(self, campaign, csv_content):
        if not campaign.created_by or not campaign.created_by.email:
            return  

        email = EmailMessage(
            subject=f"Campaign Report: {campaign.name}",
            body="Please find the attached campaign delivery report.",
            from_email=EMAIL_HOST_USER,
            to=[campaign.created_by.email],
        )

        email.attach(
            filename=f"{campaign.name}_report.csv",
            content=csv_content,
            mimetype="text/csv",
        )

        email.send(fail_silently=False)
