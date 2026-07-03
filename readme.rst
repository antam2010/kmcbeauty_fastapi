======================================
KMCBeauty FastAPI 프로젝트 실행 가이드
======================================

1. 의존성 설치
================

가상환경을 사용하는 경우::

    python3 -m venv venv
    source venv/bin/activate

필수 패키지 설치::

    pip install -r requirements.txt

가상환경 종료::

    deactivate


2. 개발 서버 / 배포
===========================

로컬 개발 서버 실행 (uvicorn, localhost:3100)::

    ./scripts/start_local.sh

컨테이너 배포는 docker-compose 대신 단일 Swarm 스택(docker-stack.yml)을 사용합니다.
스테이지/운영 배포::

    ./scripts/start_stage.sh
    # 또는 수동:
    docker build -t kmcbeauty-api:latest .
    docker stack deploy -c docker-stack.yml kmcbeauty


3. Alembic 마이그레이션
==========================

마이그레이션 파일 생성::

    alembic revision --autogenerate -m "update user model: rename password, add age"

DB에 마이그레이션 반영::

    alembic upgrade head

DB에 마이그레이션 롤백::

    alembic downgrade -1

4. FastAPI API 문서 접속
==========================

브라우저에서 아래 주소로 접속:

- Swagger UI: http://localhost:3100/docs
- ReDoc: http://localhost:3100/redoc

(로컬 uvicorn 기준. Swarm 배포 시 호스트 포트 미공개 — 외부 NGINX가 kmcbeauty_api:3100 라우팅)


5. 의존성 목록 저장 (선택)
=============================

패키지 설치 이후 현재 환경의 의존성을 저장::

    pip freeze > requirements.txt


6. 디렉토리 구조 예시
========================

::

    app/
    ├── main.py
    ├── database.py
    ├── model/
    │   ├── base.py
    │   ├── user.py
    │   └── phonebook.py
    ├── schema/
    ├── crud/
    alembic/
    ├── versions/
    docker-stack.yml
    Dockerfile
    scripts/
    ├── start_local.sh
    ├── start_stage.sh
    └── stop.sh

7. -isort 및 black 적용
========================
코드 스타일을 통일하기 위해 ``isort``와 ``black``을 사용합니다.

    isort . && black .

추가 TODO
=============

- 테스트 코드 작성
- seed 데이터 추가 방법 문서화
- 운영 배포용 ``.env.prod``, ``start_swarm.sh`` 설명 추가
- ``Makefile``로 명령어 자동화 정리
- 테스트