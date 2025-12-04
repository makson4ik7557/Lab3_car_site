from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', views.car_add, name='car_add'),
    path('cars/<int:car_id>/edit/', views.car_edit, name='car_edit'),
    path('cars/<int:car_id>/delete/', views.car_delete, name='car_delete'),
    path('cars/api-list/', views.car_api_list, name='car_api_list'),
    path('cars/api/<int:car_id>/delete/', views.car_api_delete, name='car_api_delete'),
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # Dealer URLs
    path('dealer/', views.dealer_dashboard, name='dealer_dashboard'),
    path('dealer/buy/<int:car_id>/', views.buy_car, name='buy_car'),
    path('dealer/modify/<int:car_id>/', views.modify_car, name='modify_car'),
    path('dealer/sell/<int:car_id>/', views.sell_car, name='sell_car'),
    path('dealer/transactions/', views.transaction_history, name='transaction_history'),
]

# Add test URL for 404 page preview (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += [
        path('test-404/', views.custom_404, name='test_404'),
    ]


