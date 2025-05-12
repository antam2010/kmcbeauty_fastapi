# 📘 API Changelog

> API 기능 추가, 수정, 삭제 등 변경 이력을 날짜별로 정리합니다.
> 변경이 있을 때마다 아래 템플릿을 복사해 추가하세요.

---

## 🔄 2025-05-12

### 🛠 수정 (Changed)

- [x] `POST /auth/refresh`  
  - **수정 내용 1**: `X-Refresh-Token` 헤더를 통해 리프레시 토큰 전달을 지원하도록 수정  
  - **수정 내용 2**: 응답에 `refresh_token` 필드 추가  
  - **프론트 영향**: 있음 → 리프레시 토큰을 `X-Refresh-Token` 헤더에 담아 요청해주세요.

- [x] `POST /auth/login`  
  - **수정 내용**: 기존 `access_token` 외에 `refresh_token`도 응답에 포함되도록 수정  
  - **프론트 영향**: 있음 → 로그인 응답에서 `refresh_token`을 함께 받아 저장 또는 쿠키 처리해주세요.
---

## 🧾 예시 복붙용 템플릿 (아래 내용만 복사해서 위에 붙여 사용)

````markdown
## 🔄 2025-05-09

### ✨ 추가 (Added)
- [x] `GET /user/search`
  - 설명: 사용자 검색 API 추가
  - 파라미터: `keyword`, `page`, `size`
  - 프론트 영향: 있음 → 리스트 화면 연동 필요

### 🛠 수정 (Changed)
- [x] `POST /auth/login`
  - 수정 내용: 응답에 `user_type` 필드 추가됨
  - 프론트 영향: 있음 → 로그인 후 홈 리디렉션 분기 처리 필요

### ❌ 삭제 예정 (Deprecated)
- [x] `GET /user/check`
  - 이유: 중복 API 존재 → `/user/exists`로 통합됨
  - 제거 예정일: 2025-05-31
