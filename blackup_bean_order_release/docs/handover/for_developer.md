# 💻 개발자를 위한 유지보수 가이드 (Developer's Guide)

> **Antigravity Coffee Order System**의 유지보수 담당자님을 위한 기술 문서입니다.

---

## 1. 아키텍처 개요 (Architecture)

이 시스템은 **Human-In-The-Loop** 구조의 AI 에이전트 시스템입니다.

- **Frontend/DB**: Google Sheets (별도 서버 없음)
- **Backend/Logic**: Antigravity Agent (`.agent/instructions/order_manager.md`)
- **Data Source**: Chrome Browser Automation (읽기 전용)
- **Config**: `config/settings.yaml` (단일 진실 공급원)

## 2. 디렉토리 구조 (Structure)

```
.agent/
├── instructions/
│   └── order_manager.md       # [핵심] 에이전트 로직 100% (Prompt Engineering)
└── skills/
    └── order_manager.json     # 스킬 정의 (Slash Command 등)

blackup_bean_order/
├── config/
│   └── settings.yaml          # 매장 목록, 시트 URL, 원두 목록(JSON)
├── templates/
│   └── sheets_data/           # 시트 초기 셋업 데이터
├── examples/                  # 테스트용 가짜 데이터 (Golden Test)
└── docs/                      # 각종 문서들
```

## 3. 핵심 로직 설명 (Implementation Details)

`order_manager.md` 파일이 곧 소스 코드입니다.

### Step 1: 초기 설정
- `settings.yaml` 파싱 → 50여 줄의 Dictionary로 변환.
- **오류 처리**: 파일이 없거나 문법 오류 시 `.bak` 파일로 롤백.

### Step 2: 데이터 수집 (Sheets Automation)
- Browser Tool을 사용하여 `settings.yaml`의 URL들을 순회.
- `A2:M` 범위의 데이터를 읽어옴 (Header 제외).
- **필터링**: `주문일` == `오늘 날짜` (v1.5: `미수령` 데이터 별도 수집)

### Step 3: 데이터 처리 (Calc Logic)
- **Grouping**: (원두코드, 로스팅단계, 분쇄여부)를 Key로 합산.
- **Sub-total**: 각 Group별로 (매장코드: 수량) 리스트 생성.

### Step 4~5: 검증 및 출력 (Validation & Report)
- **18개 항목 교차 검증**: `매장코드` 오타, `배송희망일` 과거 여부 등.
- **리포트 생성**: `reports/YYYY-MM/` 폴더에 Markdown 파일 저장.

## 4. 확장 가이드 (Extensibility)

### Q. 새로운 검증 규칙 추가?
> `order_manager.md`의 **Step 5: 교차검증** 테이블에 행을 추가하세요.

### Q. 리포트 양식 변경?
> `order_manager.md`의 **Step 4: 리포트 양식** 섹션을 수정하세요.

### Q. 외부 API 연동? (예: Slack 알림 자동화)
> 현재는 Browser Tool만 사용합니다. Python 코드가 필요하다면 `scripts/` 폴더에 작성하고 `run_command` 도구를 에이전트에게 허용해야 합니다.

---

## 5. 문제 해결 (Troubleshooting)

- **에이전트가 말을 안 들음**: `order_manager.md`의 Prompt를 더 구체적으로 수정하세요. (Few-Shot 예시 추가 권장)
- **시트 데이터 파싱 불가**: `docs/sheets_template_guide.md`를 참고하여 시트 구조 복구 필요.
