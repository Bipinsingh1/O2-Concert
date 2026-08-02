from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.decorators import admin_required
from frontend.ticket_sales.models import Ticket, TicketCategory
from .services.search_service import search_tickets
from .services.cancel_service import admin_cancel_ticket
from .services.upgrade_service import admin_upgrade_ticket
from frontend.my_tickets.services.amend_service import get_valid_upgrade_categories


@admin_required
def ticket_list_view(request):
    query = request.GET.get('q', '').strip()
    tickets = search_tickets(query) if query else Ticket.objects.select_related(
        'category', 'owner'
    ).order_by('-purchase_date')[:100]
    return render(request, 'ticket_admin/ticket_list.html', {'tickets': tickets, 'query': query})


@admin_required
def ticket_detail_view(request, ticket_number):
    ticket = get_object_or_404(
        Ticket.objects.select_related('category', 'owner').prefetch_related('holders'),
        ticket_number=ticket_number,
    )
    return render(request, 'ticket_admin/ticket_detail.html', {'ticket': ticket})


@admin_required
def cancel_ticket_view(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    if request.method == 'POST':
        result = admin_cancel_ticket(ticket, request.user)
        if result['success']:
            messages.success(request, 'Ticket cancelled successfully.')
        else:
            messages.error(request, result['error'])
        return redirect('ticket_admin:detail', ticket_number=ticket_number)
    return render(request, 'ticket_admin/cancel_confirm.html', {'ticket': ticket})


@admin_required
def upgrade_ticket_view(request, ticket_number):
    from core.permissions import can_amend_ticket
    from decimal import Decimal

    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    can, reason = can_amend_ticket(ticket)
    if not can:
        messages.error(request, reason)
        return redirect('ticket_admin:detail', ticket_number=ticket_number)

    upgrade_options = get_valid_upgrade_categories(ticket)

    # Annotate each option with the price difference
    options_with_diff = [
        {'category': opt, 'price_diff': max(Decimal('0'), opt.price - ticket.amount_paid)}
        for opt in upgrade_options
    ]

    if request.method == 'POST':
        new_cat_id = request.POST.get('new_category', '').strip()
        if not new_cat_id:
            messages.error(request, 'Please select an upgrade category.')
            return redirect('ticket_admin:upgrade', ticket_number=ticket_number)
        try:
            new_category = TicketCategory.objects.get(pk=new_cat_id)
        except (TicketCategory.DoesNotExist, ValueError):
            messages.error(request, 'Invalid category.')
            return redirect('ticket_admin:upgrade', ticket_number=ticket_number)
        result = admin_upgrade_ticket(ticket, new_category, request.user)
        if result['success']:
            messages.success(request, f'Ticket upgraded from {result["old_category"]} to {result["new_category"]}.')
        else:
            messages.error(request, result['error'])
        return redirect('ticket_admin:detail', ticket_number=ticket_number)

    return render(request, 'ticket_admin/upgrade_ticket.html', {
        'ticket': ticket,
        'options_with_diff': options_with_diff,
    })
