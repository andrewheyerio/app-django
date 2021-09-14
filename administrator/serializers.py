from rest_framework import serializers
from core.models import Product, Link, OrderItem, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'image', 'price']

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['code', 'user', 'products', 'created_at',
                  'updated_at']

    # def create(self, validated_data):
    #     instance = self.Meta.model(**validated_data)
    #     instance.save()
    #     return instance

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['__all__']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField('get_total')

    def get_total(self, obj):
        """
        This will retrieve all the OrderItem's that are associated with this order.
        :param obj: ID of the Order
        :return: Return the total cost of this Order Id's Order's
        """
        items = OrderItem.objects.filter(order_id=obj.id)
        return sum((o.price * o.quantity) for o in items)

    class Meta:
        model = Order
        fields = ['__all__']
