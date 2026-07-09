---
name: project-invite-expire-unit
description: ShopInviteCreateRequest.expire_in is consumed as SECONDS, but its field description wrongly says minutes
metadata:
  type: project
---

`app/schemas/shop_invite.py::ShopInviteCreateRequest.expire_in` has `default=60*60*24*7` and a field `description="초대코드 만료 기간(분 단위)"` (says MINUTES).

The ACTUAL consuming code `app/crud/shop_invite_curd.py::create_invite` computes `expired_at = datetime.now(UTC) + timedelta(seconds=expire_in)` — i.e. **expire_in is SECONDS**. Default = 604800s = 7 days. So the field description string is WRONG (should say seconds).

**Why it matters:** SPEC-API-001 REQ-API-003.2 requires the app to align its expire_in unit to the backend's *real behavior* (seconds), not to the misleading doc string. The SPEC marks 003.2 as [app], so the app side owns the alignment. The misleading backend `description="분 단위"` is a backend doc bug but was NOT in expert-backend's file-ownership scope for API-001 (only treatment/shop/user schemas), so it was left unchanged.

**How to apply:** If later asked to fix the backend invite doc, change the description to seconds (and consider renaming to expire_in_seconds). Do not change the default or the timedelta(seconds=...) logic — that is the source of truth. Note the CRUD filename is misspelled `shop_invite_curd.py` (curd, not crud).
