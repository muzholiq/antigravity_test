#!/usr/bin/env python3
"""
골든 테스트 검증기 — order_manager.md의 집계 로직을 검증합니다.
테스트 #1~#3의 입력 데이터를 시뮬레이션하고, 기대값과 비교합니다.

실행: python3 scripts/golden_test_validator.py
"""

from collections import defaultdict
from datetime import datetime, timedelta
import json

# ============================================================
# 설정 (settings.yaml에서 가져온 값)
# ============================================================
SETTINGS = {
    "stores": {
        "SM": {"name": "서면본점", "zone": "부산진구", "address": "부산진구 서전로10번길 41"},
        "HD": {"name": "해운대", "zone": "해운대구", "address": "해운대구 중동2로 16 1층"},
        "YS": {"name": "양산", "zone": "양산시", "address": "양산시 물금읍 물금리 376-12"},
    },
    "beans": {
        "ETH-YRG": {"name": "에티오피아 예가체프", "name_en": "Ethiopia Yirgacheffe", "stock_kg": 30, "cost_per_kg": 25000},
        "COL-SUP": {"name": "콜롬비아 수프리모", "name_en": "Colombia Supremo", "stock_kg": 15, "cost_per_kg": 22000},
        "BRA-SAN": {"name": "브라질 산토스", "name_en": "Brazil Santos", "stock_kg": 25, "cost_per_kg": 18000},
    },
    "roasting_profiles": {"라이트": "L-STD", "미디엄": "M-STD", "다크": "D-STD"},
    "min_lead_days": 2,
    "max_order_kg": 50,
}


def validate_order(order, settings, order_date_str="2026-02-15", store_code_expected=None):
    """단일 주문 행에 대해 17개 검증 항목을 실행합니다."""
    warnings = []

    # 검증 #10: 필수 컬럼 누락
    required_fields = ["주문일", "매장코드", "매장명", "원두코드", "원두명", "수량(kg)", "배송희망일"]
    missing = [f for f in required_fields if not order.get(f) and order.get(f) != 0]
    if missing:
        warnings.append({"level": "CRITICAL", "check": 10, "msg": f"필수 컬럼 누락: {', '.join(missing)}", "action": "해당 매장에 보충 요청"})
        return warnings, False  # 스킵 대상

    # 검증 #8: 날짜 형식
    date_str = order.get("주문일", "")
    try:
        order_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        warnings.append({"level": "WARNING", "check": 8, "msg": f"날짜 형식 오류: {date_str}", "action": "해당 매장에 형식 수정 요청"})
        order_date = None

    # 검증 #9: 수량 숫자
    qty = order.get("수량(kg)")
    try:
        qty_num = float(qty)
    except (ValueError, TypeError):
        warnings.append({"level": "WARNING", "check": 9, "msg": f"수량 비숫자: {qty}", "action": "숫자만 입력"})
        qty_num = 0

    # 검증 #12: 이상 수량
    if qty_num > settings["max_order_kg"]:
        warnings.append({"level": "WARNING", "check": 12, "msg": f"이상 수량: {qty_num}kg > {settings['max_order_kg']}kg", "action": "오타 확인, 매장에 확인 연락"})

    # 검증 #13: 수량 0
    if qty_num == 0:
        warnings.append({"level": "WARNING", "check": 13, "msg": f"수량 0kg", "action": "의도된 주문인지 매장에 확인"})

    # 검증 #6: 납기 촉박
    delivery_str = order.get("배송희망일", "")
    try:
        delivery_date = datetime.strptime(delivery_str, "%Y-%m-%d")
        if order_date:
            delta = (delivery_date - order_date).days
            if delta < settings["min_lead_days"]:
                warnings.append({"level": "WARNING", "check": 6, "msg": f"납기 촉박: {delta}일 (min {settings['min_lead_days']}일)", "action": "매장에 배송일 조율 연락"})
    except ValueError:
        pass

    # 검증 #17: 과거 배송일
    if delivery_str:
        try:
            delivery_date = datetime.strptime(delivery_str, "%Y-%m-%d")
            today = datetime.strptime(order_date_str, "%Y-%m-%d")
            if delivery_date < today:
                warnings.append({"level": "CRITICAL", "check": 17, "msg": f"과거 배송일: {delivery_str}", "action": "배송일 재설정 필요"})
        except ValueError:
            pass

    # 검증 #7 / #11: 미등록 원두
    bean_code = order.get("원두코드", "")
    if bean_code and bean_code not in settings["beans"]:
        # 유사 코드 제안
        similar = [c for c in settings["beans"] if c[:3] == bean_code[:3]]
        suggestion = f" (유사: {', '.join(similar)})" if similar else ""
        warnings.append({"level": "INFO", "check": 7, "msg": f"미등록 원두: {bean_code}{suggestion}", "action": "관리자가 settings에 추가 여부 결정"})

    # 검증 #16: 매장코드 교차검증
    if store_code_expected and order.get("매장코드") != store_code_expected:
        warnings.append({"level": "WARNING", "check": 16, "msg": f"매장코드 불일치: 시트 소속 {store_code_expected} ≠ 행 내 {order.get('매장코드')}", "action": "해당 매장에 확인"})

    return warnings, True  # valid


