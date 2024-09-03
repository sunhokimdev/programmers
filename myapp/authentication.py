from datetime import datetime

import jwt
from django.conf import settings
from rest_framework import authentication

from myapp.errors import ErrorCodes
from myapp.models import Member
from myapp.utils import error_response


def create_jwt(user):
    payload = {
        "user_id": user["id"],
        "exp": int(
            (datetime.now() + settings.JWT_CONF["ACCESS_TOKEN_LIFETIME"]).timestamp()
        ),
    }
    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return jwt_token


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.path.startswith("/swagger"):
            return None

        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None:
            print(f"token is null")
            return error_response(ErrorCodes.AUTHENTICATE)

        try:
            jwt_token = jwt_token.replace("Bearer", "").replace(" ", "")
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
            user = Member.objects.get(id=payload.get("user_id"))

            if user is None:
                print(f"User not found")
                return error_response(ErrorCodes.AUTHENTICATE)

            return user, payload
        except jwt.exceptions.InvalidSignatureError as e:
            print(f"Invalid signature: {str(e)}")
        except Exception as e:
            print(f"Unknown Exception: {str(e)}")
        return error_response(ErrorCodes.AUTHENTICATE)

    def authenticate_header(self, request):
        return "Bearer"
