---
id: SPEC-INFRA-001
version: 1.0.0
status: approved
created: 2026-07-06
updated: 2026-07-06
author: antam2010
priority: HIGH
issue_number: null
---

# SPEC-INFRA-001: 배포 하드닝 · CI/CD 파이프라인 · 개발 환경 현대화

## HISTORY

- 2026-07-06 (v0.1.0): 최초 작성. 단일 서버 → 2노드 확장을 전제로 한 무중단 배포 하드닝, GitHub Actions 기반 CI/CD, 로컬 개발/테스트 환경 현대화를 5개 마일스톤으로 정리. Docker Swarm 유지(무중단 배포 하드 요구), Kubernetes/plain Compose는 명시적으로 범위 제외.

---

## 배경 (Why)

현재 배포는 Docker Swarm 단일 스택(`docker-stack.yml`)으로 이루어지며, `start-first` 롤링 업데이트와 실패 시 자동 롤백이 이미 구성되어 있다. 그러나 무중단 배포를 실제로 보장하지 못하게 만드는 결함과 자동화 공백이 존재한다.

- **CI/CD 부재**: `.github/`에는 `PULL_REQUEST_TEMPLATE.md`만 존재하며 CI 워크플로우가 전혀 없다. 품질 게이트(ruff/pytest)가 사람 손에만 의존한다.
- **환경 변수 결함**: `.env`의 `REDIS_URL=redis://localhost:6379/0`은 Swarm 오버레이 안에서 동작하지 않는다. 로컬 개발용 `.env`와 배포용 설정이 단일 파일로 공유되는 것이 근본 원인이다.
- **시크릿 마운트 누락**: `.env`의 `FIREBASE_SERVICE_ACCOUNT_KEY_PATH`가 설정되어 있으나 `docker-stack.yml`에 시크릿/볼륨 마운트가 없어 Swarm에서 FCM이 동작하지 않는다.
- **가변 태그 배포**: 이미지가 `kmcbeauty-api:latest`로만 빌드되어 `docker service update`가 동일 태그의 다른 다이제스트를 안정적으로 롤아웃하지 못하는 함정(latest-tag digest pitfall)이 있다.
- **런타임 불일치**: 런타임은 Python 3.13이지만 ruff `target-version = "py312"`로 설정되어 있다.

이 SPEC은 위 결함을 수정하고, 1노드에서 2노드로 확장하더라도 무중단 배포가 유지되도록 로드맵을 정의한다.

## 확정된 기술 결정 (재검토 대상 아님)

- 배포 오케스트레이션: **Docker Swarm 유지**. 기존 `docker-stack.yml`(start-first 롤링 업데이트 + 실패 시 자동 롤백)을 기반으로 한다.
- Kubernetes 도입은 1~2노드 규모에 과함 → 제외. plain Compose는 무중단 배포 불가 → 제외.
- CI/CD 플랫폼: **GitHub Actions**.
- 이미지 레지스트리: **GHCR** (`ghcr.io/<owner>/kmcbeauty-api:<sha>`).

## 환경 및 전제 (Environment & Assumptions)

- Swarm 매니저 노드에 SSH 접근이 가능하며, GitHub Actions에서 사용할 배포용 SSH 키/시크릿을 저장소 시크릿으로 주입할 수 있다.
- 외부 NGINX 리버스 프록시가 `shared_network_prod` 오버레이 네트워크에 연결되어 각 서비스 DNS 이름(`kmcbeauty_api:3100`)으로 라우팅한다.
- MySQL은 운영 환경에서 컨테이너 외부(외부 관리형/호스트)에 존재하며 이 SPEC에서 컨테이너화하지 않는다.
- 애플리케이션 `/health` 엔드포인트(`app/main.py`)가 존재하며 컨테이너 `HEALTHCHECK`가 이를 사용한다.
- 현재 Alembic 마이그레이션은 7개이며 MySQL(PyMySQL) 대상이다.

---

## 요구사항 (Requirements, EARS)

EARS 키워드(WHEN / WHILE / WHERE / IF / THEN / SHALL)는 원문 형식을 유지한다.

### M1 — Swarm 하드닝 (Priority: High)

**REQ-INFRA-001 (환경별 env 분리 — 결함 1 수정)**
The system **shall** maintain separate environment-variable sources for local development and Swarm deployment (로컬: `.env`, Swarm: `.env.prod` 또는 Docker configs/secrets).
**WHEN** the API/worker container runs inside the Swarm overlay, the system **shall** resolve Redis via the overlay service DNS name (`redis://redis:6379/0`), never `localhost`.
부수 작업: `.env.prod`를 실제로 도입하여 `readme.rst`가 참조하는 존재하지 않는 파일을 정합화한다.

**REQ-INFRA-002 (Firebase 시크릿 마운트 — 결함 2 수정)**
**WHEN** the API/worker container starts in Swarm, the system **shall** mount the Firebase service-account credential via a Docker secret so that `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` resolves to an existing, readable file inside the container.

**REQ-INFRA-003 (불변 이미지 태그)**
The system **shall** tag deployment images with the immutable git commit SHA (`kmcbeauty-api:<sha>`) instead of the mutable `:latest` tag.
**WHEN** `docker stack deploy` / `docker service update` runs with a new SHA tag, the system **shall** roll every replica to the new image (latest-tag digest 함정 회피).

**REQ-INFRA-004 (HEALTHCHECK 기반 롤링 게이팅)**
**WHILE** a rolling update is in progress, the system **shall** gate promotion of each new replica on its container `HEALTHCHECK` passing before the next replica is updated, preserving `order: start-first`.

