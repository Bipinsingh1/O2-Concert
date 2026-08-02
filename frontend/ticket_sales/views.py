from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import TicketCategory, WaitlistEntry
from .forms import TicketSelectForm, GroupTicketForm
from .forms.group_ticket_form import MemberFormSet
from .services.availability_service import get_available_categories
from .services.discount_service import calculate_discounted_price
from .services.cart_service import add_to_cart
from core.utils.dates import sales_are_open
from core.constants import TICKET_GROUP


def ticket_list_view(request):
    if not sales_are_open():
        messages.warning(request, 'Ticket sales have not started yet.')
    categories = get_available_categories()
    context = {
        'categories': categories,
        'sales_open': sales_are_open(),
    }
    return render(request, 'ticket_sales/ticket_list.html', context)


def ticket_select_view(request, category_id):
    category = get_object_or_404(TicketCategory, pk=category_id)
    if category.category_type == TICKET_GROUP:
        return redirect('ticket_sales:group', category_id=category_id)

    pricing = calculate_discounted_price(category.price, request.user if request.user.is_authenticated else None)

    if request.method == 'POST':
        form = TicketSelectForm(request.POST, require_guest_fields=not request.user.is_authenticated)
        form.fields['category'].initial = category
        if form.is_valid():
            # Store selection in session for checkout
            request.session['pending_ticket'] = {
                'category_id': category.id,
                'quantity': form.cleaned_data.get('quantity', 1),
                'guest_name': form.cleaned_data.get('guest_name', ''),
                'guest_email': form.cleaned_data.get('guest_email', ''),
            }
            return redirect('checkout:review')
    else:
        form = TicketSelectForm(initial={'category': category})

    context = {'form': form, 'category': category, 'pricing': pricing}
    return render(request, 'ticket_sales/select_ticket.html', context)


def group_ticket_view(request, category_id):
    category = get_object_or_404(TicketCategory, pk=category_id)
    pricing = calculate_discounted_price(category.price, request.user if request.user.is_authenticated else None)

    if request.method == 'POST':
        form = GroupTicketForm(request.POST)
        formset = MemberFormSet(request.POST, prefix='members')
        if form.is_valid() and formset.is_valid():
            members = [f.cleaned_data for f in formset.forms if f.cleaned_data]
            request.session['pending_ticket'] = {
                'category_id': category.id,
                'guest_name': form.cleaned_data.get('guest_name', ''),
                'guest_email': form.cleaned_data.get('guest_email', ''),
                'members': members,
                'is_group': True,
            }
            return redirect('checkout:review')
    else:
        form = GroupTicketForm()
        formset = MemberFormSet(prefix='members')

    context = {'form': form, 'formset': formset, 'category': category, 'pricing': pricing}
    return render(request, 'ticket_sales/group_ticket.html', context)


def join_waitlist_view(request, category_id):
    """Allow a customer to register for a sold-out ticket category."""
    category = get_object_or_404(TicketCategory, pk=category_id)

    if category.is_available:
        messages.info(request, 'Tickets are still available — no need to join the waitlist!')
        return redirect('ticket_sales:select', category_id=category_id)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'ticket_sales/waitlist.html', {'category': category})

        entry, created = WaitlistEntry.objects.get_or_create(
            category=category,
            email=email,
            defaults={'user': request.user if request.user.is_authenticated else None},
        )
        if created:
            messages.success(
                request,
                f"You're on the waitlist for {category.name}. "
                "We'll email you if a ticket becomes available.",
            )
        else:
            messages.info(request, f'You are already on the waitlist for {category.name}.')
        return redirect('ticket_sales:list')

    return render(request, 'ticket_sales/waitlist.html', {'category': category})
