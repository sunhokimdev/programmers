from rest_framework import status
from rest_framework.views import APIView

from myapp.authentication import JWTAuthentication
from myapp.errors import ErrorCodes
from myapp.models import Schedule, Course
from myapp.permission import IsNormal
from myapp.serializer import (
    FindScheduleSerializer,
    SaveScheduleSerializer,
    ModifyScheduleSerializer,
)
from myapp.utils import success_response, error_response


class ScheduleView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsNormal,)

    @staticmethod
    def get(request):
        users = request.user
        schedule = Schedule.objects.select_related("course_id").filter(
            member_id=users.id
        )
        serializer = FindScheduleSerializer(schedule, many=True)
        return success_response(data=serializer.data)

    @staticmethod
    def post(request):
        test = Course.objects.get(id=request.data["course_id"])
        if test is None or not request.data["language"] in test.language:
            return error_response(ErrorCodes.SAVE_RESERVATIONS_01)

        reservations = Schedule.objects.filter(
            member_id=request.user.id, course_id=request.data["course_id"]
        )
        if reservations is not None and reservations.exists():
            return error_response(ErrorCodes.ALREADY_RESERVATIONS)

        serializer = SaveScheduleSerializer(data=request.data, context=request.user)
        if serializer.is_valid():
            serializer.save()
            return success_response()
        return error_response(ErrorCodes.INVALID_REQUEST_DATA)

    @staticmethod
    def patch(request, pk=None):
        user = request.user
        try:
            reservation = Schedule.objects.get(user_id=user.id, pk=pk, status="W")
            if reservation is None:
                return error_response(ErrorCodes.INVALID_DATA)
            serializer = ModifyScheduleSerializer(reservation, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response()
            else:
                return error_response(ErrorCodes.INVALID_DATA)

        except Schedule.DoesNotExist:
            return error_response(ErrorCodes.INVALID_DATA)

    @staticmethod
    def delete(request, pk=None):
        try:
            user = request.user
            reservation = Schedule.objects.get(user_id=user.id, pk=pk, status="W")
            reservation.delete()
            return success_response(status_code=status.HTTP_204_NO_CONTENT)
        except Schedule.DoesNotExist:
            return error_response(
                ErrorCodes.INVALID_DATA,
                status_code=status.HTTP_404_NOT_FOUND,
            )
