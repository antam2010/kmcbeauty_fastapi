---
name: security-argon2-migration
description: Password hashing uses argon2id default with bcrypt verify-only backward-compat and rehash-on-login upgrade
metadata:
  type: project
---

Password hashing was migrated from bcrypt-only to argon2id-default with backward compatibility.

**Why:** argon2id is the stronger modern default, but existing users have bcrypt hashes in the DB and must not get locked out. Old hashes auto-upgrade to argon2 on successful login.

**How to apply:**
- `app/core/security.py`: `pwd_context = CryptContext(schemes=["argon2","bcrypt"], deprecated=["bcrypt"], default="argon2")`. `hash_password` always emits `$argon2id$...`. `verify_password` still verifies bcrypt. `verify_and_upgrade_password(plain, hash) -> (valid, new_hash|None)` wraps passlib `verify_and_update`.
- Upgrade path is rehash-on-login: `auth_service.authenticate_user_service` calls `verify_and_upgrade_password`, and when `new_hash is not None` persists via `_persist_upgraded_password_hash(db, user, new_hash)`. That write-back is best-effort — a `SQLAlchemyError` on commit rolls back + logs a warning (no password value logged) but the already-authenticated user still logs in (never 401/500 a valid credential over a failed upgrade).
- requirements.txt pins `argon2-cffi==23.1.0` + `argon2-cffi-bindings==21.2.0`. KEEP `bcrypt==4.0.1` and `passlib==1.7.4` (passlib 1.7.4 breaks with bcrypt>=4.1 because it reads bcrypt's removed `__about__`; bcrypt stays for legacy verify only). Do NOT bump bcrypt.
- Do NOT weaken SECURITY-001 auth logic (token rotation/role/exception handling) when touching this area — only the hashing scheme + upgrade path changed. See [[project-fastapi-layout]].

**MANUAL VERIFY (no python interpreter in this env, see [[env-bash-denied]]):** run `python -m pytest tests/test_password_hash_argon2_migration.py -v` and `ruff check app/ tests/`. Confirm argon2 default params are acceptable for the deployment (passlib argon2 defaults: memory_cost ~=64MiB / time_cost=2 / parallelism=... — tune in CryptContext if the host is memory-constrained).
