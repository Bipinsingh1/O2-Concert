from django.shortcuts import render
from core.utils.dates import sales_are_open
from frontend.ticket_sales.services.availability_service import get_available_categories


def index_view(request):
    # annotate_remaining() computes sold/remaining in 1 query — no N+1
    categories = get_available_categories()
    context = {
        'categories': categories,
        'sales_open': sales_are_open(),
    }
    return render(request, 'home/index.html', context)


def about_view(request):
    return render(request, 'home/about.html')


def contact_view(request):
    return render(request, 'home/contact.html')


def faq_view(request):
    return render(request, 'home/faq.html')
