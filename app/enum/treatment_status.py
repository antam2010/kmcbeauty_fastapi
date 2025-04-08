from enum import Enum

class TreatmentStatus(str, Enum):
    RESERVED = "RESERVED"     # 예약됨
    VISITED = "VISITED"       # 방문 및 시술 완료
    CANCELLED = "CANCELLED"   # 취소됨
    NO_SHOW = "NO_SHOW"       # 노쇼