def aggregate_orders(orders, settings):
    """주문들을 집계하고 경고를 생성합니다."""
    # 원두+로스팅 조합별 합산 (매장별 소계)
    bean_totals = defaultdict(lambda: {"total_kg": 0, "store_details": defaultdict(float)})
    for o in orders:
        key = (o["원두코드"], o.get("로스팅단계", "미지정"))
        qty = float(o["수량(kg)"])
        bean_totals[key]["total_kg"] += qty
        bean_totals[key]["store_details"][o["매장코드"]] += qty

    # 원두별 합산 (로스팅 무관)
    bean_only_totals = defaultdict(float)
    for (code, _), v in bean_totals.items():
        bean_only_totals[code] += v["total_kg"]

    # 재고 과부족
    stock_warnings = []
    for code, total in bean_only_totals.items():
        if code in settings["beans"]:
            stock = settings["beans"][code]["stock_kg"]
            diff = stock - total
            if diff < 0:
                stock_warnings.append({
                    "level": "WARNING", "check": 5,
                    "msg": f"재고 부족: {code} 주문 {total}kg > 재고 {stock}kg ({diff:+.1f}kg)",
                    "action": "생두 발주 또는 매장 수량 조율"
                })

    # 중복 주문 감지
    dup_warnings = []
    seen = defaultdict(int)
    for o in orders:
        key = (o["매장코드"], o["원두코드"], o["주문일"])
        seen[key] += 1
    for key, count in seen.items():
        if count > 1:
            dup_warnings.append({
                "level": "INFO", "check": 4,
                "msg": f"중복 주문: {key[0]} {key[1]} {key[2]} — {count}건",
                "action": "매장에 확인 연락"
            })

    # 배송 일정
    delivery_schedule = defaultdict(list)
    for o in orders:
        delivery_schedule[o.get("배송희망일", "미정")].append(o)

    return {
        "bean_totals": dict(bean_totals),
        "bean_only_totals": dict(bean_only_totals),
        "stock_warnings": stock_warnings,
        "dup_warnings": dup_warnings,
        "delivery_schedule": dict(delivery_schedule),
        "total_qty": sum(float(o["수량(kg)"]) for o in orders),
        "total_count": len(orders),
    }


