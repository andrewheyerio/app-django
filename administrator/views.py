from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics, mixins

from .serializers import ProductSerializer, LinkSerializer, OrderSerializer
from common.authentication import JWTAuthentication
from common.serializers import UserSerializer
from core.models import User, Product, Link, Order

from django.core.cache import cache


# Only an administrator can view, and edit the products

class AmbassadorAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, __):
        ambassadors = User.objects.filter(is_ambassador=True)
        serializer = UserSerializer(ambassadors, many=True)

        return Response(serializer.data)


# Note to future self - a mixin is a class that contains methods for use in another class, without having to be in the
# parent class. This resolves the "diamond of death" problem when using inheretence.
class ProductGenericAPIView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)

        return self.list(request)

    def post(self, request):
        # Note to future self, the only way you could ever know the name of the caches is by looking at the views from
        # common to send under what name this data is being cached too. Hmmmm I wonder if there is a better way of doing
        # this, for example having a global dictionary defined somewhere that specific the name to be used for caching
        # certain data....
        response = self.create(request)

        # because the frontend is using the decorator method of caching, we delete them a little bit differently.
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)

        cache.delete('products_backend')
        return response

    def put(self, request, pk=None):
        response = self.partial_update(request, pk)

        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)

        cache.delete('products_backend')
        return response

    def delete(self, request, pk=None):
        response = self.destroy(request, pk)

        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)

        cache.delete('products_backend')
        return response

class LinkAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        links = Link.objects.filter(user_id=pk)
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data)

class OrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        orders = Order.objects.filter(complete=True)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)