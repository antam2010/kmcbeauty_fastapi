import logging

from fastapi import HTTPException
from sentry_sdk import capture_exception
from starlette import status

# 기본 메시지 매핑
DEFAULT_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: ("BAD_REQUEST", "잘못된 요청입니다."),
    status.HTTP_401_UNAUTHORIZED: ("UNAUTHORIZED", "인증이 필요합니다."),
    status.HTTP_403_FORBIDDEN: ("FORBIDDEN", "접근이 금지되었습니다."),
    status.HTTP_404_NOT_FOUND: ("NOT_FOUND", "요청한 리소스를 찾을 수 없습니다."),
    status.HTTP_409_CONFLICT: ("CONFLICT", "요청이 충돌되었습니다."),
    status.HTTP_422_UNPROCESSABLE_ENTITY: (
        "UNPROCESSABLE_ENTITY",
        "요청 유효성 오류입니다.",
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: (
        "INTERNAL_ERROR",
        "서버 오류가 발생했습니다.",
    ),
}


class CustomException(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        domain: str | None = None,
        code: str | None = None,
        detail: str | None = None,
        hint: str | None = "놉",
        exception: Exception | None = None,
    ):
        # 기본 메시지 및 코드 설정
        default_code, default_detail = DEFAULT_MESSAGES.get(
            status_code,
            ("UNKNOWN_ERROR", "알 수 없는 오류입니다."),
        )
        if domain is None:
            final_code = f"{code}"
        else:
            final_code = f"{domain.upper()}_{code or default_code}"

        final_detail = detail or default_detail

        # 예외 메시지 변환 (항상 문자열, 없으면 "-")
        exception_str = str(exception) if exception is not None else "-"

        # 응답 구조 정의
        error_response = {
            "code": final_code,
            "detail": final_detail,
        }

        if hint:
            error_response["hint"] = hint

        if exception:
            error_response["exception"] = exception_str

        # 500 이상 에러는 Sentry로
        if status_code >= 500:
            capture_exception(
                exception or Exception(f"{final_code}: {final_detail} ({hint})"),
            )

        logging.warning(
            "CustomException: %s - %s (%s) | Exception: %s",
            final_code,
            final_detail,
            hint,
            exception_str,
            extra={
                "status_code": status_code,
                "domain": domain,
                "code": final_code,
                "detail": final_detail,
                "hint": hint if hint else "-",
                "exception": exception_str,
            },
        )

        super().__init__(
            status_code=status_code,
            detail=error_response,
        )
