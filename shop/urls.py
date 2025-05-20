from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterUserAPIView, LoginUserAPIView, WaterProductViewSet, OrderViewSet

router = DefaultRouter()
router.register('products', WaterProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('', include(router.urls)),
]
