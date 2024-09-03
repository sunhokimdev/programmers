from django.db import models


# Create your models here.
class Member(models.Model):
    TYPE = [("N", "Normal"), ("A", "Admin")]
    SEX = [("M", "Male"), ("F", "Female")]
    name = models.CharField(max_length=50, verbose_name="유저 이름")
    email = models.CharField(max_length=255, verbose_name="유저 이메일")
    birthday = models.CharField(max_length=14, verbose_name="생일(format:yyyy-mm-dd)")
    company = models.CharField(
        max_length=255, null=True, verbose_name="회사이름, 존재하지 않을 시 null"
    )
    type = models.CharField(
        max_length=1, choices=TYPE, default="N", verbose_name="N: 일반인, A: 어드민"
    )
    sex = models.CharField(max_length=1, choices=SEX, verbose_name="M: 남자, F: 여자")

    class Meta:
        db_table = "member"


class Course(models.Model):
    name = models.CharField(max_length=50)
    language = models.TextField(
        verbose_name="테스트에 응시할 수 있는 언어 종류(구분은 ,로 구분)"
    )
    test_start_datetime = models.DateTimeField(verbose_name="테스트 시작일자")
    test_end_datetime = models.DateTimeField(verbose_name="테스트 종료일자")
    max_number = models.IntegerField(
        verbose_name="최대 응시 인원(= 최대 예약 확정 인원)"
    )
    member_id = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        null=False,
        verbose_name="테스트를 생성한 어드민 user_id",
    )

    class Meta:
        db_table = "course"


class Schedule(models.Model):
    STATUS = [("C", "Confirmed"), ("W", "Waiting")]
    created_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name="예약 생성 일자"
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS,
        default="W",
        verbose_name="예약 상태(C: 확정, W: 대기 상태)",
    )
    language = models.CharField(max_length=20, verbose_name="응시할 언어")
    member_id = models.ForeignKey(
        Member, on_delete=models.CASCADE, null=False, verbose_name="응시할 유저 아이디"
    )
    course_id = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=False, verbose_name="테스트 고유 번호"
    )

    class Meta:
        db_table = "schedule"
