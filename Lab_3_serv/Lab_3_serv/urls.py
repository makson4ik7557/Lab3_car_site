from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from repo_practice.views import CarViewSet, CustomerViewSet, EmployeeViewSet, SaleViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet, basename='car')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'sales', SaleViewSet, basename='sale')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('car_templates.urls')),  # Include car_templates URLs
]

# Custom error handlers
handler404 = 'car_templates.views.custom_404'

