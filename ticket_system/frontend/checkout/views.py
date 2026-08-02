import logging

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Order
from .services.order_service import build_order_from_session, build_orders_from_session
from .services.payment_service import complete_payment
from .services.receipt_service import send_receipt

logger = logging.getLogger(__name__)


def review_view(request):
    """Show order summary before payment."""
    pending = request.session.get('pending_ticket')
    if not pending:
        return redirect('ticket_sales:list')

    from frontend.ticket_sales.models import TicketCategory
    from frontend.ticket_sales.services.discount_service import calculate_discounted_price

    try:
        category = TicketCategory.objects.get(pk=pending['category_id'])
    except TicketCategory.DoesNotExist:
        return redirect('ticket_sales:list')

    user = request.user if request.user.is_authenticated else None
    pricing = calculate_discounted_price(category.price, user)
    quantity = int(pending.get('quantity', 1))
    members = pending.get('members', [])

    total_original = (pricing['original_price'] * quantity).quantize(Decimal('0.01'))
    total_discount = (pricing['discount_amount'] * quantity).quantize(Decimal('0.01'))
    total_final    = (pricing['final_price']    * quantity).quantize(Decimal('0.01'))

    context = {
        'category': category,
        'pricing': pricing,
        'pending': pending,
        'members': members,
        'quantity': quantity,
        'total_original': total_original,
        'total_discount': total_discount,
        'total_final': total_final,
    }
    return render(request, 'checkout/review.html', context)


def payment_view(request):
    """Show payment form. No DB writes — tickets are created only after payment is confirmed."""
    pending = request.session.get('pending_ticket')
    if not pending:
        return redirect('ticket_sales:list')

    from frontend.ticket_sales.models import TicketCategory
    from frontend.ticket_sales.services.discount_service import calculate_discounted_price
    from core.payment.gateway import simulate_payment_success, create_payment_intent
    from django.conf import settings

    try:
        category = TicketCategory.objects.get(pk=pending['category_id'])
    except TicketCategory.DoesNotExist:
        return redirect('ticket_sales:list')

    user = request.user if request.user.is_authenticated else None
    pricing = calculate_discounted_price(category.price, user)
    quantity = int(pending.get('quantity', 1))
    total_amount = (pricing['final_price'] * quantity).quantize(Decimal('0.01'))
    per_ticket_price = pricing['final_price']

    # Initiate a payment intent for the total — no orders exist yet
    # Simulation is only allowed in DEBUG mode with placeholder keys
    if settings.DEBUG and settings.STRIPE_SECRET_KEY == 'sk_test_placeholder':
        payment_result = simulate_payment_success(f'PENDING-{category.id}-qty{quantity}')
    else:
        payment_result = create_payment_intent(
            int(total_amount * 100),
            metadata={'category_id': str(pending['category_id']), 'quantity': str(quantity)},
        )

    if not payment_result.get('success'):
        messages.error(request, 'Unable to initialise payment. Please try again.')
        return redirect('ticket_sales:list')

    context = {
        'category': category,
        'quantity': quantity,
        'total_amount': total_amount,
        'per_ticket_price': per_ticket_price,
        'payment_result': payment_result,
    }
    return render(request, 'checkout/payment.html', context)


@require_POST
def confirm_view(request):
    """
    Payment submitted — now create tickets, orders, and payment records.
    Nothing is written to the DB until this point.
    """
    pending = request.session.get('pending_ticket')
    if not pending:
        # Guard against double-submit or expired session
        messages.error(request, 'Your session has expired. Please start again.')
        return redirect('ticket_sales:list')

    intent_id = request.POST.get('payment_intent_id', '')
    is_group = pending.get('is_group', False)

    # Create tickets + orders atomically now that payment is confirmed
    if is_group:
        order = build_order_from_session(request)
        if not order:
            messages.error(request, 'Could not complete your order. Please try again.')
            return redirect('ticket_sales:list')
        orders = [order]
    else:
        orders = build_orders_from_session(request)
        if not orders:
            messages.error(request, 'Could not complete your order. Please try again.')
            return redirect('ticket_sales:list')

    # Create Payment records atomically — all succeed or all roll back
    try:
        with transaction.atomic():
            for order in orders:
                complete_payment(order, intent_id)
    except Exception:
        logger.exception('Payment completion failed for intent %s', intent_id)
        messages.error(request, 'Payment processing error. Please contact support with your order details.')
        return redirect('ticket_sales:list')

    # Send receipt emails outside the transaction — emails cannot be rolled back
    for order in orders:
        try:
            send_receipt(order)
        except Exception:
            logger.exception('Receipt email failed for order %s', order.order_number)

    # Clear the pending session data — tickets are now issued
    del request.session['pending_ticket']

    # Store ticket numbers for the success page (survives one refresh)
    # Guard against null ticket field
    ticket_numbers = [o.ticket.ticket_number for o in orders if o.ticket]
    success_data = request.session.get('success_data', {})
    success_data[orders[0].order_number] = ticket_numbers
    request.session['success_data'] = success_data

    qty = len(orders)
    if qty > 1:
        messages.success(request, f'Payment successful! {qty} tickets have been emailed to you.')
    else:
        messages.success(request, 'Payment successful! Your ticket has been emailed to you.')

    return redirect('checkout:success', order_number=orders[0].order_number)


def success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    success_data = request.session.get('success_data', {})
    ticket_numbers = success_data.get(order_number, [order.ticket.ticket_number])
    return render(request, 'checkout/success.html', {
        'order': order,
        'ticket_numbers': ticket_numbers,
        'quantity': len(ticket_numbers),
    })
