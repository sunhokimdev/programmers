from .models import Schedule, Member, Course
from rest_framework import serializers, viewsets


class SaveScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["language", "course_id"]

    def create(self, validated_data):
        validated_data["member_id"] = self.context
        return super().create(validated_data)


class SaveMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"


class SaveCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "name",
            "language",
            "test_start_datetime",
            "test_end_datetime",
            "max_number",
        ]

    def create(self, validated_data):
        validated_data["member_id"] = self.context
        return super().create(validated_data)


class FindCourseListSerializer(serializers.ModelSerializer):
    current_number = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="id", help_text="응시할 테스트 아이디")

    class Meta:
        model = Course
        fields = [
            "course_id",
            "name",
            "language",
            "test_start_datetime",
            "test_end_datetime",
            "current_number",
            "max_number",
        ]

    @classmethod
    def get_current_number(cls, obj):
        return Schedule.objects.filter(course_id=obj, status="C").count()


class ModifyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["language", "status"]


class FindScheduleSerializer(serializers.ModelSerializer):
    test_start_datetime = serializers.DateTimeField(
        source="schedule_id.test_start_datetime"
    )
    language = serializers.CharField(source="schedule_id.language")
    test_language = serializers.CharField(source="language")
    schedule_id = serializers.IntegerField(source="id")
    max_number = serializers.IntegerField(source="schedule_id.max_number")

    class Meta:
        model = Schedule
        fields = [
            "schedule_id",
            "created_datetime",
            "status",
            "max_number",
            "language",
            "test_language",
            "test_start_datetime",
        ]


class FindAdminSchedulesSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="member_id.name")
    user_email = serializers.CharField(source="member_id.email")
    test_name = serializers.CharField(source="schedule_id.name")
    test_language = serializers.CharField(source="language")
    schedule_id = serializers.IntegerField(source="id")
    test_start_datetime = serializers.DateTimeField(
        source="schedule.test_start_datetime"
    )

    class Meta:
        model = Schedule
        fields = [
            "schedule_id",
            "test_name",
            "status",
            "user_name",
            "user_email",
            "test_language",
            "test_start_datetime",
        ]
