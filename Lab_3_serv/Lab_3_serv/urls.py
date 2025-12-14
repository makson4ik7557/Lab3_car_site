from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from repo_practice.views import (
    CarViewSet, CustomerViewSet, EmployeeViewSet, SaleViewSet,
    DealerProfileViewSet, TransactionViewSet, DealerViewSet, AnalyticsViewSet
)
from repo_practice import dashboard_views

# REST API Router
# АРХІТЕКТУРА: Database → Repository → API → UI
router = DefaultRouter()
router.register(r'cars', CarViewSet, basename='car')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'dealer-profiles', DealerProfileViewSet, basename='dealer-profile')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'dealer', DealerViewSet, basename='dealer')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')  # Analytics API endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # REST API layer (отримує дані з Repository)
    path('dashboard/plotly/', dashboard_views.plotly_dashboard, name='plotly-dashboard'),  # UI layer (отримує дані з API)
    path('', include('car_templates.urls')),  # Include car_templates URLs
]

# Custom error handlers
handler404 = 'car_templates.views.custom_404'

