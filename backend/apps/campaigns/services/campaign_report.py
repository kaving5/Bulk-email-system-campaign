import csv
from io import StringIO
from django.utils import timezone

from apps.campaigns.models import CampaignDeliveryLog


class CampaignReportService:

    def generate_csv_report(self, campaign):
        logs = CampaignDeliveryLog.objects.filter(campaign=campaign)

        total = logs.count()
        sent = logs.filter(status="SENT").count()
        failed = logs.filter(status="FAILED").count()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Campaign Name", campaign.name])
        writer.writerow(["Completed At", timezone.now()])
        writer.writerow(["Total Recipients", total])
        writer.writerow(["Sent", sent])
        writer.writerow(["Failed", failed])
        writer.writerow([])

        writer.writerow(
            ["Recipient Email", "Status", "Failure Reason", "Timestamp"]
        )

        for log in logs:
            writer.writerow([
                log.recipient_email,
                log.status,
                log.failure_reason or "",
                log.created_at,
            ])

        return output.getvalue()
