from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('review/', views.review_view, name='review'),
    path('payment/', views.payment_view, name='payment'),
    path('confirm/', views.confirm_view, name='confirm'),
    path('success/<str:order_number>/', views.success_view, name='success'),
]
