from django.urls import path
from . import views

app_name = 'qr_scanner'

urlpatterns = [
    path('', views.scanner_view, name='scanner'),
    path('lookup/', views.lookup_view, name='lookup'),
    path('checkin/', views.checkin_view, name='checkin'),
]
