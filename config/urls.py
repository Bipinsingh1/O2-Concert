from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Customer-facing
    path('', include('frontend.home.urls')),
    path('accounts/', include('frontend.accounts.urls')),
    path('tickets/', include('frontend.ticket_sales.urls')),
    path('checkout/', include('frontend.checkout.urls')),
    path('my-tickets/', include('frontend.my_tickets.urls')),

    # Admin-facing
    path('admin/dashboard/', include('backend.dashboard.urls')),
    path('admin/tickets/', include('backend.ticket_admin.urls')),
    path('admin/reports/', include('backend.reports.urls')),
    path('admin/qr-scanner/', include('backend.qr_scanner.urls')),
]

handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
