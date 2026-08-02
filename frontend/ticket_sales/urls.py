from django.urls import path
from . import views

app_name = 'ticket_sales'

urlpatterns = [
    path('', views.ticket_list_view, name='list'),
    path('select/<int:category_id>/', views.ticket_select_view, name='select'),
    path('group/<int:category_id>/', views.group_ticket_view, name='group'),
    path('waitlist/<int:category_id>/', views.join_waitlist_view, name='waitlist'),
]
