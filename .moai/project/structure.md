# KMCBeauty — 코드베이스 구조

> 레이어드 아키텍처 기반 FastAPI 애플리케이션

---

## 최상위 디렉터리

```
kmcbeauty_fastapi/
├── app/                  # 애플리케이션 소스 코드
├── alembic/              # DB 마이그레이션 (8개 revision)
├── tests/                # pytest 테스트 (13개 파일)
├── scripts/              # 배포·기동 스크립트
├── worker/               # Celery 작업 모듈
├── celery_app.py         # Celery 애플리케이션 팩토리
├── main.py               # FastAPI 앱 진입점
├── docker-stack.yml      # Docker Swarm 배포 스택
├── Dockerfile            # 단일 스테이지 컨테이너 빌드
├── requirements.txt      # 의존성 목록
└── .env.example          # 환경변수 문서화 템플릿
```

---

## app/ 레이어 구조

레이어 순서: **api → services → crud → models**

```
app/
├── api/                  # 라우터 레이어 (9개 라우터)
│   ├── auth.py
│   ├── user.py
│   ├── shop.py
│   ├── phonebook.py
│   ├── treatment.py
│   ├── treatment_menu.py
│   ├── treatment_menu_detail.py
│   ├── device_push_token.py
│   └── summary.py
│
├── services/             # 비즈니스 로직 레이어 (11개 서비스)
├── crud/                 # DB 접근 레이어 (10개 CRUD 모듈)
│
├── models/               # SQLAlchemy ORM 모델 (11개 테이블)
│   ├── mixins/
│   │   ├── TimestampMixin   # created_at, updated_at 자동 관리
│   │   └── SoftDeleteMixin  # deleted_at 기반 논리 삭제
│   └── (shop, user, treatment, phonebook, ...)
│
├── schemas/              # Pydantic v2 요청/응답 스키마
├── dependencies/         # FastAPI 의존성 주입
│   ├── auth.py           # OAuth2 / JWT 토큰 검증
│   └── shop.py           # 현재 샵 컨텍스트 추출
│
├── core/                 # 애플리케이션 설정·인프라
│   ├── config.py         # pydantic-settings + dotenv 로딩
│   ├── security.py       # argon2 해시 + bcrypt 레거시
│   ├── logging.py        # 로그 설정
│   ├── sentry.py         # Sentry SDK 초기화
│   ├── rate_limit.py     # slowapi 속도 제한
│   ├── redis_client.py   # Redis 연결 관리
│   ├── firebase.py       # firebase-admin 초기화
│   └── permissions.py    # 권한 헬퍼
│
├── utils/                # 유틸리티 모듈
│   ├── datetime.py       # 날짜/시간 처리
│   ├── phone.py          # 전화번호 정규화
│   ├── query.py          # 공통 쿼리 빌더
│   └── redis.py          # Redis 캐싱 헬퍼
│
└── enum/                 # 열거형 상수 (시술 상태 등)
```

---

## 레이어 책임 분리

| 레이어 | 파일 위치 | 책임 |
|--------|----------|------|
| Router (api/) | 요청 파싱, 응답 직렬화, 인증 의존성 주입 |
| Service (services/) | 비즈니스 규칙, 트랜잭션 조율, 도메인 유효성 검증 |
| CRUD (crud/) | SQLAlchemy 쿼리, 소프트 삭제 필터, 페이지네이션 |
| Model (models/) | ORM 테이블 정의, Mixin 상속 |
| Schema (schemas/) | Pydantic v2 I/O DTO, 필드 검증 |

---

## 비동기 작업 구조

```
celery_app.py                  # Celery 브로커·백엔드 설정 (Redis)
worker/
└── tasks/
    └── treatment_task.py      # auto_complete_treatment
                               # — Celery beat 30분 주기
                               # — IN_PROGRESS 상태 시술 자동 완료
```

---

## 데이터베이스 마이그레이션

```
alembic/
├── env.py          # SQLAlchemy 연결 설정
├── versions/       # 8개 revision 파일
└── alembic.ini     # 마이그레이션 설정
```

- 대상 DB: MySQL (드라이버: PyMySQL)
- 총 마이그레이션: 8개

---

## 테스트 구조

```
tests/
├── conftest.py              # 환경변수 주입 (앱 임포트 전 설정)
├── test_security.py         # 보안 단위 테스트
├── test_contract_*.py       # 계약 테스트 (API 인터페이스 검증)
├── test_perf_*.py           # 성능 테스트
└── test_regression_*.py     # 회귀·특성화 테스트
```

총 13개 테스트 파일. `conftest.py`가 앱 임포트 전 환경변수를 설정해 테스트 환경 격리를 보장함.

---

## 배포 스크립트

| 파일 | 용도 |
|------|------|
| `scripts/start_swarm.sh` | Swarm init + overlay 네트워크 생성 + 스택 배포 |
| `start_local.sh` | 로컬 개발 실행 |
| `start_stage.sh` | 스테이징 환경 실행 |
| `stop.sh` | 서비스 중지 |
