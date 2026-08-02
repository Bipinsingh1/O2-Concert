from django.urls import path
from . import views

app_name = 'my_tickets'

urlpatterns = [
    path('', views.my_tickets_view, name='list'),
    path('<str:ticket_number>/', views.ticket_detail_view, name='detail'),
    path('<str:ticket_number>/cancel/', views.cancel_ticket_view, name='cancel'),
    path('<str:ticket_number>/upgrade/', views.upgrade_ticket_view, name='upgrade'),
    path('<str:ticket_number>/upgrade/payment/', views.upgrade_payment_view, name='upgrade_payment'),
    path('<str:ticket_number>/transfer/', views.transfer_ticket_view, name='transfer'),
]
