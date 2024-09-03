from django.db.models import Q, Count
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status

from myapp.errors import ErrorCodes
from myapp.models import Schedule


def success_response(data=None, status_code=status.HTTP_200_OK):
    response = {"result": "success", "data": data, "error": None}
    return Response(response, status=status_code)


def error_response(
    error_code: ErrorCodes, data=None, status_code=status.HTTP_400_BAD_REQUEST
):
    error_message = error_code.value
    response = {
        "result": "error",
        "data": data,
        "error": {"code": error_code.name, "message": error_message},
    }
    return Response(response, status=status_code)


def swagger_default_schema_response(additional_properties=None):
    swagger_schema_response = {
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "result": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="결과 값(Success: 성공, error: 에러)",
                ),
                "data": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=True,
                    description="성공 시 응답 데이터 값, 실패 시 null",
                    properties=additional_properties or {},
                ),
                "error": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=True,
                    description="성공 시 None, 에러 발생 시 에러 코드와 에러 메시지 출력",
                    properties={
                        "code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 코드 반환",
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 메시지 반환",
                        ),
                    },
                ),
            },
        ),
    }
    return swagger_schema_response


def get_error_codes_overlapping_and_reservation_counts(exam):
    overlapping_and_count = (
        Schedule.objects.filter(
            Q(exam_id__test_start_datetime__lt=exam.test_end_datetime)
            & Q(exam_id__test_end_datetime__gt=exam.test_start_datetime)
            | Q(exam_id=exam.id)
        )
        .filter(status="C")
        .aggregate(
            overlapping_count=Count(
                "id",
                filter=Q(
                    exam_id__test_start_datetime__lt=exam.test_end_datetime,
                    exam_id__test_end_datetime__gt=exam.test_start_datetime,
                ),
            ),
            current_reservation_count=Count("id", filter=Q(exam_id=exam.id)),
        )
    )

    if overlapping_and_count["overlapping_count"] > 50000:
        return ErrorCodes.OVERLAPPING_RESERVATION_LIMIT_EXCEEDED

    if overlapping_and_count["current_reservation_count"] >= exam.max_number:
        return ErrorCodes.ADMIN_CONFIRM_EXCEED

    return None
