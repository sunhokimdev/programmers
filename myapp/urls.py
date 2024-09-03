from django.urls import path

from .views import (
    save_member,
    ScheduleView,
    confirm_reservations,
    confirm_all_reservations,
    delete_all_reservations,
    modify_reservations,
    find_admin_reservations,
    save_course,
)
from .views.course import find_course_list

urlpatterns = [
    # 일반인 전용 API
    path("reservations", ScheduleView.as_view(), name="reservations"),
    # 어드민 전용 API
    path("admin/course", save_course, name="save_course"),
    # 공통 사용 API
    path("member", save_member, name="save_member"),
    path("course", find_course_list, name="find_course_list"),
    path("reservations/<int:pk>", ScheduleView.as_view(), name="reservations"),
    path("admin/confirm", confirm_reservations, name="confirm_reservations"),
    path(
        "admin/confirm/all", confirm_all_reservations, name="confirm_all_reservations"
    ),
    path(
        "admin/delete/all/<int:pk>",
        delete_all_reservations,
        name="delete_all_reservations",
    ),
    path("admin/modify/<int:pk>", modify_reservations, name="modify_reservations"),
    path("admin/reservations", find_admin_reservations, name="find_admin_reservations"),
]
