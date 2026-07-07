# 배포 가이드 (SPEC-INFRA-001)

KMCBeauty API 의 Docker Swarm 무중단 배포 · CI/CD · 시크릿/마이그레이션/롤백 운영 문서.

- 오케스트레이션: Docker Swarm 단일 스택(`docker-stack.yml`)
- 레지스트리: GHCR (`ghcr.io/antam2010/kmcbeauty-api:<git-sha>`)
- CI/CD: GitHub Actions (`.github/workflows/ci.yml`, `cd.yml`)
- MySQL 은 컨테이너 외부(관리형/호스트)에 존재하며 이 스택에 포함하지 않는다.

---

## 1. 환경 변수 분리 (REQ-INFRA-001)

| 구분 | 파일 | REDIS_URL | 용도 |
|---|---|---|---|
| 로컬 개발 | `.env` | `redis://localhost:6379/0` | uvicorn/로컬 실행 |
| 배포(Swarm) | `.env.prod` | `redis://redis:6379/0` | 오버레이 서비스 DNS |

- 배포는 **`.env.prod` 만** 참조한다. 로컬 `.env` 를 배포에 사용하면 오버레이에서
  Redis 해석이 깨진다(결함 재발).
- `.env.prod` 는 저장소에 커밋하지 않는다(`.gitignore` 차단). 템플릿은 `.env.prod.example`.
- 매니저 노드에서 최초 1회:

  ```bash
  cp .env.prod.example .env.prod
  # 편집하여 SECRET_KEY / FERNET_KEY / DATABASE_URL 등 실제 값을 채운다
  ```

---

## 2. Firebase 시크릿 (REQ-INFRA-002)

Firebase 서비스 계정 키는 파일이 아니라 **Docker secret** 으로 주입한다.
컨테이너 내부 경로는 `docker-stack.yml` 의 `environment` 에서
`/run/secrets/firebase_service_account` 로 고정된다.

매니저 노드에서 최초 1회 등록:

```bash
docker secret create firebase_service_account ./firebase-service-account.json
```

- 스택은 이 시크릿을 `kmcbeauty_api`, `celery_worker`, `celery_beat` 세 서비스에 마운트한다
  (셋 다 `celery_app` → `app.core.firebase` 를 import 하므로 초기화 실패 방지).
- 키 로테이션 시: 새 시크릿을 만들고(`..._v2`) 스택의 참조를 갱신한 뒤 재배포한다.
  (Docker secret 은 불변이므로 동일 이름 갱신이 아니라 새 이름 + 참조 교체가 원칙.)

---

## 3. 불변 이미지 태그 (REQ-INFRA-003)

- 모든 앱 서비스는 `image: ${IMAGE_TAG:-kmcbeauty-api:local}` 로 주입한다.
- 운영/CD 배포는 반드시 **불변 커밋 SHA 태그**를 주입한다:

  ```bash
  IMAGE_TAG=ghcr.io/antam2010/kmcbeauty-api:<git-sha> \
    docker stack deploy -c docker-stack.yml kmcbeauty
  ```

- `latest` 가변 태그는 사용하지 않는다(latest-tag digest 함정 → 롤링 배포 파손).
- `IMAGE_TAG` 미지정 폴백(`kmcbeauty-api:local`)은 단일 노드 로컬 빌드 전용이다.
  멀티 노드/운영에서 IMAGE_TAG 를 누락하면 노드에 이미지가 없어 pull 이 즉시 실패한다.

---

## 4. 헬스체크 기반 롤링 게이팅 (REQ-INFRA-004)

`kmcbeauty_api` 서비스는 서비스 레벨 헬스체크(`curl /health`)와 함께
다음 `update_config` 로 무중단 롤링을 보장한다.

| 키 | 값 | 의미 |
|---|---|---|
| `order` | `start-first` | 새 태스크를 먼저 띄운 뒤 구 태스크 종료 |
| `monitor` | `30s` | 새 태스크가 이 시간 동안 healthy 유지해야 성공 |
| `max_failure_ratio` | `0` | 한 태스크라도 실패하면 롤백 트리거 |
| `failure_action` | `rollback` | 실패 시 직전 정상 태스크로 자동 롤백 |
| `parallelism` | `1` | 한 번에 한 레플리카씩 갱신 |

---

## 5. 마이그레이션 (expand/contract, REQ-INFRA-005)

배포 파이프라인은 스택 업데이트 **이전**에 `alembic upgrade head` 를 실행한다
(`scripts/deploy_migrate.sh`). 무중단 배포 중에는 구/신 레플리카가 동시에 동작하므로
마이그레이션은 **하위 호환(expand/contract)** 을 지켜야 한다.

expand/contract 2단계 규칙(1 릴리스 윈도우):

1. **Expand(릴리스 N)**: 추가만 한다. 새 컬럼/테이블 추가는 nullable 또는 default 포함.
   컬럼 삭제·rename·NOT NULL 강화·타입 축소를 **같은 릴리스에 넣지 않는다**.
