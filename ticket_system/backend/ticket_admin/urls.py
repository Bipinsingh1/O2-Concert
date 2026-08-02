from django.urls import path
from . import views

app_name = 'ticket_admin'

urlpatterns = [
    path('', views.ticket_list_view, name='list'),
    path('<str:ticket_number>/', views.ticket_detail_view, name='detail'),
    path('<str:ticket_number>/cancel/', views.cancel_ticket_view, name='cancel'),
    path('<str:ticket_number>/upgrade/', views.upgrade_ticket_view, name='upgrade'),
]