# ============================================================
# 테스트 #1: 정상 시나리오
# ============================================================
def test_1_normal():
    print("=" * 60)
    print("🧪 골든 테스트 #1: 정상 시나리오")
    print("=" * 60)

    orders = [
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "ETH-YRG", "원두명": "에티오피아 예가체프", "수량(kg)": 5, "배송희망일": "2026-02-17", "로스팅단계": "미디엄", "분쇄여부": "홀빈", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "COL-SUP", "원두명": "콜롬비아 수프리모", "수량(kg)": 3, "배송희망일": "2026-02-18", "로스팅단계": "다크", "분쇄여부": "분쇄", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "HD", "매장명": "해운대", "원두코드": "BRA-SAN", "원두명": "브라질 산토스", "수량(kg)": 10, "배송희망일": "2026-02-18", "로스팅단계": "라이트", "분쇄여부": "홀빈", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "HD", "매장명": "해운대", "원두코드": "ETH-YRG", "원두명": "에티오피아 예가체프", "수량(kg)": 3, "배송희망일": "2026-02-17", "로스팅단계": "라이트", "분쇄여부": "홀빈", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "YS", "매장명": "양산", "원두코드": "COL-SUP", "원두명": "콜롬비아 수프리모", "수량(kg)": 5, "배송희망일": "2026-02-18", "로스팅단계": "다크", "분쇄여부": "홀빈", "긴급여부": "N"},
    ]

    # 개별 검증
    all_warnings = []
    valid_orders = []
    for o in orders:
        w, is_valid = validate_order(o, SETTINGS)
        all_warnings.extend(w)
        if is_valid:
            valid_orders.append(o)

    # 집계
    result = aggregate_orders(valid_orders, SETTINGS)
    all_warnings.extend(result["stock_warnings"])
    all_warnings.extend(result["dup_warnings"])

    # 검증
    tests = []
    tests.append(("총 주문 건수", result["total_count"] == 5, f"{result['total_count']} (기대: 5)"))
    tests.append(("총 수량", result["total_qty"] == 26.0, f"{result['total_qty']} (기대: 26.0)"))
    tests.append(("처리 매장 수", len(set(o["매장코드"] for o in valid_orders)) == 3, f"{len(set(o['매장코드'] for o in valid_orders))} (기대: 3)"))
    tests.append(("원두 종류", len(result["bean_only_totals"]) == 3, f"{len(result['bean_only_totals'])} (기대: 3)"))

    # 원두+로스팅 조합 검증
    eth_medium = result["bean_totals"].get(("ETH-YRG", "미디엄"), {}).get("total_kg", 0)
    eth_light = result["bean_totals"].get(("ETH-YRG", "라이트"), {}).get("total_kg", 0)
    col_dark = result["bean_totals"].get(("COL-SUP", "다크"), {}).get("total_kg", 0)
    bra_light = result["bean_totals"].get(("BRA-SAN", "라이트"), {}).get("total_kg", 0)

    tests.append(("ETH-YRG 미디엄", eth_medium == 5.0, f"{eth_medium} (기대: 5.0)"))
    tests.append(("ETH-YRG 라이트", eth_light == 3.0, f"{eth_light} (기대: 3.0)"))
    tests.append(("COL-SUP 다크", col_dark == 8.0, f"{col_dark} (기대: 8.0)"))
    tests.append(("BRA-SAN 라이트", bra_light == 10.0, f"{bra_light} (기대: 10.0)"))

    # 경고 0건
    critical = [w for w in all_warnings if w["level"] == "CRITICAL"]
    warning = [w for w in all_warnings if w["level"] == "WARNING"]
    info = [w for w in all_warnings if w["level"] == "INFO"]
    tests.append(("CRITICAL 0건", len(critical) == 0, f"{len(critical)} (기대: 0)"))
    tests.append(("WARNING 0건", len(warning) == 0, f"{len(warning)} (기대: 0)"))
    tests.append(("INFO 0건", len(info) == 0, f"{len(info)} (기대: 0)"))

    # 개인정보 미포함 확인
    report_text = str(result)
    has_personal = any(name in report_text for name in ["김철수", "이영희", "박민수", "한지민", "최지은"])
    tests.append(("개인정보 미포함", not has_personal, "포함됨" if has_personal else "미포함 ✅"))

    passed = sum(1 for _, ok, _ in tests if ok)
    total = len(tests)
    print(f"\n{'결과':>10}: {passed}/{total} 통과\n")
    for name, ok, detail in tests:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {name}: {detail}")

    return passed == total


