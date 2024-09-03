from datetime import timedelta

from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny

from myapp.models import Course
from myapp.serializer import FindCourseListSerializer
from myapp.utils import (
    success_response,
    swagger_default_schema_response,
)


@swagger_auto_schema(
    methods=["get"],
    operation_summary="테스트 조회 API",
    tags=["common"],
    security=[],
    manual_parameters=[
        openapi.Parameter(
            "limit",
            openapi.IN_QUERY,
            description="가져올 테스트의 갯수",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "offset",
            openapi.IN_QUERY,
            description="가져올 테스트의 데이터의 시작 위치",
            type=openapi.TYPE_INTEGER,
        ),
    ],
    responses=swagger_default_schema_response(
        additional_properties={
            "course_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="응시할 테스트 고유 번호",
            ),
            "name": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="응시할 테스트 이름",
            ),
            "language": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="응시할 있는 테스트들(,로 구분)",
            ),
            "test_start_datetime": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="테스트 시작일(iso 8401 형태의 일자)",
            ),
            "test_end_datetime": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="테스트 종료일(iso 8401 형태의 일자)",
            ),
            "current_number": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="테스트의 현재 예약 확정 인원",
            ),
            "max_number": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="테스트의 최대 예약 확정 인원",
            ),
        }
    ),
    operation_description="테스트 정보 조회",
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def find_course_list(request):
    now = timezone.now()
    three_days_after_now = now + timedelta(days=3)

    course_list = Course.objects.filter(test_start_datetime__gte=three_days_after_now)

    limit = int(request.GET.get("limit", 10))
    offset = int(request.GET.get("offset", 0))

    paginated_course_list = course_list[offset : offset + limit]

    serializer = FindCourseListSerializer(paginated_course_list, many=True)
    return success_response(data=serializer.data)
