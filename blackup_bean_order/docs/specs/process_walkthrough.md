# 📘 Antigravity로 서비스 스펙 만들기 — 전체 과정 안내서

> **대상 독자**: 비개발자 (기획자, 로스터리 운영자, 사업 담당자)
> **목적**: Antigravity AI 도구를 설치한 이후, "원두 주문 관리 시스템"의 설계 문서가 어떤 과정을 거쳐 완성되었는지를 설명합니다.

---

## 전체 과정 한눈에 보기

```mermaid
flowchart TD
    subgraph Phase1["🟢 1단계: 아이디어 → 초기 설계"]
        A["💬 대화 시작<br>'각 매장 주문을 자동으로<br>정리하는 기능 만들어줘'"] --> B["🤔 설계 질문 5가지<br>데이터 형식, 시트 구성,<br>리포트 종류 등"]
        B --> C["📝 Implementation Plan v1<br>기본 설계 문서 작성"]
        C --> D["↔️ 피드백 반복<br>v1 → v2 → v3"]
    end

    subgraph Phase2["🔵 2단계: 다중 관점 검증"]
        E["👥 10명 가상 사용자 토론<br>로스터 5명 + 매장 직원 5명"] --> F["📋 Multi-Persona Debate<br>10라운드 비판 & 개선"]
    end

    subgraph Phase3["🟡 3단계: 전문가 토론"]
        G["⚔️ Tech Lead vs Product Lead<br>기술 vs 비즈니스 관점<br>15라운드 비판"]
        H["🔺 3-Agent Debate<br>모델링 + 기획 + 시스템<br>10라운드 비판"]
    end

    subgraph Phase4["🟣 4단계: 최종 스펙"]
        I["📄 Implementation Plan v5<br>모든 토론 결과 반영<br>최종 설계 문서"]
    end

    D --> E
    F --> G
    G --> H
    H --> I

    style Phase1 fill:#e8f5e9,stroke:#4caf50
    style Phase2 fill:#e3f2fd,stroke:#2196f3
    style Phase3 fill:#fff8e1,stroke:#ffc107
    style Phase4 fill:#f3e5f5,stroke:#9c27b0
```

---

## 🟢 1단계: 아이디어에서 초기 설계까지

### 무엇을 했나?

| 순서 | 한 일 | 결과물 |
|------|-------|--------|
| 1 | "각 매장에서 들어오는 원두 주문을 자동으로 정리하고 싶어" 라고 Antigravity에 요청 | 대화 시작 |
| 2 | Antigravity가 5가지 핵심 질문을 던짐 | 데이터 포맷, 시트 구성 등 결정 |
| 3 | 대화를 통해 핵심 결정 7가지 확정 | Implementation Plan v1 작성 |
| 4 | 피드백을 주고받으며 3차례 수정 | v1 → v2 → v3 |

### 핵심 결정 사항

```mermaid
mindmap
  root((원두 주문 관리<br>시스템))
    데이터
      Google Sheets 사용
      매장별 별도 시트
      13개 컬럼 정의
    처리 방식
      스크립트 0개
      AI 에이전트가 직접 처리
      브라우저로 데이터 접근
    결과물
      일일 주문 요약
      원두별 총 수량
      배송 스케줄
```

### 쉽게 비유하면

> 🍳 **요리에 비유**: "오늘 저녁 뭐 먹지?" (아이디어) → "냉장고에 뭐 있지?" (데이터 점검) → "레시피 초안 작성" (v1) → "가족 입맛 반영해서 수정" (v2, v3)

---

## 🔵 2단계: 가상 사용자 10명과 함께 검증

### 무엇을 했나?

초기 설계(v3)를 **실제 사용할 사람들의 관점**에서 검증했습니다. Antigravity에 "로스터 5명, 매장 직원 5명의 역할로 이 설계를 비판해줘"라고 요청했습니다.

```mermaid
flowchart LR
    subgraph Roasters["☕ 로스터 관점 (5라운드)"]
        R1["재고 관리 문제"]
        R2["로스팅 리드타임"]
        R3["트렌드 분석 필요"]
        R4["주문 마감 기준"]
        R5["피드백 체계"]
    end

    subgraph Stores["🏪 매장 관점 (5라운드)"]
        S1["알림 부재 문제"]
        S2["다국어 지원"]
        S3["주문 간소화"]
        S4["비용 투명성"]
        S5["데이터 검증"]
    end

    Roasters --> V["✅ v3에 반영된 개선사항"]
    Stores --> V
```

### 이 단계에서 바뀐 것들

