from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MASTER = "MASTER"
    MANAGER = "MANAGER"

    @property
    def label(self) -> str:
        return {
            UserRole.ADMIN: "관리자",
            UserRole.MASTER: "원장",
            UserRole.MANAGER: "매니저",
        }.get(self.value, "Unknown")
