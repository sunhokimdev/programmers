from django.db import transaction
from django.db.models import Count, F, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from myapp.authentication import JWTAuthentication
from myapp.errors import ErrorCodes
from myapp.models import Schedule
from myapp.permission import IsAdmin
from myapp.serializer import (
    ModifyScheduleSerializer,
    FindAdminSchedulesSerializer,
    SaveCourseSerializer,
)
from myapp.utils import (
    success_response,
    error_response,
    swagger_default_schema_response,
)


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
@transaction.atomic
def confirm_reservations(request):
    schedules = request.data.get("reservations_list", [])

    if not isinstance(schedules, list):
        return error_response(ErrorCodes.INVALID_DATA)

    processing_reservations = Schedule.objects.select_related("test_id").filter(
        test_id__user_id=request.user.id, pk__in=schedules, status="W"
    )
    if not processing_reservations.exists():
        return error_response(ErrorCodes.INVALID_DATA)
    processing_reservations.all().update(status="C")
    return success_response()


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
@transaction.atomic
def modify_reservations(request, pk=None):
    schedules = Schedule.objects.get(pk=pk, test_id__user_id=request.user.id)

    if schedules is None:
        return error_response(ErrorCodes.NO_DATA)
    serializer = ModifyScheduleSerializer(schedules, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response()
    return error_response(ErrorCodes.INVALID_DATA)


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
@transaction.atomic
def confirm_all_reservations(request):
    schedules = Schedule.objects.select_related("test_id").filter(
        test_id__user_id=request.user.id, status="W"
    )

    if not schedules.exists():
        return error_response(ErrorCodes.NO_DATA)

    schedules_summary = (
        schedules.objects.filter(test_id__user_id=request.user.id)
        .values("test_id")
        .annotate(
            max_number=F("test_id__max_number"),
            confirmed_count=Count("id", filter=Q(status="C")),
            waiting_count=Count("id", filter=Q(status="W")),
        )
    )

    valid_schedules = schedules_summary.filter(
        max_number__lt=F("confirmed_count") + F("waiting_count")
    )

    if valid_schedules.exists():
        return error_response(ErrorCodes.ADMIN_CONFIRM_EXCEED)

    valid_schedules.all().update(status="C")
    return success_response()


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def delete_all_reservations(request, pk=None):
    user = request.user
    schedules = Schedule.objects.select_related("test_id").filter(
        test_id__user_id=user.id, test_id_id=pk
    )
    if not schedules.exists():
        return error_response(ErrorCodes.INVALID_DATA)
    schedules.all().delete()
    return success_response()


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def find_admin_reservations(request):
    user = request.user
    schedules = Schedule.objects.select_related("test_id").filter(
        test_id__user_id=user.id
    )
    serializer = FindAdminSchedulesSerializer(schedules, many=True)
    return success_response(data=serializer.data)


@swagger_auto_schema(
    methods=["post"],
    operation_summary="테스트 생성 API",
    request_body=SaveCourseSerializer,
    responses=swagger_default_schema_response(),
    operation_description="테스트 정보 등록",
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def save_course(request):
    serializer = SaveCourseSerializer(
        data=request.data, context=request.user, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return success_response()
    print(serializer.errors)
    return error_response(ErrorCodes.INVALID_DATA)
