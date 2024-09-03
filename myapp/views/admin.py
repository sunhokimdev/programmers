from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.views import APIView

from myapp.authentication import JWTAuthentication
from myapp.errors import ErrorCodes
from myapp.models import Schedule
from myapp.permission import IsAdmin
from myapp.serializer import (
    FindAdminSchedulesSerializer,
    SaveCourseSerializer,
    ModifyAdminScheduleSerializer,
)
from myapp.utils import (
    success_response,
    error_response,
    swagger_default_schema_response,
    get_error_codes_overlapping_and_reservation_counts,
)


class AdminScheduleAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdmin,)

    @swagger_auto_schema(
        tags=["admin"],
        operation_summary="어드민이 등록한 시험의 회원 일정 조회 API",
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="가져올 회원 스케줄 갯수",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="가져올 회원 스케줄 시작 위치",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses=swagger_default_schema_response(
            additional_properties={
                "schedule_id": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="응시할 테스트 스케줄 고유 번호",
                ),
                "test_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="시험 이름",
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="회원 스케줄 상태(W: 대기, C: 확정)",
                ),
                "user_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="응시할 회원 이름",
                ),
                "text_language": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="회원이 선택한 언어",
                ),
                "test_start_datetime": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="테스트 스케줄 생성 일자(iso 8401 형태의 일자)",
                ),
            }
        ),
    )
    def get(self, request):
        schedules = Schedule.objects.select_related("exam").filter(
            exam__member_id=request.user.id
        )
        limit = int(request.GET.get("limit", 10))
        offset = int(request.GET.get("offset", 0))

        paginated_schedules = schedules[offset : offset + limit]
        serializer = FindAdminSchedulesSerializer(paginated_schedules, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        tags=["admin"],
        operation_summary="유저 시험 삭제 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "type": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="partial: 부분 삭제, all: 모두 삭제",
                ),
                "schedules": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="삭제할 스케줄 리스트, 단 type이 partial 이어야 이 리스트에 해당되는 스케줄 삭제입니다.",
                ),
            },
        ),
        responses=swagger_default_schema_response(),
        operation_description="어드민 토큰만 가능합니다.",
    )
    @transaction.atomic
    def delete(self, request):
        if request.data["type"] == "partial":
            schedules = request.data.get("schedules", [])
            registered_schedules = Schedule.objects.select_related("exam").filter(
                exam_id__member=request.user.id, pk__in=schedules
            )
            if not registered_schedules:
                return error_response(ErrorCodes.NO_DATA)
            registered_schedules.all().delete()
        elif request.data["type"] == "all":
            registered_schedules = Schedule.objects.select_related("exam").filter(
                exam_id__member=request.user.id
            )
            if not registered_schedules:
                return error_response(ErrorCodes.NO_DATA)
            registered_schedules.all().delete()
        else:
            return error_response(ErrorCodes.INVALID_REQUEST_DATA)
        return success_response()

    @swagger_auto_schema(
        tags=["admin"],
        operation_summary="유저 시험 수정 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="C: 확정, W: 대기",
                ),
                "language": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="시험 볼 언어",
                ),
                "schedule": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="유저 스케줄 고유번호",
                ),
            },
        ),
        responses=swagger_default_schema_response(),
        operation_description="어드민 토큰만 가능합니다.",
    )
    @transaction.atomic
    def patch(self, request):
        schedule = request.data.get("schedule")
        registered_schedule = Schedule.objects.select_related("exam").get(
            exam_id__member=request.user.id, pk=schedule
        )
        if not registered_schedule:
            return error_response(ErrorCodes.NO_DATA)

        if not request.data["language"] in registered_schedule.exam.language:
            return error_response(ErrorCodes.INVALID_REQUEST_DATA)

        if request.data["status"] == "C" and registered_schedule.status == "W":
            exam = registered_schedule.exam
            error_codes = get_error_codes_overlapping_and_reservation_counts(exam)

            if error_codes is not None:
                return error_response(error_codes)

        serializer = ModifyAdminScheduleSerializer(
            registered_schedule, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return success_response()
        return error_response(ErrorCodes.UNKNOWN)


@swagger_auto_schema(
    methods=["patch"],
    tags=["admin"],
    operation_summary="유저 시험 모두 예약 확정 API",
    manual_parameters=[
        openapi.Parameter(
            "exam_id",
            openapi.IN_PATH,
            description="시험 고유 번호",
            type=openapi.TYPE_INTEGER,
        )
    ],
    responses=swagger_default_schema_response(),
    operation_description="어드민 토큰만 가능합니다.",
)
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
@transaction.atomic
def confirm_all_reservations(request, exam_id=None):
    schedules = Schedule.objects.select_related("exam").filter(
        exam_id__member=request.user.id, status="W", exam_id=exam_id
    )

    if not schedules.exists():
        return error_response(ErrorCodes.NO_DATA)

    exam = schedules.first().exam
    if exam:
        error_codes = get_error_codes_overlapping_and_reservation_counts(exam)
        if error_codes is not None:
            return error_response(error_codes)

    schedules.all().update(status="C")
    return success_response()


@swagger_auto_schema(
    methods=["post"],
    operation_summary="시험 생성 API",
    request_body=SaveCourseSerializer,
    responses=swagger_default_schema_response(),
    operation_description="시험 정보 등록(어드민만 가능합니다.)",
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
@transaction.atomic
def save_course(request):
    serializer = SaveCourseSerializer(
        data=request.data, context=request.user, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return success_response()
    print(serializer.errors)
    return error_response(ErrorCodes.UNKNOWN)
