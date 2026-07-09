---
name: project-unbounded-list-caps
description: SPEC-PERF-001 REQ-PERF-004 defensive .limit() caps for the 4 unbounded list[...] endpoints, centralized in app/core/limits.py
metadata:
  type: project
---

SPEC-PERF-001 REQ-PERF-004 added defensive server-side `.limit(N)` caps to the four
`response_model=list[...]` (non-paginated) endpoints. Approach (a) everywhere: internal
LIMIT + warning log if returned count >= cap; response shape stays a plain array
(API-001 contract preserved — NO pagination/envelope added).

Caps live in `app/core/limits.py`:
- PHONEBOOK_GROUP_ITEMS_MAX = 1000 → `phonebook_crud.get_all_phonebooks_by_shop`
  (GET /phonebooks/groups?with_items=true) — widest growth path, so highest cap.
- SHOP_USERS_MAX = 500 → `shop_user_crud.get_shop_users_by_shop_id` (GET /shops/{id}/users)
- MENU_DETAILS_MAX = 500 → `treatment_menu_crud.get_treatment_menu_details_by_user`
  (GET /treatment-menus/{menu_id}/details)
- USER_DEVICE_TOKENS_MAX = 500 → `device_push_token_crud.get_device_tokens_by_user`
  (GET /device-tokens/me). NOTE: the sibling `get_device_tokens_by_shop` (FCM multicast
  path, NOT a list endpoint) was intentionally left uncapped — out of REQ-PERF-004 scope.

**Why:** these queries ended in `.all()` with no LIMIT, so a single response could grow
unbounded. The codebase already used this exact convention (`treatment_crud.get_treatments_to_autocomplete`
has `.limit(100)`), so caps extend an existing pattern rather than inventing one.

**How to apply:** if adding a new `list[...]` endpoint, add a cap constant here + `.limit()`
+ cap-hit warning. Do NOT convert these to `Page[...]` — the app consumes them as arrays.
`Page[...]` endpoints are already bounded by fastapi-pagination `le=100` (do not touch).

The `/device-tokens` router prefix is `/device-tokens` (NOT `/device-push-tokens` as
SPEC-PERF-001 text says — that path in the spec is stale).
