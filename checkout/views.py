from django.db import transaction
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import LinkSerializer
from core.models import Link, Order, Product, OrderItem

import decimal


class LinkAPIView(APIView):
    def get(self, _, code =''):
        link = Link.objects.filter(code=code).first()
        serializer = LinkSerializer(link)
        return Response(serializer.data)

# What happens if we fail at the for loop? We have already saved an order but let's say that the data from
# the products is incorrect and we can't save those. We solve this using transactions
class OrderAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        data = request.data
        link = Link.objects.filter(code=data['code']).first()

        if not link:
            raise exceptions.APIException('Invalid code!')

        try:
            order = Order()
            order.code = link.code
            order.user_id = link.user_id
            order.ambassador_email = link.user.email

            order.first_name = data['first_name']
            order.last_name = data['last_name']
            order.email = data['email']
            order.address = data['address']
            order.country = data['country']
            order.city = data['city']
            order.zip = data['zip']

            order.save()

            for item in data['products']:
                product = Product.objects.filter(pk=item['product_id']).first()
                quantity = decimal.Decimal(item['quantity'])

                order_item = OrderItem()
                order_item.order = order
                order_item.product_title = product.title
                order.price = product.price
                order_item.quantity = quantity
                order_item.ambassador_revenue = decimal.Decimal(.1) * product.price * quantity
                order_item.admin_revenue = decimal.Decimal(.9) * product.price * quantity

                order_item.save()
                return Response({
                    'message': 'success'
                })

        except Exception:
            transaction.rollback()

        return Response({
            'message': "Error occured"
        })