# ============================================================
# 테스트 #2: 경고 시나리오
# ============================================================
def test_2_warnings():
    print("\n" + "=" * 60)
    print("🧪 골든 테스트 #2: 경고 시나리오")
    print("=" * 60)

    orders = [
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "ETH-YRG", "원두명": "에티오피아 예가체프", "수량(kg)": 5, "배송희망일": "2026-02-16", "로스팅단계": "미디엄", "분쇄여부": "홀빈", "긴급여부": "Y"},
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "COL-SUP", "원두명": "콜롬비아 수프리모", "수량(kg)": 12, "배송희망일": "2026-02-18", "로스팅단계": "다크", "분쇄여부": "분쇄", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "ETH-YRG", "원두명": "에티오피아 예가체프", "수량(kg)": 5, "배송희망일": "2026-02-16", "로스팅단계": "미디엄", "분쇄여부": "홀빈", "긴급여부": "Y"},
        {"주문일": "2026-02-15", "매장코드": "HD", "매장명": "해운대", "원두코드": "BRA-SAN", "원두명": "브라질 산토스", "수량(kg)": 10, "배송희망일": "2026-02-18", "로스팅단계": "라이트", "분쇄여부": "홀빈", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "HD", "매장명": "해운대", "원두코드": "KEN-AA", "원두명": "케냐 AA", "수량(kg)": 8, "배송희망일": "2026-02-18", "로스팅단계": "미디엄", "분쇄여부": "홀빈", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "YS", "매장명": "양산", "원두코드": "COL-SUP", "원두명": "콜롬비아 수프리모", "수량(kg)": 7, "배송희망일": "2026-02-18", "로스팅단계": "다크", "분쇄여부": "홀빈", "긴급여부": "N"},
    ]

    all_warnings = []
    valid_orders = []
    for o in orders:
        w, is_valid = validate_order(o, SETTINGS)
        all_warnings.extend(w)
        if is_valid:
            valid_orders.append(o)

    result = aggregate_orders(valid_orders, SETTINGS)
    all_warnings.extend(result["stock_warnings"])
    all_warnings.extend(result["dup_warnings"])

    tests = []
    tests.append(("총 주문 건수", result["total_count"] == 6, f"{result['total_count']} (기대: 6)"))
    tests.append(("총 수량", result["total_qty"] == 47.0, f"{result['total_qty']} (기대: 47.0)"))
    tests.append(("처리 매장 수", len(set(o["매장코드"] for o in valid_orders)) == 3, f"3"))

    # 경고 검증
    critical = [w for w in all_warnings if w["level"] == "CRITICAL"]
    warning = [w for w in all_warnings if w["level"] == "WARNING"]
    info = [w for w in all_warnings if w["level"] == "INFO"]

    tests.append(("CRITICAL 0건", len(critical) == 0, f"{len(critical)} (기대: 0)"))
    tests.append(("WARNING 3건", len(warning) == 3, f"{len(warning)} (기대: 3)"))
    tests.append(("INFO 2건", len(info) == 2, f"{len(info)} (기대: 2)"))

    # 구체적 경고 확인
    has_dup = any(w["check"] == 4 for w in all_warnings)
    has_stock = any(w["check"] == 5 for w in all_warnings)
    has_lead = any(w["check"] == 6 for w in all_warnings)
    has_unreg = any(w["check"] == 7 for w in all_warnings)

    tests.append(("중복 주문 감지", has_dup, "감지됨" if has_dup else "미감지"))
    tests.append(("재고 부족 감지", has_stock, "감지됨" if has_stock else "미감지"))
    tests.append(("납기 촉박 감지", has_lead, "감지됨" if has_lead else "미감지"))
    tests.append(("미등록 원두 감지", has_unreg, "감지됨" if has_unreg else "미감지"))

    # COL-SUP 재고 부족 상세
    col_total = result["bean_only_totals"].get("COL-SUP", 0)
    tests.append(("COL-SUP 합계", col_total == 19.0, f"{col_total} (기대: 19.0)"))

    passed = sum(1 for _, ok, _ in tests if ok)
    total = len(tests)
    print(f"\n{'결과':>10}: {passed}/{total} 통과\n")
    for name, ok, detail in tests:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {name}: {detail}")

    if all_warnings:
        print(f"\n  📋 감지된 경고 ({len(all_warnings)}건):")
        for w in all_warnings:
            icon = {"CRITICAL": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(w["level"], "?")
            print(f"    {icon} [{w['level']}] 검증#{w['check']}: {w['msg']}")

    return passed == total


# ============================================================
# 테스트 #3: 엣지 케이스
# ============================================================
def test_3_edge_cases():
    print("\n" + "=" * 60)
    print("🧪 골든 테스트 #3: 엣지 케이스 시나리오")
    print("=" * 60)

    # 서면본점: 3건 + 필수 컬럼 누락 1건
    sm_orders = [
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "ETH-YRG", "원두명": "에티오피아 예가체프", "수량(kg)": 80, "배송희망일": "2026-02-18", "로스팅단계": "미디엄", "분쇄여부": "홀빈", "긴급여부": "N"},
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "COL-SUP", "원두명": "콜롬비아 수프리모", "수량(kg)": 0, "배송희망일": "2026-02-18", "로스팅단계": "다크", "분쇄여부": "분쇄", "긴급여부": "N"},
        {"주문일": "2/15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "BRA-SAN", "원두명": "브라질 산토스", "수량(kg)": 5, "배송희망일": "2026-02-18", "로스팅단계": "라이트", "분쇄여부": "홀빈", "긴급여부": "N"},
        # 필수 컬럼 누락
        {"주문일": "2026-02-15", "매장코드": "SM", "매장명": "서면본점", "원두코드": "", "원두명": "에티오피아 예가체프", "수량(kg)": "", "배송희망일": "2026-02-18", "로스팅단계": "미디엄", "분쇄여부": "홀빈", "긴급여부": "N"},
    ]

    # 해운대: 빈 시트 (0건)
    hd_orders = []

    # 양산: 접근 불가 (시뮬레이션)
    ys_accessible = False

    all_warnings = []
    valid_orders = []
    stores_processed = 0
    stores_failed = []

    # 서면본점 처리
    for o in sm_orders:
        w, is_valid = validate_order(o, SETTINGS, store_code_expected="SM")
        all_warnings.extend(w)
        if is_valid:
            valid_orders.append(o)
    stores_processed += 1

    # 해운대 처리 (빈 시트)
    if not hd_orders:
        all_warnings.append({"level": "INFO", "check": 0, "msg": "해운대: 주문 0건", "action": "바리스타에게 시트 입력 요청"})
    stores_processed += 1

    # 양산 처리 (접근 불가)
    if not ys_accessible:
        all_warnings.append({"level": "CRITICAL", "check": 14, "msg": "양산: Sheets 접근 불가", "action": "공유 설정·URL 확인"})
        stores_failed.append("YS")
    else:
        stores_processed += 1

    result = aggregate_orders(valid_orders, SETTINGS)
    all_warnings.extend(result["stock_warnings"])
    all_warnings.extend(result["dup_warnings"])

    tests = []
    tests.append(("원본 총 행 수", len(sm_orders) == 4, f"{len(sm_orders)} (기대: 4)"))
    tests.append(("유효 주문 건수", result["total_count"] == 3, f"{result['total_count']} (기대: 3)"))
    tests.append(("총 수량", result["total_qty"] == 85.0, f"{result['total_qty']} (기대: 85.0)"))
    tests.append(("처리 매장 수", stores_processed == 2, f"{stores_processed} (기대: 2)"))

    # 경고 등급별 카운트
    critical = [w for w in all_warnings if w["level"] == "CRITICAL"]
    warning = [w for w in all_warnings if w["level"] == "WARNING"]
    info = [w for w in all_warnings if w["level"] == "INFO"]

    tests.append(("CRITICAL 2건", len(critical) == 2, f"{len(critical)} (기대: 2)"))
    tests.append(("WARNING 4건", len(warning) == 4, f"{len(warning)} (기대: 4)"))
    tests.append(("INFO 1건", len(info) == 1, f"{len(info)} (기대: 1)"))

    # 구체적 검증
    has_overqty = any(w["check"] == 12 for w in all_warnings)
    has_zero = any(w["check"] == 13 for w in all_warnings)
    has_datefmt = any(w["check"] == 8 for w in all_warnings)
    has_empty = any("주문 0건" in w["msg"] for w in all_warnings)
    has_access = any(w["check"] == 14 for w in all_warnings)
    has_missing = any(w["check"] == 10 for w in all_warnings)

    tests.append(("이상 수량 감지", has_overqty, "감지됨" if has_overqty else "미감지"))
    tests.append(("수량 0 감지", has_zero, "감지됨" if has_zero else "미감지"))
    tests.append(("날짜 형식 오류 감지", has_datefmt, "감지됨" if has_datefmt else "미감지"))
    tests.append(("빈 시트 감지", has_empty, "감지됨" if has_empty else "미감지"))
    tests.append(("시트 접근 불가 감지", has_access, "감지됨" if has_access else "미감지"))
    tests.append(("필수 컬럼 누락 감지", has_missing, "감지됨" if has_missing else "미감지"))

    passed = sum(1 for _, ok, _ in tests if ok)
    total = len(tests)
    print(f"\n{'결과':>10}: {passed}/{total} 통과\n")
    for name, ok, detail in tests:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {name}: {detail}")

    if all_warnings:
        print(f"\n  📋 감지된 경고 ({len(all_warnings)}건):")
        for w in all_warnings:
            icon = {"CRITICAL": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(w["level"], "?")
            print(f"    {icon} [{w['level']}] 검증#{w['check']}: {w['msg']}")

    return passed == total


# ============================================================
# 실행
# ============================================================
if __name__ == "__main__":
    print()
    print("🏁 블랙업 원두 주문 관리 — 골든 테스트 검증기")
    print(f"   실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []
    results.append(("테스트 #1: 정상 시나리오", test_1_normal()))
    results.append(("테스트 #2: 경고 시나리오", test_2_warnings()))
    results.append(("테스트 #3: 엣지 케이스", test_3_edge_cases()))

    print("\n" + "=" * 60)
    print("📊 전체 결과 요약")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print(f"\n  {'🎉 전체 통과!' if all_passed else '⚠️ 일부 실패 — 확인 필요'}")
    print()