| # | 발견된 문제 | 개선 내용 |
|---|-----------|----------|
| 1 | 로스팅 프로파일이 매장마다 다름 | 로스팅단계별 별도 집계 추가 |
| 2 | 영문 원두명이 없어 소통 어려움 | 원두명 한/영 병기 |
| 3 | 소량 주문 합배송 기준 없음 | 배송 구역(zone) 개념 도입 |
| 4 | 원가 정보 접근 우려 | `enable_cost_report` 토글 추가 |
| 5 | 입력 형식 오류 감지 불가 | 교차검증 11개 항목 추가 |

### 관련 문서
📄 [multi_persona_debate.md](file:///Users/sangwook/Documents/workspace/repo/antigravity_test/blackup_bean_order/docs/debates/multi_persona_debate.md)

---

## 🟡 3단계: 전문가 에이전트 토론 (2회)

### 3-A. Tech Lead vs Product Lead (15라운드)

v3 설계를 **기술 전문가 vs 비즈니스 전문가** 두 관점에서 격렬하게 비판시켰습니다.

```mermaid
flowchart LR
    TL["⚙️ Tech Lead<br>시스템 안정성<br>보안/확장성"] <--->|"15라운드<br>공방"| PL["📋 Product Lead<br>사용자 가치<br>비즈니스 실현성"]
    TL --> R["결과: v4"]
    PL --> R
```

#### 주요 공방과 결과

| 주제 | Tech Lead 주장 | Product Lead 반론 | 결론 |
|------|---------------|------------------|------|
| 브라우저 접근 위험 | "장애 시 복구 불가" | "사장님이 API 키 관리?" | 실패 가이드 추가, v2에서 API 검토 |
| 에이전트가 자기 검증 | "학생이 자기 시험 채점" | "0%에서 80%로 개선" | 골든 테스트 셋 3종 추가 |
| settings.yaml 비대 | "설정+데이터 혼재" | "파일 1개가 인지 부담 ↓" | 유지하되 max_order_kg 추가 |
| 에러 메시지 부실 | "무슨 오류인지 모름" | "사용자 눈높이 맞춤" | 3단계 경고 (❌/⚠️/ℹ️) 도입 |
| 개인정보 노출 | "리포트에 연락처?" | "관리자 신뢰 중요" | 리포트에 개인정보 미포함 |

#### 관련 문서
📄 [tech_vs_product_debate.md](file:///Users/sangwook/Documents/workspace/repo/antigravity_test/blackup_bean_order/docs/debates/tech_vs_product_debate.md)

---

### 3-B. 3자 토론: 모델링 × 기획 × 시스템 (10라운드)

v4 설계를 **AI 전문가까지 포함한 3자 토론**으로 추가 검증했습니다.

```mermaid
flowchart TD
    ML["🤖 Modeling Lead<br>AI/ML 전문가<br>'이것이 AI가 해야 할 일인가?'"]
    PL2["📋 Product Lead<br>기획 전문가<br>'사용자에게 가치가 있는가?'"]
    TL2["⚙️ Tech Lead<br>시스템 전문가<br>'안전하고 안정적인가?'"]

    ML <-->|토론| PL2
    PL2 <-->|토론| TL2
    TL2 <-->|토론| ML

    ML --> D1["코드 실행 분리<br>숫자 계산은 AI 말고<br>코드가 직접 수행"]
    ML --> D2["가드레일 추가<br>AI가 확신 없으면<br>추측 금지"]
    TL2 --> D3["사전 헬스체크<br>실행 전에 먼저<br>설정·접근 점검"]
    TL2 --> D4["보안 가이드<br>전용 계정 사용<br>읽기 전용 원칙"]
    PL2 --> D5["설정 변경 지원<br>AI를 통해 설정 파일<br>편하게 변경"]
```

#### 가장 중요한 발견

> 🔑 **Modeling Lead의 핵심 지적**: "숫자 합산은 AI가 할 일이 아니다. AI는 계산을 틀릴 수 있다. 숫자 계산은 코드가 하고, AI는 데이터 해석과 리포트 작성에만 집중해야 한다."
>
> → **결론**: 숫자 집계는 코드로, 해석·문장은 AI로 — **역할 분리 원칙** 확정

#### 관련 문서
📄 [three_agent_debate.md](file:///Users/sangwook/Documents/workspace/repo/antigravity_test/blackup_bean_order/docs/debates/three_agent_debate.md)

---

## 🟣 4단계: 최종 스펙 문서 완성

모든 토론 결과를 반영하여 **Implementation Plan v5**가 완성되었습니다.

### 버전별 발전 과정

```mermaid
timeline
    title Implementation Plan 버전 변화
    v1 : 첫 설계
       : 기본 구조 + 7개 확정 사항
    v2 : 1차 수정
       : 데이터 컬럼 확정
       : 리포트 형식 결정
    v3 : 다중 페르소나 반영
       : 로스팅 프로파일 + 배송 구역
       : 교차검증 11개 항목
       : 영문명 병기
    v4 : Tech vs Product 반영
       : 경고 3단계 + 개인정보 보호
       : 엣지 케이스 + 테스트 전략
       : 교차검증 14개 항목
    v5 : 3자 토론 반영 (최종)
       : 코드 실행 분리 원칙
       : 사전 헬스체크 + 가드레일
       : 보안 가이드
       : 교차검증 15개 항목
```

### 최종 문서 구성

```
docs/
├── 📁 specs/          ← 설계 스펙 문서
│   ├── implementation_plan.md   ← 최종 스펙 (v5)
│   └── process_walkthrough.md   ← 이 문서
├── 📁 reviews/        ← 설계 리뷰
│   └── design_review.md         ← 로스터 관점 리뷰
└── 📁 debates/        ← 토론 기록
    ├── multi_persona_debate.md   ← 10인 가상 사용자 토론
    ├── tech_vs_product_debate.md ← 기술 vs 비즈니스 토론
    └── three_agent_debate.md     ← 3자 전문가 토론
```

### 관련 문서
📄 [implementation_plan.md (v5)](file:///Users/sangwook/Documents/workspace/repo/antigravity_test/blackup_bean_order/docs/specs/implementation_plan.md)

---

## 숫자로 보는 전체 과정

| 지표 | 수치 |
|------|------|
| 총 대화 횟수 | 4회 |
| 스펙 버전 업 횟수 | 5회 (v1 → v5) |
| 토론 총 라운드 수 | 40라운드 |
| 참여 가상 에이전트 수 | 13명 (로스터 5 + 매장 5 + 전문가 3) |
| 교차검증 항목 | 0개 → 15개 |
| 확정 사항 | 7개 → 12개 |
| 로드맵 항목 | 6개 → 22개 (v1.5: 8 + v2: 14) |

---

## 이 과정이 왜 좋은가?

```mermaid
flowchart TD
    OLD["기존 방식<br>🧑 혼자 기획서 작성<br>→ 개발 시작<br>→ 문제 발견<br>→ 처음부터 다시"] 
    
    NEW["Antigravity 방식<br>💬 대화로 초안 작성<br>→ 가상 사용자 검증<br>→ 전문가 토론<br>→ 검증된 스펙으로 개발"]

    OLD -->|"시간 ⬆️ 비용 ⬆️<br>리스크 ⬆️"| BAD["😰 개발 중 재설계"]
    NEW -->|"시간 ⬇️ 비용 ⬇️<br>리스크 ⬇️"| GOOD["😊 검증된 설계로 개발 시작"]

    style OLD fill:#ffebee,stroke:#f44336
    style NEW fill:#e8f5e9,stroke:#4caf50
    style BAD fill:#ffcdd2,stroke:#ef5350
    style GOOD fill:#c8e6c9,stroke:#66bb6a
```

### 핵심 이점 3가지

1. **개발 전에 문제를 발견**: 40라운드의 가상 토론으로 실제 개발 전에 35개 이상의 잠재 문제를 발견하고 해결했습니다.

2. **다양한 시각 반영**: 로스터, 매장 직원, 시스템 전문가, AI 전문가, 기획자 — 한 사람이 혼자 생각하면 놓치는 관점을 13명의 가상 전문가가 보완했습니다.

3. **결정의 근거 추적 가능**: 모든 설계 결정에 "왜 이렇게 결정했는가"의 기록이 남아 있어, 나중에 변경할 때 맥락을 잃지 않습니다.

---

## 다음 단계: 이 스펙으로 무엇을 하나?

| 순서 | 할 일 | 설명 |
|------|-------|------|
| 1 | **SKILL.md 작성** | v5 스펙을 바탕으로 에이전트 실행 가이드 작성 |
| 2 | **settings.yaml 작성** | 실제 매장 정보와 원두 목록 입력 |
| 3 | **테스트** | 골든 테스트 셋 3종으로 에이전트 동작 검증 |
| 4 | **UAT (사용자 수용 테스트)** | 실제 데이터로 리포트 생성 → 관리자 확인 |
| 5 | **운영 시작** | 매일 "오늘 주문 정리해줘" 한 마디로 실행 |
