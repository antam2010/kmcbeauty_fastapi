---
name: project-soft-delete-treatment
description: Treatment/TreatmentItem/ShopUser have NO SoftDeleteMixin; only status-transition or hard-delete are consistent options for deleting a treatment
metadata:
  type: project
---

FIX-001 established which models carry `SoftDeleteMixin` (deleted_at + soft_delete()/is_deleted()): only **Phonebook, Shop, TreatmentMenu, TreatmentMenuDetail, User**.

Models WITHOUT soft-delete (verified 2026-07-03): **Treatment, TreatmentItem, ShopUser** — no `deleted_at` column. `tests/test_soft_delete_filter_fix.py::test_treatment_models_have_no_deleted_at_column` asserts Treatment/TreatmentItem must NOT have deleted_at (over-application guard).

**Why it matters:** SPEC-API-001 REQ-API-001 asks for `DELETE /treatments/{id}` "soft-delete consistent with FIX-001". But Treatment cannot be soft-deleted without a schema/migration change (out of scope + would break the FIX-001 guard test). Options for a treatment-delete endpoint that stay consistent: (a) status transition to `CANCELLED` (TreatmentStatus enum already has it), or (b) hard delete (Treatment.treatment_items cascades via `all, delete-orphan`; shop FK is ondelete=CASCADE). Do NOT add deleted_at to Treatment inside API-001.

**How to apply:** When a delete is requested on a model, first grep the model header for `SoftDeleteMixin`. Soft-delete pattern = `model.soft_delete()` or `model.deleted_at = datetime.now(UTC)` then `db.commit()` (see phonebook_service.delete_phonebook_service, treatment_menu_service.delete_treatment_menu_service). If the model lacks the mixin, a soft-delete is impossible without a migration — choose status-transition or hard-delete and document it. See [[project-fastapi-layout]].
