from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterUserAPIView, LoginUserAPIView, WaterProductViewSet, OrderViewSet
from .views import clear_orders

# Initialize DRF router and register viewsets
router = DefaultRouter()
router.register(r'products', WaterProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

# Define URL patterns
urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('orders/clear/', clear_orders, name='clear-orders'),

    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('', include(router.urls)),
]




