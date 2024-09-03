from django.urls import path

from .views import (
    save_member,
    confirm_all_reservations,
    save_course,
    AdminScheduleAPIView,
)
from .views.course import find_course_list
from .views.schedule import MemberScheduleAPIView

urlpatterns = [
    # 일반인 전용 API
    path(
        "member/schedule",
        MemberScheduleAPIView.as_view(),
        name="member_schedule_api_view",
    ),
    # 어드민 전용 API
    path(
        "admin/confirm/all/<int:exam_id>",
        confirm_all_reservations,
        name="confirm_all_reservations",
    ),
    path(
        "admin/schedule",
        AdminScheduleAPIView.as_view(),
        name="api_schedule_api_view",
    ),
    path("admin/course", save_course, name="save_course"),
    # 공통 사용 API
    path("member", save_member, name="save_member"),
    path("course", find_course_list, name="find_course_list"),
]
