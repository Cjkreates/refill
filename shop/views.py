from rest_framework import generics, permissions, viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes

from .models import WaterProduct, Order
from .serializers import UserSerializer, WaterProductSerializer, OrderSerializer


# --- User Registration View ---
class RegisterUserAPIView(generics.CreateAPIView):
    """
    API view to register a new user.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# --- User Login View ---
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
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


# --- Water Product ViewSet ---
class WaterProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list and retrieve available water products.
    """
    queryset = WaterProduct.objects.all()
    serializer_class = WaterProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['price', 'name']
    search_fields = ['name', 'description']


# --- Custom permission to allow only owners to edit/delete ---
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only owners of an object to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for all
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the owner
        return obj.user == request.user


# --- Order ViewSet ---
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage user orders (create, list, retrieve).
    Only authenticated users can access and manage their own orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Only show the authenticated user's orders
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically assign the user to the order
        serializer.save(user=self.request.user)

    # Disable update/partial_update/delete methods
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Order update is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Order partial update is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Order deletion is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


# --- Clear Orders API View ---
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_orders(request):
    """
    API endpoint to delete all orders for the authenticated user.
    """
    deleted, _ = Order.objects.filter(user=request.user).delete()
    return Response(
        {"detail": f"{deleted} order(s) cleared."},
        status=status.HTTP_204_NO_CONTENT
    )