2. **코드 이행**: 신버전 코드가 새 스키마를 사용하도록 배포(롤링). 구버전도 여전히 동작.
3. **Contract(릴리스 N+1)**: 모든 레플리카가 신버전이 된 다음 릴리스에서만
   구 컬럼 삭제/rename 등 파괴적 변경을 수행한다.

금지 예시(단일 릴리스에 포함 시 롤링 중 구버전 레플리카가 깨짐):

- 컬럼 `DROP` / `RENAME`
- `NOT NULL` 신규 강제(백필 없이)
- 타입 축소(예: `VARCHAR(255)` → `VARCHAR(50)`)

실행:

```bash
# 매니저 노드에서 배포 이미지로 일회성 실행(권장)
IMAGE_TAG=ghcr.io/antam2010/kmcbeauty-api:<sha> ./scripts/deploy_migrate.sh
# 또는 로컬 단일 노드
./scripts/deploy_migrate.sh --local
```

---

## 6. CI/CD (REQ-INFRA-006 ~ 010)

### CI (`.github/workflows/ci.yml`)

- 트리거: `pull_request`, `push`
- Python 3.13 + pip 캐시 → `ruff check` → `ruff format --check` → `pytest`(커버리지 리포트)
- 커버리지 게이트(`--cov-fail-under`)는 두지 않는다.
- Redis 서비스 컨테이너 없음(테스트가 전부 모킹).

### CD (`.github/workflows/cd.yml`)

- 트리거: `push` to `main`
- `build-and-push`: GHCR 로그인(GITHUB_TOKEN, `packages: write`) → 불변 SHA 태그 빌드·푸시
- `deploy`: `environment: production`(수동 승인 게이트 가능) → 매니저 노드 SSH →
  `deploy_migrate.sh` → `docker stack deploy`

### 필요한 GitHub 저장소 시크릿

| 시크릿 | 용도 |
|---|---|
| `SWARM_SSH_HOST` | 매니저 노드 호스트/IP |
| `SWARM_SSH_USER` | 배포 계정(최소 권한) |
| `SWARM_SSH_KEY` | 배포 계정 개인키 |
| `GITHUB_TOKEN` | GHCR 푸시(자동 제공, 별도 등록 불필요) |

사전 준비:

- 매니저 노드에서 GHCR pull 로그인: `echo <PAT> | docker login ghcr.io -u antam2010 --password-stdin`
- 매니저 노드에 저장소 체크아웃(`/opt/kmcbeauty` 등, CD 스크립트의 `DEPLOY_DIR`)
- (선택) GitHub `production` environment 에 필수 리뷰어 설정(수동 승인, REQ-INFRA-010)

---

## 7. 롤백 (REQ-INFRA-011)

### 자동 롤백

`update_config.failure_action: rollback` + `max_failure_ratio: 0` 에 의해,
새 레플리카가 헬스 게이트를 통과하지 못하면 Swarm 이 직전 정상 태스크로 자동 롤백한다.
`/health` 폴링에 지속적 다운타임이 발생하지 않는다.

### 수동 롤백

```bash
# 방법 A: 직전 스펙으로 서비스 롤백
docker service rollback kmcbeauty_kmcbeauty_api

# 방법 B: 직전 정상 SHA 태그로 재배포(권장, 명시적)
IMAGE_TAG=ghcr.io/antam2010/kmcbeauty-api:<이전-정상-sha> \
  docker stack deploy -c docker-stack.yml kmcbeauty
```

상태 확인:

```bash
docker service ps kmcbeauty_kmcbeauty_api          # 태스크 상태/이미지 다이제스트
docker service inspect kmcbeauty_kmcbeauty_api --format '{{.Spec.TaskTemplate.ContainerSpec.Image}}'
```

---

## 8. uv 도입 평가 (REQ-INFRA-015, Optional)

결론: **현 시점 미도입, 관찰 유지(revisit)**.

| 항목 | 평가 |
|---|---|
| 이점 | 설치/해상도 속도 대폭 향상, `uv.lock` 재현성, `uv pip` 호환 |
| 비용 | 완전 고정된 `requirements.txt` 트리를 `pyproject`/`uv.lock` 으로 이전하는 마이그레이션 부담, Dockerfile/CI 파이프라인 재작성 |
| 리스크 | 현재 핀 전략(전이 의존까지 수동 고정)이 안정적으로 동작 중 — 교체 시 회귀 위험 |

권고: 의존성 관리 현대화를 별도 SPEC 으로 분리해 진행한다. 도입 시
`pip install -r requirements.txt` → `uv pip sync` 로 1:1 치환부터 시작하고,
`pyproject.toml` 기반 잠금은 그 다음 단계로 미룬다. 이 SPEC 에서는 채택하지 않는다.
