---
name: native-api-client-topology
description: kmcbeauty-native live axios client + service/type dirs after REFACTOR-001 deleted the dead duplicates
metadata:
  type: project
---

The Expo app `kmcbeauty-native` previously had THREE parallel axios API clients (triple-client duplication, DIAGNOSIS-2026-07-02). SPEC-REFACTOR-001 (completed) deleted the two dead clients.

**LIVE client: `src/api/client.ts`** (the only remaining client)
- Reads the access token from the Zustand store (`useAuthStore.getState().accessToken`), not AsyncStorage.
- Refresh path uses the HttpOnly cookie only (`POST /auth/refresh` with `withCredentials: true`) and writes the new access token back to the Zustand store. It never manually stores a refresh token.
- Live consumer chain: `app/login.tsx` -> `useAuthStore().login` (`src/stores/authStore.ts`) -> `authApiService` (`src/api/services/auth.ts`) -> `BaseApiService` (`src/api/services/base.ts`) -> `src/api/client.ts`.
- Also used live by `src/services/api/treatment-menu.ts` and `src/services/api/phonebook.ts` (imported by management components).

**LIVE services dir: `src/api/services/*`** — auth, base, dashboard, invite, phonebook, shop, staff, treatment, treatmentMenu, index. These are what the app actually consumes (confirmed via SPEC-API-001 verification 2026-07-03).

**DELETED by REFACTOR-001 (do NOT resurrect — confirmed absent 2026-07-03):**
- `src/api/apiClient.ts` (was the dead client)
- `src/api/index.ts` (was the semi-dead client)
- `src/services/api/auth.ts`, `booking.ts`, `dashboard.ts`, `shop.ts` (only `phonebook.ts` + `treatment-menu.ts` survive in `src/services/api/`)

**Why:** SECURITY-001 token invariants (SecureStore single source, no plaintext token storage/logging) live in `client.ts` + `authStore.ts` and must be preserved. REFACTOR-001 dead-file deletion must be preserved — never recreate the deleted files.

**How to apply:** When asked about the app's auth/token flow, `client.ts` is authoritative. The type-system entry `@/src/types` resolves via `src/types/index.ts` -> `unified.ts` (which re-exports auth/common/dashboard/phonebook/shop/treatment/user), so `src/types/{treatment,auth,common}.ts` are the LIVE API types. Note `src/types/user.ts` `StaffUser*` is a DEAD unimported duplicate (the live `StaffUser*` lives in `src/api/services/staff.ts`).
