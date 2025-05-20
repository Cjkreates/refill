from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import WaterProduct, Order


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


class WaterProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterProduct
        fields = ['id', 'name', 'description', 'price', 'stock']


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
        total_price = product.price * quantity

        with transaction.atomic():
            product.refresh_from_db()
            if product.stock < quantity:
                raise serializers.ValidationError("Not enough stock available.")

            product.stock -= quantity
            product.save()

            order = Order.objects.create(
                user=self.context['request'].user,
                product=product,
                quantity=quantity,
                total_price=total_price,
                status='PENDING',
            )

        return order
