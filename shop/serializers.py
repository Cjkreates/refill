from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import WaterProduct, Order


# --- User Serializer ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# --- Water Product Serializer ---
class WaterProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterProduct
        fields = ['id', 'name', 'description', 'price', 'stock']


# --- Order Serializer ---
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product = serializers.PrimaryKeyRelatedField(queryset=WaterProduct.objects.all())
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'product', 'product_name',
            'quantity', 'total_price', 'status', 'created_at'
        ]
        read_only_fields = ['total_price', 'status', 'created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']
        if product.stock < quantity:
            raise serializers.ValidationError("Not enough stock available.")
        return data

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']
        user = self.context['request'].user

        with transaction.atomic():
            product.refresh_from_db()

            if product.stock < quantity:
                raise ValidationError("Not enough stock available.")

            # Update stock
            product.stock -= quantity
            product.save()

            # total_price is auto-calculated in model
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
            )

        return order
