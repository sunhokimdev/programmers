from enum import Enum


class ErrorCodes(Enum):
    NO_DATA = "조회된 데이터가 존재하지 않습니다."
    UNKNOWN = "원인을 알 수 없는 에러가 발생했습니다."
    INVALID_REQUEST_DATA = "Request 정보가 올바르지 않습니다"
    ADMIN_CONFIRM_EXCEED = "최대 응시 인원보다 크게 예약을 확정 지을 수 없습니다."
    ALREADY_RESERVATIONS = "이미 존재하는 테스트의 예약건입니다."
    OVERLAPPING_RESERVATION_LIMIT_EXCEEDED = (
        "동일 시간대의 시험 응시 인원이 5만명을 초과했습니다."
    )
    INVALID_REQUEST_DATA_TOO_LATE = "예약할 수 있는 시간이 지났습니다."
    AUTHENTICATE = "인증이 올바르지 않습니다."
