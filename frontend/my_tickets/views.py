import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal
from frontend.ticket_sales.models import Ticket, TicketCategory
from .services.ticket_service import get_user_tickets
from .services.cancel_service import cancel_ticket
from .services.amend_service import get_valid_upgrade_categories
from .services.upgrade_service import upgrade_ticket

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
def my_tickets_view(request):
    tickets = get_user_tickets(request.user)
    active_tickets = [t for t in tickets if t.status != 'cancelled']
    cancelled_tickets = [t for t in tickets if t.status == 'cancelled']
    return render(request, 'my_tickets/my_tickets.html', {
        'tickets': tickets,
        'active_tickets': active_tickets,
        'cancelled_tickets': cancelled_tickets,
    })


@login_required
def ticket_detail_view(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, owner=request.user)
    return render(request, 'my_tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def cancel_ticket_view(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, owner=request.user)

    from core.permissions import can_cancel_ticket, get_refund_eligibility
    from core.utils.helpers import calculate_refund_amount

    can_cancel, block_reason = can_cancel_ticket(ticket, request.user)
    will_refund, no_refund_reason = get_refund_eligibility(ticket, request.user)

    refund_amount = None
    fee_amount = None
    if can_cancel and will_refund:
        refund_amount = calculate_refund_amount(ticket.amount_paid)
        fee_amount = ticket.amount_paid - refund_amount

    if request.method == 'POST':
        if not can_cancel:
            messages.error(request, block_reason)
            return redirect('my_tickets:detail', ticket_number=ticket_number)
        result = cancel_ticket(ticket, request.user)
        if result['success']:
            if result.get('refund_amount'):
                messages.success(request, f'Ticket cancelled. A refund of £{result["refund_amount"]:.2f} will be returned to your original payment method.')
            else:
                messages.info(request, 'Your ticket has been cancelled. No refund applies to this ticket type.')
            return redirect('my_tickets:list')
        else:
            messages.error(request, result['error'])

    context = {
        'ticket': ticket,
        'can_cancel': can_cancel,
        'block_reason': block_reason,
        'will_refund': will_refund,
        'no_refund_reason': no_refund_reason,
        'refund_amount': refund_amount,
        'fee_amount': fee_amount,
    }
    return render(request, 'my_tickets/cancel_ticket.html', context)


@login_required
def upgrade_ticket_view(request, ticket_number):
    """Step 1 – choose the new category."""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, owner=request.user)

    from core.permissions import can_amend_ticket
    can, reason = can_amend_ticket(ticket)
    if not can:
        messages.error(request, reason)
        return redirect('my_tickets:detail', ticket_number=ticket_number)

    upgrade_options = get_valid_upgrade_categories(ticket)

    # Annotate each option with the price diff the user will pay
    options_with_diff = []
    for opt in upgrade_options:
        diff = max(Decimal('0'), opt.price - ticket.amount_paid)
        options_with_diff.append({'category': opt, 'price_diff': diff})

    if request.method == 'POST':
        new_cat_id = request.POST.get('new_category')
        if not new_cat_id:
            messages.error(request, 'Please select an upgrade option.')
            return redirect('my_tickets:upgrade', ticket_number=ticket_number)

        try:
            new_category = TicketCategory.objects.get(pk=new_cat_id)
        except TicketCategory.DoesNotExist:
            messages.error(request, 'Invalid category selected.')
            return redirect('my_tickets:upgrade', ticket_number=ticket_number)

        from core.constants import TICKET_UPGRADE_PATHS
        valid_upgrades = TICKET_UPGRADE_PATHS.get(ticket.category.category_type, [])
        if new_category.category_type not in valid_upgrades:
            messages.error(request, 'Invalid upgrade selection.')
            return redirect('my_tickets:upgrade', ticket_number=ticket_number)

        price_diff = max(Decimal('0'), new_category.price - ticket.amount_paid)

        # Store upgrade intent in session and go to payment
        request.session['pending_upgrade'] = {
            'ticket_number': ticket_number,
            'new_category_id': new_category.id,
            'new_category_name': new_category.name,
            'price_diff': str(price_diff),
            'old_category_name': ticket.category.name,
        }
        return redirect('my_tickets:upgrade_payment', ticket_number=ticket_number)

    return render(request, 'my_tickets/upgrade_ticket.html', {
        'ticket': ticket,
        'options_with_diff': options_with_diff,
    })


