from django.shortcuts import render
from core.decorators import admin_required
from .services.dashboard_service import get_dashboard_stats


@admin_required
def dashboard_view(request):
    stats = get_dashboard_stats()
    return render(request, 'dashboard/index.html', {'stats': stats})
