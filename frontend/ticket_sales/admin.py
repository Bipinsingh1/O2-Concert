from django.contrib import admin
from .models import TicketCategory, Ticket, TicketHolder


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'price', 'total_available', 'sold_count', 'remaining', 'is_refundable', 'is_amendable')


class TicketHolderInline(admin.TabularInline):
    model = TicketHolder
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'category', 'customer_name', 'status', 'amount_paid', 'purchase_date', 'is_guest_purchase')
    list_filter = ('status', 'category', 'is_guest_purchase')
    search_fields = ('ticket_number', 'owner__email', 'guest_email', 'guest_name')
    inlines = [TicketHolderInline]
