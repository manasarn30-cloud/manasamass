from django.contrib import admin
from support.models import FAQ, SupportTicket


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'display_order', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer', 'keywords')
    list_editable = ('is_active', 'display_order')
    ordering = ('display_order', 'id')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'subject', 'user', 'guest_email', 'category', 'status', 'priority', 'source', 'created_at')
    list_filter = ('status', 'priority', 'category', 'source', 'created_at')
    search_fields = ('reference_number', 'subject', 'description', 'user__username', 'guest_email')
    readonly_fields = ('reference_number', 'source', 'created_at', 'updated_at')
    ordering = ('-created_at',)
