from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MASTER = "MASTER"
    MANAGER = "MANAGER"
