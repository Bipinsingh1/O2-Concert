from django.shortcuts import render
from django.http import StreamingHttpResponse
from core.decorators import admin_required
from .services.sales_report import get_sales_volume_report
from .services.revenue_report import get_revenue_report
from .services.demographic_report import get_demographic_report
from .services.export_service import generate_ticket_rows


@admin_required
def reports_view(request):
    context = {
        'sales': get_sales_volume_report(),
        'revenue': get_revenue_report(),
        'demographics': get_demographic_report(),
    }
    return render(request, 'reports/reports.html', context)


@admin_required
def export_csv_view(request):
    response = StreamingHttpResponse(
        generate_ticket_rows(),
        content_type='text/csv',
    )
    response['Content-Disposition'] = 'attachment; filename="tickets_report.csv"'
    return response