**REQ-INFRA-005 (배포 시 Alembic 마이그레이션 단계)**
**WHEN** a deployment includes schema changes, the system **shall** execute Alembic migrations before the stack update.
The system **shall** keep migrations backward-compatible for one release window so that old and new replicas can run concurrently during rollout (무중단 전제).

### M2 — CI (GitHub Actions) (Priority: High)

**REQ-INFRA-006 (CI 파이프라인)**
**WHEN** a pull request is opened or a commit is pushed, the GitHub Actions CI workflow **shall** run `ruff check`, `ruff format --check`, and `pytest` on Python 3.13 with pip cache enabled.
**WHERE** the test suite requires Redis, the CI workflow **shall** provide a Redis service container.

**REQ-INFRA-007 (ruff target-version 정합화)**
The system **shall** set ruff `target-version = "py313"` in `pyproject.toml` to match the Python 3.13 runtime.

### M3 — CD (GitHub Actions) (Priority: High)

**REQ-INFRA-008 (이미지 빌드 및 GHCR 푸시)**
**WHEN** a change is merged to `main`, the GitHub Actions CD workflow **shall** build the image and push it to GHCR tagged with the commit SHA (`ghcr.io/<owner>/kmcbeauty-api:<sha>`).

**REQ-INFRA-009 (매니저 노드 배포)**
**WHEN** the SHA-tagged image is published, the CD workflow **shall** deploy to the Swarm manager node over SSH by running `docker stack deploy -c docker-stack.yml` with the new image tag injected via environment substitution.

**REQ-INFRA-010 (수동 승인 — Optional)**
**WHERE** a protected GitHub environment is configured, the CD workflow **shall** require manual approval before deploying to production.

**REQ-INFRA-011 (롤백 절차)**
**IF** a deployment fails its health gate, **THEN** the system **shall** automatically roll back (Swarm `failure_action: rollback`).
The system **shall** document a manual rollback procedure (`docker service rollback` 또는 직전 SHA 태그 재배포).

### M4 — 개발 환경 현대화 (Priority: Medium)

**REQ-INFRA-012 (로컬 개발용 compose)**
The system **shall** provide a local development compose file at `docker/compose/compose.dev.yml` that starts Redis and, optionally, MySQL for local runs.

**REQ-INFRA-013 (pre-commit 훅)**
**WHEN** a developer creates a commit, pre-commit hooks **shall** run ruff (lint + format) locally before the commit is accepted.

**REQ-INFRA-014 (개발 워크플로우 문서화)**
The system **shall** document the local development and test workflow in the README.

**REQ-INFRA-015 (uv 도입 평가 — Optional, low priority)**
**WHERE** dependency-management modernization is pursued, the system **shall** evaluate `uv` as a replacement for pip and record the decision.

### M5 — 2노드 확장 준비 (문서 수준) (Priority: Low)

**REQ-INFRA-016 (노드 조인 절차)**
The system **shall** document the Swarm worker-node join procedure for expanding from one node to two nodes.

**REQ-INFRA-017 (배치 제약)**
The system **shall** document placement constraints so that single-instance services (`celery_beat`, `redis`) are pinned to a specific node — or `redis` is externalized to a managed instance — preventing duplicate scheduled-task dispatch and data split.

**REQ-INFRA-018 (NGINX 업스트림 고려사항)**
The system **shall** document NGINX upstream considerations for routing across two nodes over the `shared_network_prod` overlay network.

---

## Exclusions (What NOT to Build)

- **Kubernetes 마이그레이션**: 1~2노드 규모에 과도한 복잡성. Swarm 유지.
- **관리형 클라우드 컨테이너 서비스**(ECS/Cloud Run/EKS 등): 범위 밖.
- **운영 환경 DB 컨테이너화**: MySQL은 컨테이너 외부(외부 관리형)로 유지. 로컬 개발용 MySQL 컨테이너는 M4에서 선택 사항으로만 허용.
- **Sentry를 넘어서는 APM/관측성 스택**(Prometheus/Grafana/OpenTelemetry 신규 도입 등): 기존 Sentry로 충분하며 이 SPEC 범위 밖.
- **애플리케이션 기능/도메인 로직 변경**: 이 SPEC은 인프라·파이프라인·개발 환경에 한정한다. 코드 리팩터링은 결함 수정에 필요한 최소 범위(REDIS_URL 해석, 시크릿 경로 로딩)로 제한한다.
- **투기적 기능**: 카나리/블루-그린 배포, 오토스케일링, 멀티리전 등은 현 요구에 없으므로 도입하지 않는다.

---

## 추적성 (Traceability)

| 요구사항 | 마일스톤 | 대상 아티팩트(예상) |
|---|---|---|
| REQ-INFRA-001, 002 | M1 | `.env.prod`, `docker-stack.yml`, `readme.rst` |
| REQ-INFRA-003, 004, 005 | M1 | `docker-stack.yml`, 배포 스크립트, 마이그레이션 실행 단계 |
| REQ-INFRA-006, 007 | M2 | `.github/workflows/ci.yml`, `pyproject.toml` |
| REQ-INFRA-008~011 | M3 | `.github/workflows/cd.yml`, 롤백 문서 |
| REQ-INFRA-012~015 | M4 | `docker/compose/compose.dev.yml`, `.pre-commit-config.yaml`, README |
| REQ-INFRA-016~018 | M5 | 배포/운영 문서 |
