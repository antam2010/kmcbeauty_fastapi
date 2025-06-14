# 📘 API Changelog

> API 기능 추가, 수정, 삭제 등 변경 이력을 날짜별로 정리합니다.
> 변경이 있을 때마다 아래 템플릿을 복사해 추가하세요.

---

## 🔄 2025-05-12

### 🛠 수정 (Changed)

- [o] `POST /auth/refresh`  
  - **수정 내용 1**: `X-Refresh-Token` 헤더를 통해 리프레시 토큰 전달을 지원하도록 수정  
  - **수정 내용 2**: 응답에 `refresh_token` 필드 추가  
  - **프론트 영향**: 있음 → 리프레시 토큰을 `X-Refresh-Token` 헤더에 담아 요청해주세요.

- [o] `POST /auth/login`  
  - **수정 내용**: 기존 `access_token` 외에 `refresh_token`도 응답에 포함되도록 수정  
  - **프론트 영향**: 있음 → 로그인 응답에서 `refresh_token`을 함께 받아 저장 또는 쿠키 처리해주세요.
---

## 🔄 2025-05-13

### 🛠 변경 사항 (Changed)

- **[모든 API]**
  - **수정 내용**: 모든 API endpoint의 마지막 `/`를 제거했습니다.  
    예시: `/phonebook/` → `/phonebook`
  - **프론트엔드 영향**: **있음**  
    - 프론트에서 사용하는 모든 API 요청 경로를 변경된 endpoint에 맞게 수정해주세요.  
    - 변경하지 않으면, **도메인이 다른 경우 `307 Temporary Redirect`가 발생**하며 브라우저에서 요청이 실패할 수 있습니다.
---

## 🔄 2025-05-14

### 🛠 변경 사항 (Changed)

### ✨ 추가 (Added)
- [o] `GET /phonebooks/groups`
  - 설명: 전화번호부에서 `group_name` 기준으로 그룹화된 리스트를 반환하는 API 추가
  - 파라미터: `with_items`
  - 파라미터 설명: `with_items=true`일 경우 각 그룹별 전화번호 목록도 함께 반환되어 문자 발송 등 기능에 활용 가능
  - 프론트 영향: 있음 → 문자 전송 등 그룹별 고객 리스트 활용 시 연동 필요

### 🛠 수정 (Changed)
- [o] `POST /treatment-menus`
  - 수정 내용: 이름에 중복 못하게 유니크 잡음, 실수 방지
  - 프론트 영향: 중복에러 처리 해줘야함
  - 설명: 시술 메뉴 명이 중복되면 안됨

---

## 🔄 2025-05-15

### 🛠 변경 사항 (Changed)

### 🛠 수정 (Changed)
- [o] `GET /treatment-menus`
  - 수정 내용: 검색 시 하위 테이블 까지 검색가능하도록 수정
  - 프론트 영향: 없음
  - 설명: treatment_menu 테이블 뿐만아니라 그 하위 메뉴의 `name` 까지 검색 가능하도록 개선
---


## 🔄 2025-05-20

### ✨ 추가 (Added)
- [o] `PUT /treatment-menus/{menu_id}/details/{detail_id}`
  - 설명: 시술 메뉴 상세 수정 API 추가
  - 파라미터: `menu_id`, `detail_id`
  - 프론트 영향: 있음 → 수정 기능 연동 필요

### ✨ 추가 (Added)
- [o] `DELETE /treatment-menus/{menu_id}/details/{detail_id}`
  - 설명: 시술 메뉴 상세 삭제 API 추가
  - 파라미터: `menu_id`, `detail_id`
  - 프론트 영향: 있음 → 삭제 기능 연동 필요

---

## 🔄 2025-05-22

### ✨ 추가 (Added)
- [o] `POST /shops/{shop_id}/invites`
  - 설명: 샵 초대 코드 생성 (한 번만 생성 가능)
  - 파라미터: `shop_id`
  - 프론트 영향: 있음 → 초대코드 생성 기능 필요

- [o] `GET /shops/{shop_id}/invites`
  - 설명: 샵 초대 코드 조회
  - 파라미터: `shop_id`
  - 프론트 영향: 있음 → 초대코드 조회 기능 필요

- [o] `DELETE /shops/{shop_id}/invites`
  - 설명: 샵 초대 코드 삭제
  - 파라미터: `shop_id`
  - 프론트 영향: 있음 → 초대코드 삭제 기능 필요
  

