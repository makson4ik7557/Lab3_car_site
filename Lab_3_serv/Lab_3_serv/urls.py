from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from repo_practice.views import (
    CarViewSet, CustomerViewSet, EmployeeViewSet, SaleViewSet,
    DealerProfileViewSet, TransactionViewSet, DealerViewSet, AnalyticsViewSet,
    benchmark_dashboard, run_benchmark, get_benchmark_results, clear_benchmark_results, create_demo_data
)
from analytics import dashboard_views
from analytics import bokeh_dashboard_views

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
    path('dashboard/plotly/', dashboard_views.plotly_dashboard, name='plotly_dashboard'),  # Plotly Dashboard v1
    path('dashboard/bokeh/', bokeh_dashboard_views.bokeh_dashboard, name='bokeh_dashboard'),  # Bokeh Dashboard v2
    path('repo/benchmark/', benchmark_dashboard, name='benchmark_dashboard'),
    path('repo/benchmark/run/', run_benchmark, name='run_benchmark'),
    path('repo/benchmark/results/', get_benchmark_results, name='get_benchmark_results'),
    path('repo/benchmark/clear/', clear_benchmark_results, name='clear_benchmark_results'),
    path('repo/benchmark/demo/', create_demo_data, name='create_demo_data'),
    path('', include('car_templates.urls')),  # Include car_templates URLs
]

# Custom error handlers
handler404 = 'car_templates.views.custom_404'

