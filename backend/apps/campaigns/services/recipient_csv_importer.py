import csv
from io import TextIOWrapper
from typing import Dict

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.campaigns.models import Recipient


class RecipientCSVImporter:

    REQUIRED_HEADERS = {"email", "name", "is_subscribed"}

    def import_csv(self, csv_file) -> Dict[str, int]:
        summary = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.DictReader(decoded_file)

        self._validate_headers(reader.fieldnames)

        existing_recipients = {
            r.email: r for r in Recipient.objects.all()
        }

        seen_emails = set()
        to_create = []
        to_update = []

        for row in reader:
            try:
                email = self._normalize_email(row.get("email"))

                if not email or email in seen_emails:
                    summary["skipped"] += 1
                    continue

                seen_emails.add(email)

                is_subscribed = self._parse_boolean(
                    row.get("is_subscribed")
                )
                name = (row.get("name") or "").strip()

                if email in existing_recipients:
                    recipient = existing_recipients[email]
                    if (
                        recipient.name != name
                        or recipient.is_subscribed != is_subscribed
                    ):
                        recipient.name = name
                        recipient.is_subscribed = is_subscribed
                        recipient.full_clean()
                        to_update.append(recipient)
                        summary["updated"] += 1
                    else:
                        summary["skipped"] += 1
                else:
                    recipient = Recipient(
                        email=email,
                        name=name,
                        is_subscribed=is_subscribed
                    )
                    recipient.full_clean()
                    to_create.append(recipient)
                    summary["created"] += 1

            except ValidationError:
                summary["errors"] += 1

        self._bulk_persist(to_create, to_update)

        return summary


    def _validate_headers(self, headers):
        if not headers:
            raise ValidationError("CSV file is empty or invalid.")

        missing = self.REQUIRED_HEADERS - set(headers)
        if missing:
            raise ValidationError(
                f"Missing required CSV columns: {missing}"
            )

    def _normalize_email(self, email: str) -> str:
        if not email:
            raise ValidationError("Email is required.")
        return email.strip().lower()

    def _parse_boolean(self, value: str) -> bool:
        if value is None:
            raise ValidationError("is_subscribed is required")

        value = str(value).strip().lower()

        if value == "true":
            return True
        if value == "false":
            return False

        raise ValidationError(
            "is_subscribed must be either 'true' or 'false'"
        )


    def _bulk_persist(self, to_create, to_update):
        with transaction.atomic():
            if to_create:
                Recipient.objects.bulk_create(
                    to_create,
                    batch_size=500
                )
            if to_update:
                Recipient.objects.bulk_update(
                    to_update,
                    fields=["name", "is_subscribed"],
                    batch_size=500
                )
