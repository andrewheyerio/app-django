import jwt, datetime
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from app import settings
from core.models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        is_ambassador = 'api/ambassador' in request.path

        # First, check to see if there is an encoded jwt cookie on the clients browser.
        token = request.COOKIES.get('jwt')
        if not token:
            return None

        # If a cookie exists, decode it using the same secret key and algo used to
        # encrypt it
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('unauthenticated')

        if (is_ambassador and payload['scope'] != 'ambassador') or (not is_ambassador and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid Scope')



        # If we successfully decode the jwt token, then there should be a user ID on
        # that token.
        user = User.objects.get(pk=payload['user_id'])

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        return (user, None)

    @staticmethod
    def generate_jwt(id, scope):
        payload = {
            'user_id': id,
            'scope': scope,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
