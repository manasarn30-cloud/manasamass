import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FAQ(models.Model):
    """
    SQL storage for Frequently Asked Questions.
    Powering both the FAQ help page and the AI Chatbot Knowledge Base.
    """
    CATEGORY_CHOICES = [
        ('Account & Authentication', 'Account & Authentication'),
        ('Streaming & Playback', 'Streaming & Playback'),
        ('Lists & Navigation', 'Lists & Navigation'),
        ('Platform Errors & Status Codes', 'Platform Errors & Status Codes'),
        ('Support & Technical Diagnostics', 'Support & Technical Diagnostics'),
    ]

    question = models.CharField(max_length=300, db_index=True)
    answer = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General')
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated search keywords for the chatbot search engine"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class SupportTicket(models.Model):
    """
    SQL storage for User Support Tickets.
    Created either via the web support form or escalated from the AI Chatbot.
    """
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    CATEGORY_CHOICES = [
        ('Account & Login', 'Account & Login'),
        ('Streaming & Playback', 'Streaming & Playback'),
        ('Movie Metadata / Missing Title', 'Movie Metadata / Missing Title'),
        ('Platform Error / Bug Report', 'Platform Error / Bug Report'),
        ('Billing & Subscription', 'Billing & Subscription'),
        ('General Inquiry', 'General Inquiry'),
    ]

    SOURCE_CHOICES = [
        ('Web Form', 'Web Form'),
        ('Chatbot Assistant', 'Chatbot Assistant'),
    ]

    reference_number = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        editable=False,
        help_text="Unique ticket identifier (e.g., SF-TICK-A1B2C3D4)"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets'
    )
    guest_email = models.EmailField(blank=True, null=True, help_text="Used for tickets submitted by unauthenticated guests")
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General Inquiry')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open', db_index=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='Medium')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='Web Form')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number}: {self.subject} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate unique reference formatted like SF-TICK-XXXXXXXX
            hex_token = uuid.uuid4().hex[:8].upper()
            self.reference_number = f"SF-TICK-{hex_token}"
        if self.status in ('Resolved', 'Closed') and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def status_badge_class(self):
        mapping = {
            'Open': 'badge-warning',
            'In Progress': 'badge-info',
            'Resolved': 'badge-success',
            'Closed': 'badge-muted',
        }
        return mapping.get(self.status, 'badge-info')
