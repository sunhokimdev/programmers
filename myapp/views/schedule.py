from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from myapp.authentication import JWTAuthentication
from myapp.errors import ErrorCodes
from myapp.models import Schedule, Exam
from myapp.permission import IsNormal
from myapp.serializer import (
    FindMemberScheduleSerializer,
    SaveScheduleSerializer,
    ModifyMemberScheduleSerializer,
)
from myapp.utils import (
    success_response,
    error_response,
    swagger_default_schema_response,
    get_error_codes_overlapping_and_reservation_counts,
)


class MemberScheduleAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsNormal,)

    @swagger_auto_schema(
        tags=["member"],
        operation_summary="유저 시험 일정 조회 API",
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="가져올 시험의 갯수",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="가져올 시험의 데이터의 시작 위치",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses=swagger_default_schema_response(
            additional_properties={
                "schedule_id": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="응시할 테스트 스케줄 고유 번호",
                ),
                "created_datetime": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="테스트 스케줄 생성 일자(iso 8401 형태의 일자)",
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="스케줄 상태(W: 대기, C: 확정)",
                ),
                "language": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="응시할 시험의 언어 종류(,로 구분)",
                ),
                "test_language": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="응시할 시험의 선택한 언어",
                ),
                "max_number": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="시험의 최대 예약 확정 인원",
                ),
            }
        ),
    )
    def get(self, request):
        users = request.user
        limit = int(request.GET.get("limit", 10))
        offset = int(request.GET.get("offset", 0))
        schedule = Schedule.objects.select_related("exam").filter(member_id=users.id)
        paginated_schedule_list = schedule[offset : offset + limit]
        serializer = FindMemberScheduleSerializer(paginated_schedule_list, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        tags=["member"],
        operation_summary="유저 시험 일정 예약 API",
        request_body=SaveScheduleSerializer,
        responses=swagger_default_schema_response(),
    )
    @transaction.atomic
    def post(self, request):
        schedule = Schedule.objects.select_related("exam").filter(
            member_id=request.user.id, exam_id=request.data["exam"]
        )

        if schedule is not None and schedule.exists():
            return error_response(ErrorCodes.ALREADY_RESERVATIONS)

        exam = Exam.objects.get(id=request.data["exam"])
        if exam is None or not request.data["language"] in exam.language:
            return error_response(ErrorCodes.INVALID_REQUEST_DATA)

        three_days_after_now = timezone.now() + timedelta(days=3)
        if exam.test_start_datetime < three_days_after_now:
            return error_response(ErrorCodes.INVALID_REQUEST_DATA_TOO_LATE)

        error_codes = get_error_codes_overlapping_and_reservation_counts(exam)

        if error_codes is not None:
            return error_response(error_codes)

        serializer = SaveScheduleSerializer(data=request.data, context=request.user)
        if serializer.is_valid():
            serializer.save()
            return success_response()
        return error_response(ErrorCodes.INVALID_REQUEST_DATA)

    @swagger_auto_schema(
        tags=["member"],
        operation_summary="유저 시험 수정 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "schedule_id": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="바꿀 테스트의 고유번호"
                ),
                "language": openapi.Schema(
                    type=openapi.TYPE_STRING, description="바꿀 시험의 언어"
                ),
            },
        ),
        responses=swagger_default_schema_response(),
        operation_description="유저 토큰만 가능하며, 상태가 대기인 스케줄만 수정됩니다.",
    )
    @transaction.atomic
    def patch(self, request):
        schedule = Schedule.objects.select_related("exam").get(
            member_id=request.user.id, id=request.data["schedule_id"], status="W"
        )

        if not schedule:
            return error_response(ErrorCodes.NO_DATA)
        if request.data["language"] not in schedule.exam.language:
            return error_response(ErrorCodes.INVALID_REQUEST_DATA)

        serializer = ModifyMemberScheduleSerializer(
            schedule, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return success_response()
        return error_response(ErrorCodes.UNKNOWN)

    @swagger_auto_schema(
        tags=["member"],
        operation_summary="유저 시험 삭제 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "schedules": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="삭제할 스케줄 리스트",
                )
            },
        ),
        responses=swagger_default_schema_response(),
        operation_description="유저 토큰만 가능하며, 상태가 대기인 스케줄만 삭제됩니다.",
    )
    @transaction.atomic
    def delete(self, request):
        schedules_list = request.data.get("schedules", [])
        try:
            user = request.user
            schedules = Schedule.objects.filter(
                member_id=user.id, pk__in=schedules_list, status="W"
            )
            schedules.all().delete()
            return success_response()
        except Schedule.DoesNotExist:
            return error_response(ErrorCodes.NO_DATA)
