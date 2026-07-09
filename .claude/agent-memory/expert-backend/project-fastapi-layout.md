---
name: project-fastapi-layout
description: kmcbeauty_fastapi backend structure and testing setup constraints
metadata:
  type: project
---

FastAPI 0.115 + SQLAlchemy 2.0 (sync) + MySQL + Redis + python-jose. Layout: app/api (routers), app/services, app/crud, app/dependencies, app/schemas, app/core, app/utils/redis.

**Config-at-import gotcha:** `app/core/config.py` reads env vars at import time with `int(os.getenv(...))` casts (SECRET_KEY, ALGORITHM, ACCESS/REFRESH_TOKEN_EXPIRE_SECONDS, FERNET_KEY). Any test importing app.* modules crashes unless these env vars are set FIRST. `tests/conftest.py` at repo root sets them via os.environ.setdefault before imports. FERNET_KEY must be a valid Fernet key (44-char url-safe base64) because security.py builds `Fernet(FERNET_KEY)` at import.

**Auth token model:** refresh tokens stored in Redis keyed by user_id (auth:refresh:{id}); Redis storage IS the allowlist, so logout = delete from Redis = revocation (no separate blacklist needed). refresh_access_token checks saved_token == raw_token.

**Ownership gate:** shop-scoped access uses `get_current_shop` dependency (dependencies/shop.py) -> `get_user_shop_by_id(db, user.id, shop_id)`. shop.py's own /{shop_id}/* routes instead gate via `get_shop_user(db, shop_id, user.id)` membership check. Both enforce ownership.

**Password hashing:** argon2id is the default new-hash scheme; bcrypt kept verify-only for legacy DB hashes. `app/core/security.py` uses `CryptContext(schemes=["argon2","bcrypt"], deprecated=["bcrypt"], default="argon2")` and exposes `verify_and_upgrade_password()` (wraps passlib `verify_and_update`). Rehash-on-login write-back lives in `auth_service.authenticate_user_service` via `_persist_upgraded_password_hash` (best-effort: commit failure rolls back + logs but still logs the user in). See [[security-argon2-migration]].

**Testing:** tests live at `kmcbeauty_fastapi/tests/` (NOT the monorepo root — Glob from the monorepo cwd returns them as `tests\...`, but the real path is under `kmcbeauty_fastapi/`). conftest.py injects required env vars via `os.environ.setdefault` BEFORE any `app.*` import (config-at-import gotcha above). Test files are named by SPEC concern (`test_*_security.py`, `test_*_fix.py`, `test_*_perf.py`). DB-free pattern: hand-rolled `SpySession`/`SpyQuery` classes (per test file) record method calls — `SpyQuery.filter/join/options/order_by/limit` return self, `.all()`/`.first()` return fixed rows; assert on recorded criteria/limit or compiled SQL (`str(stmt.compile(compile_kwargs={"literal_binds": True}))`). Also `monkeypatch.setattr(module, "helper", fake)` to stub Redis/CRUD/DB. No pyproject.toml/requirements in tests dir; ruff config + `requirements.txt` (SQLAlchemy==2.0.51) at `kmcbeauty_fastapi/` root, line-length 88, targets py312.
