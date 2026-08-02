import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.decorators import admin_required
from core.constants import TICKET_ACTIVE, TICKET_CHECKED_IN
from frontend.ticket_sales.models import Ticket

logger = logging.getLogger(__name__)


@admin_required
def scanner_view(request):
    return render(request, 'qr_scanner/scanner.html')


@admin_required
def lookup_view(request):
    ticket_number = request.GET.get('ticket_number', '').strip().upper()
    if not ticket_number:
        return JsonResponse({'found': False, 'error': 'No ticket number provided.'})
    try:
        ticket = Ticket.objects.select_related('category', 'owner').prefetch_related('holders').get(
            ticket_number=ticket_number
        )
        holders = [{'name': h.name, 'age_group': h.age_group} for h in ticket.holders.all()]
        return JsonResponse({
            'found': True,
            'ticket_number': ticket.ticket_number,
            'category': ticket.category.name,
            'status': ticket.status,
            'customer_name': ticket.customer_name,
            'purchase_date': ticket.purchase_date.strftime('%d %b %Y'),
            'holders': holders,
        })
    except Ticket.DoesNotExist:
        return JsonResponse({'found': False, 'error': 'Ticket not found.'})


@admin_required
@require_POST
def checkin_view(request):
    """Mark a ticket as checked-in at the door. Prevents duplicate entry."""
    ticket_number = request.POST.get('ticket_number', '').strip().upper()
    if not ticket_number:
        return JsonResponse({'success': False, 'error': 'No ticket number provided.'})
    try:
        ticket = Ticket.objects.select_related('category').get(ticket_number=ticket_number)

        if ticket.status == TICKET_CHECKED_IN:
            logger.warning('Duplicate check-in attempt for ticket %s', ticket_number)
            return JsonResponse({
                'success': False,
                'error': 'This ticket has already been checked in.',
                'already_checked_in': True,
            })

        if ticket.status != TICKET_ACTIVE:
            logger.warning(
                'Check-in refused for ticket %s — status is %s', ticket_number, ticket.status
            )
            return JsonResponse({
                'success': False,
                'error': f'Ticket cannot be checked in (status: {ticket.status}).',
            })

        ticket.status = TICKET_CHECKED_IN
        ticket.save(update_fields=['status'])
        logger.info('Ticket %s checked in by staff user %s', ticket_number, request.user)
        return JsonResponse({
            'success': True,
            'message': f'Ticket {ticket_number} checked in successfully.',
            'category': ticket.category.name,
        })

    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ticket not found.'})
