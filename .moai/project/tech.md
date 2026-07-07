# KMCBeauty — 기술 스택 및 인프라

---

## 런타임 환경

| 항목 | 버전 / 값 |
|------|----------|
| Python | 3.13-slim (Dockerfile 기준) |
| ruff target-version | py313 |
| 컨테이너 베이스 이미지 | `python:3.13-slim` |
| 실행 사용자 | non-root (Dockerfile 설정) |

---

## 핵심 프레임워크

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| FastAPI | 0.139 | Web API 프레임워크 |
| Uvicorn | 0.49 | ASGI 서버 |
| uvloop | — | 고성능 이벤트 루프 |
| httptools | — | HTTP 파서 (uvicorn 성능 최적화) |
| orjson | — | 고속 JSON 직렬화 |

---

## 데이터베이스 & ORM

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| SQLAlchemy | 2.0.51 | ORM (비동기 세션 포함) |
| Alembic | 1.18.5 | DB 스키마 마이그레이션 |
| PyMySQL | — | MySQL 드라이버 |

- 대상 DB: **MySQL**
- 마이그레이션 수: 7개 revision

---

## 데이터 검증 & 설정

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Pydantic | 2.13 | 요청/응답 스키마 검증 |
| pydantic-settings | — | `.env` 기반 설정 관리 |

---

## 인증 & 보안

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| PyJWT | — | JWT 토큰 생성·검증 |
| argon2-cffi | — | 기본 비밀번호 해시 알고리즘 |
| passlib | — | 비밀번호 해시 추상화 (bcrypt 레거시 지원) |
| bcrypt | 4.0.1 (pinned `<4.1`) | 레거시 해시 지원 (passlib 호환성) |
| cryptography (Fernet) | — | 대칭 암호화 |

> **주의:** bcrypt는 passlib 호환성 문제로 `4.0.1`로 고정됨. 업그레이드 시 검증 필요.

---

## 캐시 & 비동기 작업

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Redis 클라이언트 | 6.4 | 캐싱, 속도 제한 카운터, Celery 브로커 |
| Celery | 5.6.3 | 비동기 태스크 큐 + beat 스케줄러 |

Celery 작업:
- `auto_complete_treatment`: 30분 주기, `IN_PROGRESS` 상태 시술 자동 완료

---

## 추가 기능 라이브러리

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| slowapi | — | Redis 기반 요청 속도 제한 |
| fastapi-pagination | — | 커서/페이지 기반 페이지네이션 |
| firebase-admin | 7.5 | FCM 푸시 알림 발송 |
| Sentry SDK | 2.64 | 에러 추적 및 성능 트레이싱 |

Sentry 설정: `traces_sample_rate=0.2`, 로컬·디버그 환경에서 비활성화.

---

## 개발 도구

| 도구 | 버전 | 용도 |
|------|------|------|
| ruff | 0.14.0 | 린트 + 포맷 (line-length 88, target-version py313) |
| pytest | 8.4.2 | 테스트 프레임워크 |
| pytest-cov | 6.1.1 | 커버리지 측정 (report-only, --fail-under 게이트 없음) |
| coverage | 7.6.10 | 커버리지 리포트 백엔드 |
| pre-commit | — | ruff lint+format 커밋 훅 (`.pre-commit-config.yaml`) |

---

## 인프라

### Docker Swarm 스택 (`docker-stack.yml`)

| 서비스 | 레플리카 | 포트 | 비고 |
|--------|---------|------|------|
| `kmcbeauty_api` | 2 | `:3100` (내부) | rolling update + 자동 롤백 |
| `redis` | 1 | (내부) | redis:7-alpine, appendonly, `redis_data` 볼륨 |
| `celery_worker` | 2 | — | 태스크 처리 |
| `celery_beat` | 1 | — | 단일 레플리카 (중복 디스패치 방지) |

- 외부 포트 노출 없음: NGINX가 `shared_network_prod` overlay 네트워크를 통해 리버스 프록시
- 헬스체크: `curl /health` (Dockerfile 설정)

### 환경변수 관리

- 로컬 개발: `.env` 파일 (오버레이 DNS 불필요)
- Swarm 배포: `.env.prod` 파일 (`env_file` 지시어, `.gitignore`에 포함)
- `.env.example`: 로컬 변수 문서화 템플릿
- `.env.prod.example`: 운영 변수 문서화 템플릿 (`.env.prod` 생성 기준)

### CI/CD 파이프라인

| 파일 | 트리거 | 역할 |
|------|--------|------|
| `.github/workflows/ci.yml` | PR 오픈 / push | ruff check + format-check + pytest (Python 3.13, pip 캐시) |
| `.github/workflows/cd.yml` | main 병합 | GHCR 이미지 빌드·푸시 + SSH Swarm 배포 |

- 이미지 레지스트리: `ghcr.io/antam2010/kmcbeauty-api:<sha>` (불변 SHA 태그)
- 배포 시 `IMAGE_TAG` 환경변수 치환으로 `:latest` 함정 회피
- Docker secrets: `firebase_service_account` (api, celery_worker, celery_beat 모두 마운트)
- CD 수동 승인 게이트: GitHub environment `production` 보호 규칙

---

## 의존성 관리

- `requirements.txt` 단일 파일로 관리
- lock 파일(poetry.lock, pip-tools generated) 없음 — 재현 가능한 빌드를 위해 도입 권장
- uv 도입 평가 완료 — 현재 pip 방식 유지 결정 (평가 기록: `docs/deployment.md`)