@login_required
def upgrade_payment_view(request, ticket_number):
    """Step 2 – pay the price difference."""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, owner=request.user)
    pending = request.session.get('pending_upgrade')

    if not pending or pending.get('ticket_number') != ticket_number:
        messages.error(request, 'Upgrade session expired. Please start again.')
        return redirect('my_tickets:upgrade', ticket_number=ticket_number)

    from core.payment.gateway import simulate_payment_success
    from django.conf import settings

    price_diff = Decimal(pending['price_diff'])
    new_category_name = pending['new_category_name']
    old_category_name = pending['old_category_name']

    if request.method == 'POST':
        # Simulate payment processing
        if settings.STRIPE_SECRET_KEY == 'sk_test_placeholder':
            payment_result = simulate_payment_success(f'UPG-{ticket_number}')
        else:
            from core.payment.gateway import create_payment_intent
            payment_result = create_payment_intent(
                int(price_diff * 100),
                metadata={'ticket_number': ticket_number, 'upgrade': True}
            )

        if not payment_result.get('success'):
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('my_tickets:upgrade_payment', ticket_number=ticket_number)

        # Payment succeeded — apply the upgrade
        try:
            new_category = TicketCategory.objects.get(pk=pending['new_category_id'])
        except TicketCategory.DoesNotExist:
            messages.error(request, 'Upgrade category no longer available.')
            return redirect('my_tickets:list')

        result = upgrade_ticket(ticket, new_category, request.user)
        if result['success']:
            del request.session['pending_upgrade']
            messages.success(
                request,
                f'Upgrade successful! Your ticket has been upgraded from '
                f'{result["old_category"]} to {result["new_category"]}. '
                f'£{result["price_diff"]:.2f} has been charged.'
            )
            return redirect('my_tickets:detail', ticket_number=ticket_number)
        else:
            messages.error(request, result['error'])
            return redirect('my_tickets:upgrade', ticket_number=ticket_number)

    # GET – show payment form
    if settings.STRIPE_SECRET_KEY == 'sk_test_placeholder':
        payment_result = simulate_payment_success(f'UPG-{ticket_number}')
    else:
        from core.payment.gateway import create_payment_intent
        payment_result = create_payment_intent(
            int(price_diff * 100),
            metadata={'ticket_number': ticket_number}
        )

    return render(request, 'my_tickets/upgrade_payment.html', {
        'ticket': ticket,
        'price_diff': price_diff,
        'new_category_name': new_category_name,
        'old_category_name': old_category_name,
        'payment_result': payment_result,
    })


@login_required
def transfer_ticket_view(request, ticket_number):
    """Transfer a ticket to another registered user by their email address."""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, owner=request.user)

    from core.constants import TICKET_ACTIVE
    if ticket.status != TICKET_ACTIVE:
        messages.error(request, 'Only active tickets can be transferred.')
        return redirect('my_tickets:detail', ticket_number=ticket_number)

    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email', '').strip().lower()

        if not recipient_email:
            messages.error(request, 'Please enter the recipient\'s email address.')
            return render(request, 'my_tickets/transfer_ticket.html', {'ticket': ticket})

        if recipient_email == request.user.email.lower():
            messages.error(request, 'You cannot transfer a ticket to yourself.')
            return render(request, 'my_tickets/transfer_ticket.html', {'ticket': ticket})

        try:
            recipient = User.objects.get(email__iexact=recipient_email, is_active=True, is_staff=False)
        except User.DoesNotExist:
            messages.error(
                request,
                'No registered customer account found with that email address. '
                'The recipient must have an account on this site.'
            )
            return render(request, 'my_tickets/transfer_ticket.html', {'ticket': ticket})

        old_owner_email = request.user.email
        ticket.owner = recipient
        ticket.save(update_fields=['owner'])
        logger.info(
            'Ticket %s transferred from %s to %s',
            ticket_number, old_owner_email, recipient.email,
        )
        messages.success(
            request,
            f'Ticket {ticket_number} has been transferred to {recipient.email}.'
        )
        return redirect('my_tickets:list')

    return render(request, 'my_tickets/transfer_ticket.html', {'ticket': ticket})
