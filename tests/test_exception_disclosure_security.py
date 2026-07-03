"""REQ-SEC-004 정보 노출 관리 테스트.

대상: app/exceptions.py
- 비-debug 환경에서 raw exception 문자열이 응답에 노출되지 않음 (AC-004-2)
- debug 환경에서는 노출 허용 (AC-004-3)
"""

from app import exceptions
from app.exceptions import CustomException


def _build_exc(monkeypatch, app_env: str) -> dict:
    # exceptions 모듈이 import 시점에 캡처한 APP_ENV 를 테스트 값으로 교체
    monkeypatch.setattr(exceptions, "APP_ENV", app_env)
    exc = CustomException(
        status_code=400,
        domain="TEST",
        detail="something failed",
        exception=ValueError("internal db password leak details"),
    )
    return exc.detail


def test_non_debug_hides_raw_exception(monkeypatch):
    """AC-004-2: local(비-debug) 환경에서는 exception 필드 미노출."""
    detail = _build_exc(monkeypatch, "local")
    assert "exception" not in detail


def test_production_hides_raw_exception(monkeypatch):
    """AC-004-2: production 환경에서도 exception 필드 미노출."""
    detail = _build_exc(monkeypatch, "production")
    assert "exception" not in detail


def test_debug_exposes_raw_exception(monkeypatch):
    """AC-004-3: debug 환경에서는 exception 필드가 노출될 수 있다."""
    detail = _build_exc(monkeypatch, "debug")
    assert "exception" in detail
    assert "internal db password leak details" in detail["exception"]
