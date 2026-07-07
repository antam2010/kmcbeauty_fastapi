# KMCBeauty — 제품 개요

> 뷰티샵 예약·시술 관리를 위한 멀티샵 SaaS API 백엔드

---

## 제품 목적

KMCBeauty는 뷰티샵(피부관리, 네일, 헤어 등) 사업자가 여러 지점을 단일 플랫폼에서 운영할 수 있도록 설계된 **샵 범위 멀티테넌시** API 서버다. 각 샵은 독립된 사용자 권한 체계를 갖추고, 시술 예약부터 결제·완료 처리까지 전체 라이프사이클을 관리한다.

---

## 핵심 도메인

### 멀티테넌시 구조

| 계층 | 설명 |
|------|------|
| Shop | 최상위 테넌트 단위. 모든 리소스는 Shop에 귀속됨 |
| ShopUser | Shop에 소속된 사용자 계정 및 역할(Role) |
| Role 기반 접근 | 샵 내 권한(예: 오너, 직원)으로 API 접근 제어 |

### 시술 라이프사이클

```
RESERVED → IN_PROGRESS → COMPLETED
                ↓
            CANCELED
```

- **RESERVED**: 고객 예약 완료
- **IN_PROGRESS**: 시술 진행 중
- **COMPLETED**: 시술 완료 (자동 완료 포함 — Celery beat 30분 주기)
- **CANCELED**: 예약 취소

### 주요 기능

| 기능 | 설명 |
|------|------|
| 인증 | OAuth2 Password Flow + JWT 액세스/리프레시 토큰 |
| 시술 메뉴 관리 | 메뉴 및 세부 항목(treatment_menu, treatment_menu_detail) |
| 고객 전화번호부 | 샵별 고객 연락처 관리(phonebook) |
| 결제 수단 | 시술 건별 결제 방식 기록 |
| FCM 푸시 알림 | firebase-admin 연동, 디바이스 토큰 등록 및 알림 발송 |
| 대시보드 요약 | 샵별 통계·현황 요약 엔드포인트(summary) |
| 소프트 삭제 | `SoftDeleteMixin` 기반 논리 삭제 (물리 삭제 없음) |
| 속도 제한 | slowapi + Redis 기반 요청 횟수 제한 |

---

## API 라우터 목록

| 라우터 모듈 | 경로 접두사 | 주요 역할 |
|------------|-----------|---------|
| `auth` | `/auth` | 로그인, 토큰 발급/갱신 |
| `user` | `/users` | 사용자 등록·조회·수정 |
| `shop` | `/shops` | 샵 생성·조회·수정 |
| `phonebook` | `/phonebook` | 고객 연락처 CRUD |
| `treatment` | `/treatments` | 시술 예약·상태 변경 |
| `treatment_menu` | `/treatment-menus` | 시술 메뉴 관리 |
| `treatment_menu_detail` | `/treatment-menu-details` | 메뉴 세부 항목 관리 |
| `device_push_token` | `/device-push-tokens` | FCM 토큰 등록 |
| `summary` | `/summary` | 대시보드 요약 통계 |

---

## 비기능 요구사항

| 항목 | 현황 |
|------|------|
| 가용성 | Docker Swarm 2 레플리카, rolling update + 자동 롤백 |
| 성능 | uvloop + httptools + orjson 적용, Redis 캐싱 |
| 모니터링 | Sentry SDK (traces_sample_rate 0.2, 로컬/디버그 비활성) |
| 보안 | argon2 기본 해시 + bcrypt 레거시 지원, Fernet 대칭 암호화 |
| 데이터 안전성 | 소프트 삭제로 실수 삭제 방지 |

---

## 알려진 제약사항

- 일부 테스트(5건)가 fastapi-pagination 0.15.15 환경 비호환으로 실패 — SPEC-INFRA-001 이전부터 존재, 별도 정리 필요
- ruff 기존 lint 부채(~700건) 및 format 미적용 파일(11개)은 SPEC-INFRA-001 범위 밖 — 별도 정리 필요

> SPEC-INFRA-001(2026-07-07)으로 해소된 이슈: REDIS_URL localhost 결함, Firebase 시크릿 마운트 누락, `.env.prod` 부재
