from django.contrib import admin, messages
from apps.campaigns.models import Recipient
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path
from apps.campaigns.models import Campaign
from apps.campaigns.services.recipient_csv_importer import RecipientCSVImporter

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'is_subscribed',
        'created_at',
    )

    list_filter = (
        'is_subscribed',
        'created_at',
    )

    search_fields = (
        'email',
        'name',
    )

    ordering = ('-created_at',)

    readonly_fields = ('created_at',)


    actions = ['go_to_csv_upload']

    # ✅ 1. Register PRIVATE admin URL
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:campaign_id>/upload-recipients/',
                self.admin_site.admin_view(self.upload_recipients_view),
                name='campaign-upload-recipients',
            ),
        ]
        return custom_urls + urls

    # ✅ 2. REAL admin view → renders HTML
    def upload_recipients_view(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)

        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")

            if not csv_file:
                self.message_user(
                    request,
                    "Please upload a CSV file.",
                    level=messages.ERROR
                )
                return redirect(request.path)

            service = RecipientCSVImporter()
            result = service.import_csv(csv_file)

            self.message_user(
                request,
                f"{result['created']} created, "
                f"{result['updated']} updated, "
                f"{result['skipped']} skipped, "
                f"{result['errors']} errors.",
                level=messages.SUCCESS
            )

            return redirect("..")

        return render(
            request,
            "admin/upload_recipients.html",
            {"campaign": campaign}
        )

    # ✅ 3. Admin action ONLY redirects
    def go_to_csv_upload(self, request, queryset):
        # if queryset.count() != 1:
        #     self.message_user(
        #         request,
        #         "Please select exactly one campaign.",
        #         level=messages.ERROR
        #     )
        #     return

        campaign = queryset.first()
        return redirect(f"{campaign.id}/upload-recipients/")

    go_to_csv_upload.short_description = "Upload Recipients via CSV"
