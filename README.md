# Bulk Email Campaign Management System

## Overview
This project is a production-grade Bulk Email Campaign Management System built using Django, Celery, Redis, and PostgreSQL.

The system enables admins to:
- Create and manage email campaigns
- Upload recipients in bulk using CSV
- Schedule campaigns for future execution
- Send emails efficiently to large recipient lists
- Track delivery status for each email
- View campaign dashboards and delivery logs
- Generate and email campaign summary reports

## Why Django Admin instead of a separate frontend?
Initially, the plan was to build a client-side application using **Angular**.  
However, the assessment clearly mentions that:

*“The frontend can be minimal — basic HTML forms and tables are sufficient.”*

Considering this:
- The application is meant only for **admins**
- No public user-facing UI is required(End user is not going to involved)
- Django Admin already provides CRUD, filtering, searching, and forms


This approach still keeps the backend APIs and services reusable if a frontend like Angular is added later.

---

## Technology Choices 

### Django
- Provides a stable and mature backend framework
- Built-in Admin panel speeds up development
- Strong ORM and validation support
- Well-suited for admin-based workflows

### Celery
- Email sending is a time-consuming operation
- Running it synchronously would block the server
- Celery allows emails to be sent in the background
- Supports retries and failure handling
- Makes the system scalable for large recipient lists

### Redis
- Used as a message broker for Celery
- Lightweight and easy to configure locally
- Reliable for background task execution

### PostgreSQL
- More suitable for production than SQLite
- Handles concurrent writes well (important for delivery logs)
- Scales better with larger datasets
- Ensures data consistency and integrity

### Gmail SMTP (Demo purpose)
- Easy to configure for local testing
- Commonly used and well-documented
- For demo purposes only (daily limits apply)

In real production scenarios, this can be replaced with services like:
- Amazon SES
- SendGrid
- Mailgun

---

## Project Structure

backend/
├── apps/
│   └── campaigns/
│       ├── admin/
│       ├── models/
│       ├── services/
│       ├── tasks/
│       └── templates/
├── server/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
└── manage.py

---

## Core Models

### Campaign
- name
- subject
- content (plain text or HTML)
- scheduled_at
- status (Draft, Scheduled, In Progress, Completed)
- created_by
- created_at / updated_at

### Recipient
- name
- email (unique)
- is_subscribed
- created_at

### CampaignDeliveryLog
- campaign
- recipient_email
- status (Sent / Failed)
- failure_reason
- timestamp



## Workflow (High Level)

1. Admin creates campaign (Draft)
2. Recipients uploaded via CSV
3. Campaign scheduled
4. Celery executes campaign at scheduled time
5. Emails sent in batches
6. Delivery logs recorded
7. Campaign marked Completed
8. Summary report generated and emailed

---

## Batch Email Sending
To handle large recipient lists efficiently:
- Recipients are split into smaller batches
- Each batch is processed by a separate Celery task
- Multiple workers can run in parallel

This avoids:
- SMTP connection drops
- Provider throttling
- Long-running single tasks

---

## Dashboard & Reporting
Using Django Admin:
- Campaign list shows sent / failed counts
- Status summary like `88 / 100 sent`
- Clicking a campaign shows detailed delivery logs
- After completion, a CSV summary report is generated and emailed

---

## Run Locally

### 1. Create virtual environment
python -m venv venv  
source venv/bin/activate  

### 2. Install dependencies
pip install -r requirements.txt  

### 3. PostgreSQL setup
- Install PostgreSQL
- Create database:
  CREATE DATABASE email_campaign_db;
- Update database credentials in `settings.py`

### 4. Apply migrations
python manage.py migrate  

### 5. Create admin user
python manage.py createsuperuser  

### 6. Start Django server
python manage.py runserver  

### 7. Start Redis
redis-server  

### 8. Start Celery worker
celery -A server worker -l info

### 9. Once the server is up and run
Admin panel --  http://127.0.0.1:8000/admin/

### 10. Login To Admin Panel
With createsuperuser credentials

### 11. Option Bulk Recipient Upload
Go to Recipients in the admin panel
On the recipient list page, use the Actions dropdown
Select “Upload Recipients via CSV”

## 12.Option Scheduling a Campaign
From the Campaign list view, select a campaign
Use the Actions dropdown
Choose “Schedule Campaign”
Provide a future date and time


---




## Demo / Testing Mode
For testing without sending real emails:
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

Emails will be printed in the console.

---

## Notes
- Gmail SMTP has strict daily sending limits
- The system handles failures gracefully and logs them properly

---

## Conclusion
This project focuses on:
- Clean backend structure
- Proper separation of concerns
- Scalable email execution
- Realistic handling of bulk email scenarios

The design allows easy extension in the future with a full frontend or a production email service.
