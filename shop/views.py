from rest_framework import generics, permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import WaterProduct, Order
from .serializers import UserSerializer, WaterProductSerializer, OrderSerializer


class RegisterUserAPIView(generics.CreateAPIView):
    """
    API view to register a new user.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class LoginUserAPIView(APIView):
    """
    API view to authenticate a user and return a token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid Credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class WaterProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list and retrieve available water products.
    """
    queryset = WaterProduct.objects.all()
    serializer_class = WaterProductSerializer
    permission_classes = [permissions.AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage user orders (create, list, retrieve).
    Only authenticated users can access and manage their orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
