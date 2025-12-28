from django.contrib import admin, messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path

from apps.campaigns.models import Campaign
from apps.campaigns.services.recipient_csv_importer import RecipientCSVImporter
from apps.campaigns.services.campaign_scheduler import CampaignSchedulerService


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'total_recipients','sent_count','failed_count','progress_summary','scheduled_at', 'created_at')
    readonly_fields = ('status', 'created_at', 'updated_at', 'created_by')

    def total_recipients(self, obj):
        return obj.delivery_logs.count()

    def sent_count(self, obj):
        return obj.delivery_logs.filter(status="SENT").count()

    def failed_count(self, obj):
        return obj.delivery_logs.filter(status="FAILED").count()

    def progress_summary(self, obj):
        total = obj.delivery_logs.count()
        sent = obj.delivery_logs.filter(status="SENT").count()
        return f"{sent}/{total} sent" if total else "0/0"

    progress_summary.short_description = "Status Summary"

    def save_model(self, request, obj, form, change):
        """
        Automatically set created_by on first save
        """
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    
    #  Schedule Campaign action
    actions = ['schedule_campaign']

    def schedule_campaign(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one campaign to schedule.",
                level=messages.ERROR
            )
            return

        campaign = queryset.first()

        try:
            CampaignSchedulerService.schedule(campaign)
            self.message_user(
                request,
                "Campaign scheduled successfully.",
                level=messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                str(e),
                level=messages.ERROR
            )

    schedule_campaign.short_description = "Schedule Campaign"
