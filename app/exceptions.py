from fastapi import HTTPException
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
        domain: str,
        code: str | None = None,
        message: str | None = None,
    ):
        # 기본 메시지 지정
        default_code, default_message = DEFAULT_MESSAGES.get(
            status_code, ("UNKNOWN_ERROR", "알 수 없는 오류입니다.")
        )

        final_code = f"{domain.upper()}_{code or default_code}"
        final_message = message or default_message

        super().__init__(
            status_code=status_code,
            detail={
                "code": final_code,
                "message": final_message,
            },
        )
