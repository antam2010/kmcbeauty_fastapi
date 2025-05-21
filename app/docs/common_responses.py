from fastapi import status

COMMON_ERROR_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "잘못된 요청",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_BAD_REQUEST",
                        "message": "요청이 잘못되었습니다.",
                    },
                },
            },
        },
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "인증 필요",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_UNAUTHORIZED",
                        "message": "인증이 필요합니다.",
                    },
                },
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "접근 권한 없음",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_FORBIDDEN",
                        "message": "허용되지 않은 작업입니다.",
                    },
                },
            },
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "리소스를 찾을 수 없음",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_NOT_FOUND",
                        "message": "요청한 리소스를 찾을 수 없습니다.",
                    },
                },
            },
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "중복 또는 충돌",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_DUPLICATE",
                        "message": "이미 존재하는 리소스입니다.",
                    },
                },
            },
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "유효성 검사 실패",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_VALIDATION_ERROR",
                        "message": "요청 데이터의 유효성 검사를 통과하지 못했습니다.",
                    },
                },
            },
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "서버 오류",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "code": "{DOMAIN}_INTERNAL_ERROR",
                        "message": "서버 내부 오류가 발생했습니다.",
                    },
                },
            },
        },
    },
}
