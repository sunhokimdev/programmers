from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import (
    permission_classes,
    authentication_classes,
    api_view,
)
from rest_framework.permissions import AllowAny

from myapp.authentication import create_jwt
from myapp.errors import ErrorCodes
from myapp.serializer import SaveMemberSerializer
from myapp.utils import (
    success_response,
    error_response,
    swagger_default_schema_response,
)


@swagger_auto_schema(
    methods=["post"],
    tags=["common"],
    operation_summary="유저 생성 API",
    security=[],
    request_body=SaveMemberSerializer,
    responses=swagger_default_schema_response(
        additional_properties={
            "access_token": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="API 사용 Access Token(어드민과 일반인 토큰 구분 필요)",
            )
        }
    ),
    operation_description="유저 정보 저장",
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@transaction.atomic
def save_member(request):
    serializer = SaveMemberSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        token = create_jwt(serializer.data)
        data = {"access_token": token}

        return success_response(data=data)
    return error_response(ErrorCodes.UNKNOWN)
