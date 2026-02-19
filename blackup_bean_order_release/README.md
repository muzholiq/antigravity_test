# ☕ 블랙업 커피 로스터스 — 원두 주문 관리 자동화 시스템

> **Antigravity AI 에이전트 기반 원두 주문 정리 시스템**
>
> 로스터가 Antigravity에 "오늘 주문 정리해줘" 한 마디로 각 매장의 Google Sheets 주문을 자동 집계·리포트합니다.

[![설계 버전](https://img.shields.io/badge/버전-v7%20(구현완료)-brightgreen)]()
[![문서량](https://img.shields.io/badge/문서-3,500+%20줄-blue)]()
[![토론 라운드](https://img.shields.io/badge/토론-60+%20라운드-orange)]()
[![교차검증](https://img.shields.io/badge/교차검증-17개%20항목-purple)]()

---

## 📖 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 특징](#-주요-특징)
- [동작 방식](#-동작-방식)
- [프로젝트 구조](#-프로젝트-구조)
- [매장 목록](#-매장-목록)
- [설계 진화 과정](#-설계-진화-과정)
- [최종 확정 사항](#-최종-확정-사항)
- [교차검증 체계](#-교차검증-체계)
- [테스트 전략](#-테스트-전략)
- [로드맵](#-로드맵)
- [설치 및 실행](#-설치-및-실행)
- [관련 문서](#-관련-문서)

---

## 🎯 프로젝트 개요

### 문제 정의

블랙업 커피 로스터스는 부산·경남·울산 10개 매장에서 들어오는 원두 주문을 수작업으로 정리하고 있습니다. 각 매장이 별도 Google Sheets에 주문을 입력하면, 로스터가 이를 일일이 확인하고 집계하는 데 많은 시간이 소요됩니다.

### 솔루션

**로스터 1인이 Antigravity를 직접 사용** (시나리오 A)하여:

- 각 매장의 Google Sheets를 순회하여 주문 데이터 수집
- 원두별, 매장별, 날짜별 집계
- 일일 리포트 자동 생성 (요약 + 배송 스케줄)
- 15개 항목 교차검증으로 데이터 정확성 보장

### 핵심 가치

- ⏱️ **시간 절약**: 30분 수작업 → 1분 자동화
- 🎯 **정확성**: AI + 코드 실행으로 집계 오류 제로화
- 🔒 **보안**: 읽기 전용 원칙, 개인정보 보호
- 🚀 **접근성**: 코드 작성 불필요, "오늘 주문 정리해줘" 한 마디로 실행

---

## ✨ 주요 특징

### 1. 하이브리드 자동화 (Hybrid Architecture)

- **Agent + Script**: 복잡한 계산과 검증은 Python 스크립트(`src/core`)로, 자연어 명령 해석은 Agent가 수행
- **정확성 보장**: 기존 LLM 단독 처리의 불확실성을 제거하고, 엄격한 룰(`validator.py`) 적용

### 2. 하이브리드 AI 접근

- **숫자 계산**: 코드 실행으로 100% 정확성 보장
- **데이터 해석**: LLM으로 유연한 비정형 데이터 처리
- **역할 분리**: Hallucination 리스크 최소화

### 3. 대화형 설정 관리

- **파일 편집 불필요**: 모든 설정 변경은 에이전트에게 말로 요청
- 예: "에티오피아 하라 추가해줘", "재고 20kg 들어왔어"
- 변경 전 미리보기(Dry-run) + 자동 백업

### 4. 철저한 검증

- **15개 항목** 자동 교차검증
- **3단계 경고 체계**: ❌ CRITICAL / ⚠️ WARNING / ℹ️ INFO
- 각 경고에 **권장 조치(Suggested Action)** 포함

### 5. 보안 중심 설계

- 에이전트는 **읽기 전용** — 원본 Sheets 절대 수정 불가
- 개인정보(주문자, 연락처) 리포트에 미포함
- 전용 Google 계정 사용 권장

---

## ⚙️ 동작 방식

```
사용자: "오늘 주문 정리해줘"
     ↓
Antigravity (메인 에이전트)
     ↓ order_manager.md를 "플레이북"으로 참조
     ↓
[Step 0] settings.yaml 읽기 + 사전 헬스체크
[Step 1] 브라우저 도구로 Google Sheets 접속 (매장별 순회)
[Step 2] 데이터 추출 + 정제
[Step 3] 코드 실행으로 집계 계산 (숫자는 코드, 해석은 LLM)
[Step 4] 리포트 생성 + 15개 항목 교차검증
[Step 5] 파일 저장 + 경로 안내
```

> **핵심**: `order_manager.md`는 별도 프로그램이 아니라, Antigravity가 따르는 **작업 매뉴얼(플레이북)**입니다.
> 사용자가 "주문 정리해줘"라고 하면 Antigravity가 이 매뉴얼을 읽고 브라우저 도구·코드 실행 도구를 사용하여 직접 처리합니다.

---

## 📂 프로젝트 구조

```
.agent/
├── instructions/
│   └── order_manager.md       # 에이전트 실행 가이드 (플레이북)
└── skills/
    └── order_manager.json     # /order-report 스킬 정의

blackup_bean_order/
├── config/
│   ├── settings.yaml          # 에이전트가 자동 관리 (직접 편집 금지)
│   └── settings.yaml.example  # 스키마 참고용 (개발자용)
├── templates/
│   └── daily_report.md        # 리포트 참고 형식 (예시 포함)
├── examples/                  # 골든 테스트 셋
│   ├── sample_sheet_data.md
│   ├── test_normal.md
│   ├── test_warnings.md
│   └── test_edge_cases.md
├── reports/                   # 리포트 출력 폴더 (YYYY-MM/)
└── docs/
    ├── specs/                 # 설계 스펙
    ├── reviews/               # 설계 비판
    └── debates/               # 토론 기록 (5건)
```

---

## 🏪 매장 목록

블랙업 커피 로스터스 전체 10개 매장:

### 부산 (5개)

| 코드 | 매장명 | 주소 | 영업시간 |
|------|--------|------|---------|
| RST | 로스터리 | 부산진구 신천대로 108 | 10:00-19:00 |
| SM | 서면 본점 | 부산진구 서전로10번길 41 | 09:00-22:00 |
| HD | 해운대 | 해운대구 중동2로 16 1층 | 08:00-20:00 |
| ESD | 을숙도 | 사하구 낙동남로 1233번길 30 | 09:00-21:00 |
| LGR | 롯데 광복 | 중구 중앙대로 2 아쿠아몰 B1 | 10:30-21:00 |

### 경남 (3개)

| 코드 | 매장명 | 주소 | 영업시간 |
|------|--------|------|---------|
| YS | 양산 | 양산시 물금읍 물금리 376-12 | 09:00-22:00 |
| GSW | 거제 수월 | 거제시 제산안길 18 | 09:00-22:00 |
| GH | 고현 | 거제시 서문로5길 6 1층 | 08:00-21:00 |

### 울산 (2개)

| 코드 | 매장명 | 주소 | 영업시간 |
|------|--------|------|---------|
| UOD | 울산 옥동 | 남구 법대로14번길 21 | 09:00-21:00 |
| UHD | 울산 현대백화점 | 남구 삼산로 261 별관 3층 | 10:00-20:00 |

---

## 🔄 설계 진화 과정

### v1-v2: 초기 설계

- 기본 아키텍처 확정, 7개 핵심 결정사항 수립

### v3: 다중 페르소나 검증 (10R)

📄 [multi_persona_debate.md](docs/debates/multi_persona_debate.md) — 로스터 5명 + 매장 5명 관점

### v4: Tech Lead vs Product Lead (15R)

📄 [tech_vs_product_debate.md](docs/debates/tech_vs_product_debate.md) — 기술 vs 비즈니스 공방

### v5: 3자 전문가 토론 (10R)

📄 [three_agent_debate.md](docs/debates/three_agent_debate.md) — Modeling × Product × Tech Lead

### v6: 구현 + 사용성 토론 (20R) — 최종

📄 [implementation_review_debate.md](docs/debates/implementation_review_debate.md) + [settings_usability_debate.md](docs/debates/settings_usability_debate.md)

**v6 주요 개선:**

- ✅ 파일 구조 개편 (`.agent/instructions/` + `.agent/skills/` 분리)
- ✅ settings.yaml 직접 편집 금지 → 대화형 변경
- ✅ 첫 실행 시 명령어 안내 가이드
- ✅ 시나리오 A 확정 (로스터 1인 Antigravity 직접 사용)

---

## 📋 최종 확정 사항

| # | 항목 | 결정 |
|---|------|------|
| 1 | 데이터 형식 | Google Sheets |
| 2 | 데이터 컬럼 | 13개 컬럼 (필수 7 + 선택 6) |
| 3 | Sheets 구성 | **매장별 별도 Sheets** |
| 4 | 인증 방식 | 브라우저 기반 (별도 API 인증 불필요) |
| 5 | 처리 방식 | 에이전트가 직접 처리 (스크립트 0개) |
| 6 | 리포트 | 일일 요약 + 원두별 합산 + 배송 스케줄 |
| 7 | 교차검증 | 스킬 내 자체 검증 (15개 항목) |
| 8 | 개인정보 | 리포트에 주문자·연락처 **미포함** |
| 9 | 경고 체계 | 3단계 (`❌` / `⚠️` / `ℹ️`) |
| 10 | 코드 실행 분리 | 산술=코드, 해석=LLM |
| 11 | 보안 | 읽기 전용, 전용 계정 권장 |
| 12 | 사전 헬스체크 | settings/Sheets/매핑 사전 검증 |
| 13 | 설정 관리 | 사용자 대화형 변경 (YAML 직접 편집 금지) |
| 14 | 사용 시나리오 | 시나리오 A (로스터 1인 직접 사용) |

---

## ✅ 교차검증 체계

### 15개 자동 검증 항목

| # | 검증 항목 | 등급 | 권장 조치 |
|---|-----------|------|----------|
| 1 | 총 주문 건수 일치 | `❌` | 재실행 필요 |
| 2 | 원두별 수량 합계 일치 | `❌` | 재실행 필요 |
| 3 | 매장 수 일치 | `❌` | 누락 매장 시트 확인 |
| 4 | 중복 주문 감지 | `⚠️` | 매장에 확인 연락 |
| 5 | 재고 부족 경고 | `⚠️` | 생두 발주 또는 수량 조율 |
| 6 | 납기 촉박 경고 | `⚠️` | 배송일 조율 연락 |
| 7 | 미등록 원두 감지 | `ℹ️` | settings 추가 여부 결정 |
| 8 | 날짜 형식 검증 | `⚠️` | 형식 수정 요청 |
| 9 | 수량 숫자 검증 | `⚠️` | 해당 행 확인 |
| 10 | 필수 컬럼 누락 | `❌` | 보충 요청 |
| 11 | 원두코드-원두명 매핑 | `ℹ️` | settings 또는 시트 확인 |
| 12 | 이상 수량 감지 | `⚠️` | 오타 확인 |
| 13 | 수량 0 감지 | `⚠️` | 의도 확인 |
| 14 | 시트 접근 불가 | `❌` | 공유 설정·URL 확인 |
| 15 | 리포트 형식 검증 | `ℹ️` | 템플릿 확인 후 재실행 |

---

## 🧪 테스트 전략

### 골든 테스트 셋 3종

| # | 파일 | 시나리오 |
|---|------|---------|
| 1 | [test_normal.md](examples/test_normal.md) | 3매장 5건 정상 주문 |
| 2 | [test_warnings.md](examples/test_warnings.md) | 재고 부족 + 납기 촉박 + 미등록 원두 |
| 3 | [test_edge_cases.md](examples/test_edge_cases.md) | 빈 시트 + 0kg + 이상 수량 + 접근 불가 |

**검증 기준**: 전체 텍스트 일치가 아닌, **핵심 수치** (총 건수, 총 수량, 경고 건수) 비교

---

## 🗺️ 로드맵

### v1.5 (단기)

- **Shipping Manager** (송장 입력 + 수령 확인)
- 리포트를 공유 Google Docs에 자동 기록
- 비상용 간이 집계 스크립트 (DR 대비)
- 리포트 섹션별 on/off 옵션
- 리포트 데이터 CSV 부출력 (수요 예측용)
- 주간 품질 요약 자동 생성

### v2 (향후)

- 주간/월간 트렌드 분석
- 리포트 자동 공유 (카카오톡/Slack)
- 배송 루트 최적화
- Google Sheets API + 서비스 계정
- 수요 예측 모델

---

## 🚀 설치 및 실행

### 전제 조건

- Antigravity 설치 완료
- Google 계정 (에이전트 전용 권장)
- 각 매장의 Google Sheets URL

### 설정 변경 방법

**❌ settings.yaml을 직접 수정하지 마세요!**

에이전트에게 말로 요청하세요:

```text
"에티오피아 하라 원두 추가해줘"
"에티오피아 예가체프 재고 50kg으로 업데이트해줘"
"강남점 Sheets URL 바꿔줘"
"원가 리포트 켜줘"
```

### 현재 상태

**✅ 완료:**

- ✅ 설계 문서 v6 최종 확정
- ✅ 에이전트 instruction + skill 정의
- ✅ 설정 파일 (settings.yaml)
- ✅ 리포트 템플릿
- ✅ 골든 테스트 셋 3종
- ✅ 대화형 설정 변경 (YAML 직접 편집 불필요)
- ✅ 설치 가이드 & 사용자 매뉴얼
- ✅ Google Sheets 템플릿 가이드

자세한 설치 방법은 [설치 가이드](docs/setup_guide.md)를 참고하세요.

---

## 📚 관련 문서

### 설계 스펙

- [📄 Implementation Plan v6](docs/specs/implementation_plan.md)
- [📘 Process Walkthrough](docs/specs/process_walkthrough.md)

### 설계 리뷰

- [🔄 Design Review](docs/reviews/design_review.md)

### 토론 기록 (5건, 50+ 라운드)

- [👥 Multi-Persona Debate](docs/debates/multi_persona_debate.md) — 10R
- [⚔️ Tech vs Product Debate](docs/debates/tech_vs_product_debate.md) — 15R
- [🔺 Three-Agent Debate](docs/debates/three_agent_debate.md) — 10R
- [📋 Implementation Review](docs/debates/implementation_review_debate.md) — 10R
- [🔧 Settings Usability](docs/debates/settings_usability_debate.md) — 10R

---

**Last Updated**: 2026-02-16
**Version**: v7 (구현/문서화 완료)
**Status**: 🟢 배포 준비 완료 (Ready for Deployment)
