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

    @classmethod
    def unfinished_statuses(cls) -> list[str]:
        return [cls.RESERVED, cls.VISITED]

    @classmethod
    def for_expected_sales(cls) -> list[str]:
        """예상매출에 포함할 상태들."""
        return [cls.RESERVED.value, cls.VISITED.value, cls.COMPLETED.value]

    @classmethod
    def for_actual_sales(cls) -> str:
        """실매출(완료 기준)은 COMPLETED만."""
        return cls.COMPLETED.value


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

    @classmethod
    def paid_methods(cls) -> list[str]:
        """결제 완료 방식(카드/현금) 배열 리턴."""
        return [cls.CARD.value, cls.CASH.value]

    @classmethod
    def unpaid_methods(cls) -> list[str]:
        """외상 결제 방식(미수금) 배열 리턴."""
        return [cls.UNPAID.value]
