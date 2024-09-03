from .models import Schedule, Member, Exam
from rest_framework import serializers


class SaveScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["language", "exam"]

    def create(self, validated_data):
        validated_data["member"] = self.context
        return super().create(validated_data)


class SaveMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"


class SaveCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "name",
            "language",
            "test_start_datetime",
            "test_end_datetime",
            "max_number",
        ]

    def create(self, validated_data):
        validated_data["member"] = self.context
        return super().create(validated_data)


class FindCourseListSerializer(serializers.ModelSerializer):
    current_number = serializers.SerializerMethodField()
    exam_id = serializers.IntegerField(source="id", help_text="응시할 테스트 아이디")

    class Meta:
        model = Exam
        fields = [
            "exam_id",
            "name",
            "language",
            "test_start_datetime",
            "test_end_datetime",
            "current_number",
            "max_number",
        ]

    @classmethod
    def get_current_number(cls, obj):
        return Schedule.objects.filter(exam_id=obj, status="C").count()


class ModifyAdminScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["status", "language"]


class ModifyMemberScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        exclude = ["created_datetime", "status", "member", "exam"]


class FindMemberScheduleSerializer(serializers.ModelSerializer):
    schedule_id = serializers.IntegerField(
        source="exam.id", help_text="응시할 테스트 아이디"
    )
    test_start_datetime = serializers.DateTimeField(source="exam.test_start_datetime")

    created_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    status = serializers.CharField()
    language = serializers.CharField(source="exam.language")
    test_language = serializers.CharField(source="language")
    max_number = serializers.IntegerField(source="exam.max_number")

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
    user_name = serializers.CharField(source="member.name")
    user_email = serializers.CharField(source="member.email")
    test_name = serializers.CharField(source="exam.name")
    test_language = serializers.CharField(source="language")
    schedule_id = serializers.IntegerField(source="id")
    test_start_datetime = serializers.DateTimeField(source="exam.test_start_datetime")

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
