from enum import Enum


class ErrorCodes(Enum):
    NO_DATA = "조회된 데이터가 존재하지 않습니다."
    INVALID_DATA = "Request 정보가 올바르지 않습니다"
    INVALID_REQUEST_DATA = "Request 정보가 올바르지 않습니다"
    ADMIN_CONFIRM_EXCEED = "최대 응시 인원보다 크게 예약을 확정 지을 수 없습니다."
    SAVE_RESERVATIONS_01 = "응시할 언어가 올바르지 않습니다."
    ALREADY_RESERVATIONS = "이미 존재하는 테스트의 예약건입니다."
