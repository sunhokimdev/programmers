from datetime import datetime

import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

from myapp.models import Member


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None:
            raise AuthenticationFailed("Invalid signature")

        try:
            jwt_token = jwt_token.replace("Bearer", "").replace(" ", "")
            payload = jwt
            user = Member.objects.get(id=payload.get("user_id"))

            if user is None:
                raise AuthenticationFailed("User not found")

            return user, payload
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed("Invalid signature")
        except:
            raise ParseError("Parse error")

    def authenticate_header(self, request):
        return "Bearer"

    @classmethod
    def create_jwt(cls, user):
        payload = {
            "user_id": user["id"],
            "exp": int(
                (
                    datetime.now() + settings.JWT_CONF["ACCESS_TOKEN_LIFETIME"]
                ).timestamp()
            ),
        }
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return jwt_token
