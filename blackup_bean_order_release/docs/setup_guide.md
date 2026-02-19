# 🛠️ 설치 및 설정 가이드 (Setup Guide)

> **Antigravity Coffee Order System**을 사용하기 위한 초기 설정 안내서입니다.

---

## 1. 사전 요구사항 (Prerequisites)

이 시스템은 **Antigravity Agent** 환경에서 동작하며, Google Sheets를 데이터베이스로 활용합니다.

- **OS**: macOS (권장) 또는 Linux/Windows
- **Python**: 3.9 이상
- **Google Chrome**: 최신 버전 (브라우저 자동화를 위해 필요)
- **Google 계정**: Google Sheets 생성 및 접근용

---

## 2. 프로젝트 설정

### 2.1 저장소 클론 (Clone Repository)

```bash
git clone https://github.com/your-username/antigravity_test.git
cd antigravity_test/blackup_bean_order
```

### 2.2 설정 파일 준비

기본 설정 파일을 복사하여 실제 환경에 맞게 수정합니다.

```bash
cp config/settings_example.yaml config/settings.yaml
```

`config/settings.yaml` 파일을 열어 다음 내용을 수정하세요(또는 에이전트에게 요청하세요):
- **roastery**: 로스터리 이름 및 코드
- **stores**: 각 매장의 정보 (이름, 코드, **Google Sheets URL**)
- **beans**: 취급 원두 목록 및 단가

---

## 3. Google Sheets 준비 (중요!)

이 시스템의 핵심 데이터 소스인 Google Sheets를 준비해야 합니다.

### 3.1 마스터 코드표 시트 생성
1. Google Sheets를 새로 생성합니다. (제목: `블랙업_마스터코드표`)
2. 하단 탭 이름을 각각 `매장코드`, `원두코드`, `옵션`으로 변경합니다.
3. `templates/sheets_data/` 폴더 내의 `.tsv` 파일 내용을 각 탭에 복사해 붙여넣습니다.

### 3.2 매장별 주문 시트 생성
각 매장마다 별도의 시트를 생성해야 합니다. (예: `블랙업_주문_서면본점`)

1. 새 시트를 생성합니다.
2. **1행(헤더)**을 다음과 같이 설정합니다. (`templates/sheets_data/주문시트_헤더.tsv` 참조)
   - A: 주문일
   - B: 매장코드
   - C: 매장명
   - D: 원두코드
   - E: 원두명
   - F: 수량(kg)
   - G: 배송희망일
   - H: 로스팅단계
   - I: 분쇄여부
   - J: 긴급여부
   - K: 비고
   - L: (공란/예비)
3. **[v1.5 확장]** 배송 관리를 위해 다음 컬럼을 추가하세요:
   - **M: 운송장번호** (텍스트)
   - **N: 수령확인** (체크박스)

### 3.3 공유 설정
에이전트가 접근할 수 있도록 권한을 설정합니다.
- 우측 상단 `Share` 버튼 클릭
- `General access`를 **Anyone with the link** → **Editor** (또는 Viewer)로 변경
- 링크를 복사하여 `settings.yaml`의 해당 매장 `sheet_url`에 붙여넣습니다.

> **보안 팁**: 보안이 중요한 경우, 에이전트 전용 Google 계정을 생성하고 해당 계정만 `Editor`로 초대하는 것을 권장합니다.

---

## 4. 에이전트 실행

터미널에서 에이전트를 실행하고 다음 명령어로 시작하세요.

- **일일 리포트 생성**:
  ```text
  "오늘 주문 정리해줘"
  ```
- **특정 날짜 리포트**:
  ```text
  "2/15 주문 리포트 만들어줘"
  ```
- **설정 변경**:
  ```text
  "해운대점 시트 URL 변경해줘"
  ```

---

## 5. 문제 해결 (Troubleshooting)

- **브라우저가 열리지 않아요**: Chrome이 설치되어 있는지 확인하세요.
- **시트 데이터를 못 읽어요**: `settings.yaml`의 URL이 정확한지, 시트의 공유 권한이 올바른지 확인하세요.
- **주문이 누락돼요**: 시트의 `주문일` 형식이 `YYYY-MM-DD`인지 확인하세요.
