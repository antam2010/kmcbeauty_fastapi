from enum import Enum


class TreatmentStatus(str, Enum):
    RESERVED = "RESERVED"
    VISITED = "VISITED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    COMPLETED = "COMPLETED"

    @property
    def label(self) -> str:
        return {
            TreatmentStatus.RESERVED: "예약됨",
            TreatmentStatus.VISITED: "방문 및 시술 완료",
            TreatmentStatus.CANCELLED: "취소됨",
            TreatmentStatus.NO_SHOW: "노쇼",
            TreatmentStatus.COMPLETED: "시술 완료",
        }.get(self.value, "Unknown")


class PaymentMethod(str, Enum):
    CARD = "CARD"  # 카드 결제
    CASH = "CASH"  # 현금 결제
    UNPAID = "UNPAID"  # 미수금

    @property
    def label(self) -> str:
        return {
            PaymentMethod.CARD: "카드 결제",
            PaymentMethod.CASH: "현금 결제",
            PaymentMethod.UNPAID: "미수금",
        }.get(self.value, "Unknown")

    @property
    def is_paid(self) -> bool:
        """결제 수단이 결제 완료 상태인지 확인."""
        return self in {PaymentMethod.CARD, PaymentMethod.CASH}

    @property
    def is_unpaid(self) -> bool:
        """결제 수단이 미수금 상태인지 확인."""
        return self == PaymentMethod.UNPAID
