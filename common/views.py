from django.shortcuts import render
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from .serializers import UserSerializer
from core.models import User


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Password do not match!')

        # If the request has the ambassador api then register the user an ambassador
        data['is_ambassador'] = 'api/ambassador' in request.path

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        # Because the user object inherits from abstract UserModel
        # we are provided with lots of useful methods such as
        # filtering, and checking the password
        user = User.objects.filter(email=email).first()

        # first we try to find the user based on their email
        if user is None:
            raise exceptions.AuthenticationFailed("User not found")

        # If successful use the parent method to check the password
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Incorrect Password!")

        # Here we can define two different "scopes" which allow us to identify if the
        # request is either an ambassador or and admin or whatever ambiguous identifier.
        scope = 'ambassador' if 'api/ambassador' in request.path else 'admin'

        # If the password is also correct, generate an authentication token
        token = JWTAuthentication.generate_jwt(user.id, scope)

        # setting the jwt key/value as a cookie prevents this value from reaching
        # the frontend to further secure the authentication
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, __):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException("Passwords do not match!")

        user.set_password(data['password'])
        user.save()

        return Response(UserSerializer(user).data)
