# -*- coding: utf-8 -*-
"""
목적지 옆 주차장 · Streamlit 단일 화면 앱

[GitHub / 배포]
1. 이 app.py와 requirements.txt 두 파일을 같은 GitHub 폴더에 올립니다.
2. Streamlit Community Cloud에서 저장소 연결, main file = app.py로 배포합니다.
   파일명은 반드시 requirements.txt(복수형)로 유지하세요.
   예전 requirement.txt는 제거하고 이 파일로 교체하세요.
   로컬은 pip install -r requirements.txt 후
   streamlit run app.py 로 실행합니다. Python 3.11 이상 권장.
3. App settings > Secrets에 아래 TOML을 입력합니다. 키를 GitHub에 커밋하지 마세요.
   KAKAO_REST_API_KEY = "카카오_REST_API_키"
   카카오 개발자 앱에서 카카오맵 API 이용 설정/권한/쿼터를 확인하세요.
4. API 키 없이 '가상 데이터' 모드로 검색·비교·요금·추천을 모두 시연할 수 있습니다.

[간편 화면 기본 조건]
- 방문 날짜/입차 시간/예상 주차 시간/검색 반경 입력란은 없습니다.
- 2시간 주차, 반경 1km로 자동 비교합니다. 실제 모드는 현재 한국 시간,
  가상 모드는 당일 12:00~14:00 기준이며 화면에 기준을 표시합니다.

[실제 데이터 / 한계]
- 카카오맵 REST API 장소 키워드 검색 및 PK6 주차장 카테고리 검색:
  https://developers.kakao.com/docs/en/kakaomap/rest-api
  https://dapi.kakao.com/v2/local/search/keyword.json
  https://dapi.kakao.com/v2/local/search/category.json
- 카카오 API는 이름·주소·좌표·장소 링크를 제공하며 전용/제휴 관계, 요금,
  운영시간, 방문객 할인, 도보 경로, 실시간 빈자리를 보장하지 않습니다.
  이 앱은 해당 정보를 이름이나 거리로 유추하지 않습니다.
- 실제 모드의 추가 정보는 아래 PARKING_RECORDS_JSON을 관리자가 공식 안내 또는
  운영자에게 직접 확인한 뒤 등록할 때만 적용됩니다. 미등록은 '확인 필요'.
  정보는 조회 당일 확인된 기록만 계산/운영판정에 사용합니다(보수적 정책).
  방문 예정일에도 동일 조건인지는 출발 전 재확인해야 합니다.
- 추가 정보가 없으면 실제 모드에서도 장소/주차장/지도/길찾기는 동작하나,
  확정 추천과 정확한 요금 계산은 불가능합니다. 가상 모드는 이를 시연합니다.
- 별도 실시간 API는 연결하지 않았으므로 항상 잔여 자리 확인 불가입니다.
- 지도 배경 타일은 네트워크가 필요하며, 가상 모드의 계산은 외부 API 없이 됩니다.

[선택: 확인된 실제 주차장 정보 등록]
Secrets에 PARKING_RECORDS_JSON = '''[ ... ]''' 형태의 JSON 배열을 추가합니다.
아래는 스키마 설명용이며 실제 장소의 요금 정보가 아닙니다. 가짜 값을 실제
모드에 등록하지 마세요. kakao_id는 검색결과의 '주차장 장소 ID'와 정확히 일치,
verified_on은 한국 기준 확인일 YYYY-MM-DD, source_url은 공식 안내 HTTPS URL.
{
  "kakao_id": "실제 주차장 ID", "verified_on": "YYYY-MM-DD",
  "source_url": "https://운영기관의공식안내",
  "hours": {"weekly": {"0": [["09:00","22:00"]],
    "1": [["09:00","22:00"]], "2": [["09:00","22:00"]],
    "3": [["09:00","22:00"]], "4": [["09:00","22:00"]],
    "5": [["09:00","22:00"]], "6": []},
    "exceptions": {"YYYY-MM-DD": []}, "holiday_policy_confirmed": true},
  "tariff": {"complete": true, "free_min": 10, "base_min": 30,
    "base_fee": 1000, "step_min": 10, "step_fee": 500, "daily_cap": 15000,
    "discount": {"label": "방문 인증 시 60분 추가 무료", "free_min": 60,
      "percent": 0, "amount": 0}},
  "affiliations": [{"destination_id": "실제 목적지 ID", "kind": "제휴"}]
}
- weekly의 키는 월요일 0 ~ 일요일 6, []=휴무, 빠진 요일=확인 필요.
  24시간은 [["00:00","24:00"]], 익일 종료는 [["20:00","02:00"]].
  exceptions는 날짜별 대체 시간. holiday_policy_confirmed는 공휴일/특별휴무
  예외 검토까지 했을 때만 true. false 또는 누락은 운영시간 확인 필요 처리.
- tariff.complete=true는 시간/요일/차종별 예외 없는 단일 요금제임을 확인했다는 뜻.
  일반 승용차, 1회 입출차 기준만 지원. 복잡한 요일별 요금은 complete=false로 둡니다.
  기본 무료시간 및 선택한 할인 무료시간 차감 → 기본요금 → 추가요금 올림
  → 선택한 비율/정액 할인 → 일일상한 순서가 실제 규정과 일치할 때만 등록하세요.
  daily_cap=null은 상한이 없음을 확인했다는 의미. 모르면 complete=false.
  discount=null은 할인 없음 확인; 할인 조건을 모르면 complete=false.
  자정 넘김은 재정산 기준이 달라 계산하지 않습니다. 할인은 사용자가 해당
  주차장의 조건 충족을 선택한 경우만 적용하며 중복 할인은 지원하지 않습니다.
- affiliation 누락은 '없음'이 아니라 '확인 필요'. 관계 확인은 목적지 ID로만 매칭.
  반경 검색에 없는 전용·제휴 주차장은 등록한 ID를 키워드 API로 추가 조회합니다.
  단, 카카오에서 ID로 직접 상세 조회하는 API가 없어 키워드+ID 필터 방식을 씁니다.
  등록 레코드에 lookup_query(정확한 주차장 이름)를 함께 넣어야 추가 조회됩니다.
- 출처 링크·확인일을 표시합니다. 직접 HTML에 사용자 입력을 삽입하지 않습니다.
"""

from __future__ import annotations
import io
import json
import math
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from datetime import date, datetime, time, timedelta
from urllib.parse import quote, urlparse
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

KST = ZoneInfo("Asia/Seoul")
UNKNOWN = "확인 필요"


def secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def https_url(value):
    try:
        p = urlparse(str(value))
        host = (p.hostname or "").lower()
        return p.scheme == "https" and bool(host) and host not in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} and not p.username and not p.password
    except ValueError:
        return False


def distance_m(a, b):
    lat1, lat2 = math.radians(a["lat"]), math.radians(b["lat"])
    dlat = lat2 - lat1
    dlon = math.radians(b["lon"] - a["lon"])
    h = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2
    return round(6371000 * 2 * math.asin(min(1, math.sqrt(h))))


def minutes_at(value):
    if value == "24:00":
        return 1440
    if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
        raise ValueError("HH:MM 형식 필요")
    t = datetime.strptime(value, "%H:%M")
    return t.hour*60 + t.minute


def validate_hours(hours):
    if not isinstance(hours, dict):
        raise ValueError("운영시간 형식 오류")
    for section in ["weekly", "exceptions"]:
        mapping = hours.get(section, {})
        if not isinstance(mapping, dict):
            raise ValueError("운영시간 목록 오류")
        for key, slots in mapping.items():
            if section == "weekly":
                if str(key) not in [str(i) for i in range(7)]:
                    raise ValueError("요일 오류")
            else:
                date.fromisoformat(key)
            if not isinstance(slots, list):
                raise ValueError("시간 구간 배열 필요")
            for pair in slots:
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    raise ValueError("시작·종료 쌍 필요")
                a, b = map(minutes_at, pair)
                # 같은 시각은 24시간인지 휴무인지 모호하므로 허용하지 않음.
                if a == 1440 or a == b:
                    raise ValueError("24시간은 00:00~24:00으로 명시")


def operation_status(hours, start, end):
    """운영 구간의 합집합이 전체 이용시간을 포함하는지 확인. 종료시각 출차 허용."""
    try:
        validate_hours(hours)
        if hours.get("holiday_policy_confirmed") is not True or end <= start:
            return "unknown"
        weekly, exceptions = hours.get("weekly", {}), hours.get("exceptions", {})
        intervals, possible = [], []
        day = start.date() - timedelta(days=1)
        while day <= end.date():
            slots = exceptions.get(day.isoformat(), weekly.get(str(day.weekday())))
            midnight = datetime.combine(day, time.min)
            if slots is None:
                # 알 수 없는 전날 심야 운영까지 고려하되, 불필요한 미확인 전파 방지.
                possible.append((midnight, midnight+timedelta(days=2)))
            else:
                for pair in slots:
                    a, b = map(minutes_at, pair)
                    left = midnight+timedelta(minutes=a)
                    right = midnight+timedelta(minutes=b)
                    if b < a:
                        right += timedelta(days=1)
                    intervals.append((left,right))
            day += timedelta(days=1)
        def covers(parts):
            cursor = start
            for left,right in sorted(parts):
                if left <= cursor < right:
                    cursor = max(cursor,right)
                if cursor >= end:
                    return True
            return False
        if covers(intervals):
            return "open"
        return "unknown" if covers(intervals+possible) else "closed"
    except (ValueError, TypeError, AttributeError, OverflowError):
        return "unknown"


def estimate_fee(tariff, start, end, use_discount=False):
    if not isinstance(tariff, dict) or tariff.get("complete") is not True:
        return None, "요금 정보 부족 · 확인 필요"
    if start.date() != end.date():
        return None, "자정 경유: 날짜별 재정산 규정 확인 필요"
    required = ["free_min", "base_min", "base_fee", "step_min", "step_fee", "daily_cap", "discount"]
    if any(key not in tariff for key in required):
        return None, "요금 항목 누락 · 확인 필요"
    try:
        def number(value):
            if isinstance(value, bool):
                raise ValueError
            result = Decimal(str(value))
            if not result.is_finite() or result < 0:
                raise ValueError
            return result
        free, base_min, base_fee, step_min, step_fee = [number(tariff[k]) for k in required[:5]]
        if step_min <= 0:
            raise ValueError
        cap = None if tariff["daily_cap"] is None else number(tariff["daily_cap"])
        disc = tariff["discount"]
        if disc is not None:
            if not isinstance(disc, dict) or not all(k in disc for k in ["free_min","percent","amount","label"]):
                raise ValueError
            df, percent, amount = [number(disc[k]) for k in ["free_min","percent","amount"]]
            if percent > 100 or not isinstance(disc["label"],str) or not disc["label"].strip():
                raise ValueError
        else:
            df = percent = amount = Decimal(0)
        if not use_discount:
            df = percent = amount = Decimal(0)
        total = Decimal(math.ceil((end-start).total_seconds()/60))
        if total <= 0:
            raise ValueError
        billable = max(Decimal(0),total-free-df)
        extra = (max(Decimal(0),billable-base_min)/step_min).to_integral_value(rounding=ROUND_CEILING)
        cost = Decimal(0) if billable == 0 else base_fee+extra*step_fee
        cost = max(Decimal(0),cost*(1-percent/100)-amount)
        if cap is not None:
            cost = min(cost,cap)
        if cost != cost.to_integral_value():
            return None, "할인 후 원 미만 반올림 규정 확인 필요"
        detail = "할인 조건 적용" if use_discount and disc is not None else "할인 미적용"
        return int(cost), f"등록된 단일 요금제 기준 예상액 · {detail} · 현장 확인 필요"
    except (TypeError, ValueError, OverflowError, InvalidOperation):
        return None, "요금 규칙 오류 또는 미확인 · 확인 필요"


def tariff_text(t):
    if not isinstance(t, dict) or not t.get("complete"):
        return UNKNOWN
    try:
        cap = "상한 없음" if t["daily_cap"] is None else f"일 최대 {t['daily_cap']:,}원"
        return (f"무료 {t['free_min']}분 / 기본 {t['base_min']}분 {t['base_fee']:,}원 / "
                f"추가 {t['step_min']}분당 {t['step_fee']:,}원 / {cap}")
    except (KeyError, TypeError, ValueError):
        return UNKNOWN


def hours_text(h, start, end):
    try:
        validate_hours(h)
        entries = []
        day = start.date()
        while day <= end.date():
            slots = h.get("exceptions", {}).get(day.isoformat(),h.get("weekly", {}).get(str(day.weekday())))
            def label(a,b):
                suffix = " (익일 종료)" if minutes_at(b)<minutes_at(a) else ""
                return f"{a}–{b}{suffix}"
            text = UNKNOWN if slots is None else ("휴무" if not slots else ", ".join(label(a,b) for a,b in slots))
            entries.append(f"{day:%m/%d} {text}")
            day += timedelta(days=1)
        return " / ".join(entries)
    except (ValueError,TypeError,AttributeError):
        return UNKNOWN


@st.cache_data(ttl=300, show_spinner=False)
def kakao_search(key, path, params):
    r = requests.get("https://dapi.kakao.com/v2/local/search/"+path+".json",
                     headers={"Authorization": "KakaoAK "+key}, params=params, timeout=(5, 12))
    r.raise_for_status()
    result = r.json()
    return result.get("documents", []), result.get("meta", {})


def place(doc):
    return {"id": str(doc["id"]), "name": doc["place_name"],
            "address": doc.get("road_address_name") or doc.get("address_name") or UNKNOWN,
            "lat": float(doc["y"]), "lon": float(doc["x"]),
            "url": doc.get("place_url", ""), "phone": doc.get("phone", "")}


def validated_records():
    raw = secret("PARKING_RECORDS_JSON", "[]")
    try:
        rows = json.loads(raw)
        if not isinstance(rows, list):
            raise ValueError
    except (TypeError, ValueError):
        st.warning("추가 정보 JSON 형식이 잘못되어 적용하지 않았습니다.")
        return {}
    valid = {}
    rejected = 0
    for r in rows:
        try:
            if not isinstance(r, dict) or not r.get("kakao_id") or not https_url(r.get("source_url", "")):
                raise ValueError
            if date.fromisoformat(r.get("verified_on", "")) != datetime.now(KST).date():
                raise ValueError
            h = r.get("hours")
            if h is not None:
                validate_hours(h)
            if r.get("tariff") is not None and not isinstance(r["tariff"],dict):
                raise ValueError
            if r.get("tariff", {}) and r["tariff"].get("complete") is True:
                check_start = datetime.combine(datetime.now(KST).date(),time(12))
                if estimate_fee(r["tariff"],check_start,check_start+timedelta(hours=1))[0] is None:
                    raise ValueError
            if not isinstance(r.get("affiliations", []), list):
                raise ValueError
            if any(not isinstance(a, dict) or a.get("kind") not in ["전용", "제휴"] or not a.get("destination_id") for a in r.get("affiliations", [])):
                raise ValueError
            valid[str(r["kakao_id"])] = r
        except (ValueError, TypeError, AttributeError):
            rejected += 1
    if rejected:
        st.caption(f"추가 기록 {rejected}개는 출처/당일 확인일/형식 검증을 통과하지 않아 사용하지 않았습니다.")
    return valid


def demo_data():
    destinations = [
        {"id": "demo-1", "name": "가상 · 햇살식당", "address": "가상시 나들이구 산책로 10 (시연용)", "lat": 37.5665, "lon": 126.9780},
        {"id": "demo-2", "name": "가상 · 햇살식당", "address": "가상시 나들이구 호수로 80 (동명 장소 시연)", "lat": 37.5700, "lon": 126.9820},
        {"id": "demo-3", "name": "가상 · 초록정원", "address": "가상시 나들이구 정원길 5 (시연용)", "lat": 37.5680, "lon": 126.9750}]
    def hours(a, b):
        return {"weekly": {str(i): [[a,b]] for i in range(7)}, "exceptions": {}, "holiday_policy_confirmed": True}
    def fee(base, step, cap, discount=None):
        return {"complete": True, "free_min": 10, "base_min": 30, "base_fee": base,
                "step_min": 10, "step_fee": step, "daily_cap": cap, "discount": discount}
    ds = {"label": "식당 영수증 인증 시 추가 60분 무료 (가상 조건)", "free_min": 60, "percent": 0, "amount": 0}
    common = {"verified_on": "가상 시연 설정", "source_label": "가상 데이터 · 실제 시설이 아님"}
    lots = [
        {"id":"demo-p1", "name":"가상 · 식당 전용 주차장", "address":"가상시 산책로 10 지하", "lat":37.5668,"lon":126.9782,
         "hours":hours("10:00","22:00"),"tariff":fee(2000,1000,30000,ds),
         "affiliations":[{"destination_id":"demo-1","kind":"전용"}]},
        {"id":"demo-p2", "name":"가상 · 산책 공영주차장", "address":"가상시 산책로 25", "lat":37.5678,"lon":126.9798,
         "hours":hours("00:00","24:00"),"tariff":fee(500,200,8000),"affiliations":[]},
        {"id":"demo-p3", "name":"가상 · 정원 제휴주차장", "address":"가상시 정원길 20", "lat":37.5685,"lon":126.9743,
         "hours":hours("09:00","21:00"),"tariff":fee(1000,400,12000),
         "affiliations":[{"destination_id":"demo-3","kind":"제휴"}]},
        {"id":"demo-p4", "name":"가상 · 저녁 주차장", "address":"가상시 호수로 60", "lat":37.5695,"lon":126.9812,
         "hours":hours("18:00","23:00"),"tariff":fee(300,100,5000),"affiliations":[]},
        {"id":"demo-p5", "name":"가상 · 정보 미확인 주차장", "address":"가상시 산책로 30", "lat":37.5671,"lon":126.9770,
         "hours":None,"tariff":None,"affiliations":[]}]
    return destinations, [dict(common, **p) for p in lots]


def affiliation(p, destination_id):
    return next((a.get("kind") for a in p.get("affiliations", []) if str(a.get("destination_id")) == str(destination_id)), None)


def rank_lots(rows, criterion):
    eligible = [dict(r) for r in rows if r["status"] == "open"]
    if criterion != "거리 우선":
        eligible = [r for r in eligible if r["cost"] is not None]
    if not eligible:
        return []
    if criterion == "요금 우선":
        eligible.sort(key=lambda r: (r["cost"], r["distance"], r["id"]))
    elif criterion == "거리 우선":
        eligible.sort(key=lambda r: (r["distance"], r["cost"] if r["cost"] is not None else math.inf, r["id"]))
    else:
        lo_c, hi_c = min(r["cost"] for r in eligible), max(r["cost"] for r in eligible)
        lo_d, hi_d = min(r["distance"] for r in eligible), max(r["distance"] for r in eligible)
        for r in eligible:
            nc = (r["cost"]-lo_c)/(hi_c-lo_c) if hi_c>lo_c else 0
            nd = (r["distance"]-lo_d)/(hi_d-lo_d) if hi_d>lo_d else 0
            r["score"] = .5*nc + .5*nd
        eligible.sort(key=lambda r: (r["score"], r["cost"], r["distance"], r["id"]))
    return eligible


def show_lot(r, destination_id, demo, compact=False):
    kind = affiliation(r, destination_id)
    relation = kind if kind else ("전용·제휴 아님 (가상 설정)" if demo else "전용·제휴 관계 확인 필요")
    price = f"{r['cost']:,}원 예상" if r["cost"] is not None else "예상요금 확인 필요"
    st.markdown(f"**{r['name']}**")
    st.write(f"{price} · 직선 {r['distance']:,}m · {relation}")
    st.caption(r["address"])
    if not compact:
        st.write(f"운영시간: {r['hours_label']}")
        st.write(f"기본 요금: {tariff_text(r.get('tariff'))}")
        discount = (r.get("tariff") or {}).get("discount")
        st.write("방문객 할인: " + (str(discount.get("label", UNKNOWN)) if isinstance(discount, dict) else ("없음 (확인된 요금제)" if (r.get("tariff") or {}).get("complete") else UNKNOWN)))
        st.caption(r["fee_note"])
        st.caption("실시간 잔여 자리 확인 불가 · 주차 가능 여부를 보장하지 않습니다.")
        if demo:
            st.caption("가상 데이터 · 이름/주소/운영/요금/관계는 모두 시연용. 좌표는 화면 표시용입니다.")
        else:
            st.caption(f"주차장 장소 ID: {r['id']} · 추가 정보 확인일: {r.get('verified_on', UNKNOWN)}")
            if https_url(r.get("source_url", "")):
                st.link_button("운영·요금 정보 출처", r["source_url"])
            if r.get("url"):
                st.link_button("카카오맵 장소 정보", r["url"])


def main():
    st.set_page_config(page_title="목적지 옆 주차장", page_icon="🅿️", layout="centered")
    st.markdown("""<style>
    .block-container{max-width:800px;padding-top:1.4rem;padding-bottom:2rem}
    h1{font-size:1.85rem!important}h2{font-size:1.35rem!important}
    button{min-height:48px!important;white-space:normal!important}
    [data-testid="stBaseButton-primary"]{background:#176B55;border-color:#176B55}
    [data-testid="stMarkdownContainer"] p{font-size:1.04rem;overflow-wrap:anywhere}
    [data-testid="stCaptionContainer"] p{font-size:.91rem}
    @media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem}
    [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important}
    [data-testid="stColumn"]{min-width:100%!important;width:100%!important;flex:1 1 100%!important}}
    </style>""", unsafe_allow_html=True)
    st.title("🅿️ 목적지 옆 주차장")
    st.caption("식당·나들이 장소를 고르면, 주차 조건을 한눈에 비교해 드려요.")
    mode = st.radio("사용 모드", ["가상 데이터 · 시연", "실제 장소 · API"], horizontal=True)
    demo = mode.startswith("가상")
    if demo:
        st.warning("가상 데이터 모드입니다. 실제 시설·요금·빈자리 정보가 아닙니다.")
    else:
        st.info("실제 장소는 카카오 API로 검색합니다. 확인된 운영·요금 정보가 없으면 확정 추천하지 않습니다.")
    key = str(secret("KAKAO_REST_API_KEY", "")).strip()
    today = datetime.now(KST).date()
    with st.form("search_form"):
        query = st.text_input("① 어디로 가세요?", placeholder="예: 햇살식당 / 경복궁 / 부산 맛집", max_chars=100)
        submitted = st.form_submit_button("장소 검색", type="primary", use_container_width=True)
    if st.session_state.get("mode") != mode:
        st.session_state["mode"] = mode
        st.session_state.pop("destinations", None)
        st.session_state.pop("destination_choice", None)
        for state_key in list(st.session_state):
            if state_key.startswith(("discounts_", "lot_")):
                del st.session_state[state_key]
    if submitted:
        st.session_state.pop("destination_choice", None)
        st.session_state["destinations"] = []
        if demo:
            ds, _ = demo_data()
            q = query.strip().lower()
            st.session_state["destinations"] = [d for d in ds if not q or q in d["name"].lower() or q in d["address"].lower()]
        elif not query.strip():
            st.warning("목적지 이름을 입력해 주세요.")
        elif not key:
            st.error("API 키가 없습니다. Secrets에 KAKAO_REST_API_KEY를 설정하거나 가상 데이터 모드를 사용하세요.")
        else:
            try:
                with st.spinner("장소를 찾고 있어요…"):
                    docs, meta = kakao_search(key, "keyword", {"query": query.strip(), "size":15})
                st.session_state["destinations"] = [place(d) for d in docs]
                if not meta.get("is_end", True):
                    st.caption("검색 결과 중 첫 15개입니다. 지역명을 붙여 검색하면 더 정확해요.")
            except (requests.RequestException, ValueError, KeyError):
                st.error("장소 검색에 실패했습니다. API 키·이용 권한·쿼터·연결 상태를 확인한 뒤 다시 검색해 주세요.")
    destinations = st.session_state.get("destinations", [])
    if demo and "destinations" not in st.session_state:
        destinations, _ = demo_data()
    if not destinations:
        st.caption("검색 결과가 없으면 지역명 또는 다른 장소 이름으로 검색하세요. 시연은 '햇살식당' 또는 '초록정원'을 사용하세요.")
        return
    by_id = {d["id"]: d for d in destinations}
    selected_id = st.selectbox("검색 결과 · 주소를 보고 선택하세요", list(by_id),
                               format_func=lambda i: f"{by_id[i]['name']} | {by_id[i]['address']}", key="destination_choice")
    dest = by_id[selected_id]
    st.caption("선택한 주소: " + dest["address"])
    # 방문 조건 입력 UI 제거: 간단한 기본 조건으로 자동 비교합니다.
    duration, radius = 120, 1000
    start = (datetime.combine(today,time(12,0)) if demo else
             datetime.now(KST).replace(tzinfo=None,second=0,microsecond=0))
    end = start+timedelta(minutes=duration)
    lots = []
    if demo:
        _, all_lots = demo_data()
        lots = [p for p in all_lots if distance_m(dest,p)<=radius or affiliation(p,dest["id"])]
    elif key:
        records = validated_records()
        try:
            with st.spinner("주변 주차장을 확인하고 있어요…"):
                docs = []
                last_meta = {}
                for page in range(1,4):
                    part, last_meta = kakao_search(key,"category", {"category_group_code":"PK6", "x":dest["lon"],"y":dest["lat"],"radius":radius,"sort":"distance","size":15,"page":page})
                    docs.extend(part)
                    if last_meta.get("is_end",True):
                        break
                indexed = {str(d["id"]): d for d in docs}
                for pid, rec in records.items():
                    if pid not in indexed and affiliation(rec,dest["id"]) and rec.get("lookup_query"):
                        more, _ = kakao_search(key,"keyword",{"query":rec["lookup_query"],"category_group_code":"PK6","size":15})
                        for d in more:
                            if str(d["id"]) == pid:
                                indexed[pid] = d
                for pid,d in indexed.items():
                    p = place(d)
                    rec = records.get(pid,{})
                    for field in ["hours","tariff","affiliations","source_url","verified_on"]:
                        if field in rec:
                            p[field] = rec[field]
                    lots.append(p)
                if not last_meta.get("is_end",True):
                    st.caption("주변 검색은 가까운 최대 45개 결과입니다. 지역 내 모든 주차장을 포함하지 않을 수 있습니다.")
                missing = [pid for pid,r in records.items() if affiliation(r,dest["id"]) and pid not in indexed]
                if missing:
                    st.warning("등록된 전용·제휴 주차장 일부는 지도 위치 조회가 안 되어 목록에서 제외했습니다. 목적지에 직접 문의하세요.")
        except (requests.RequestException,ValueError,KeyError):
            st.error("주차장 조회에 실패했습니다. 연결·API 권한을 확인하고 아래 버튼으로 재시도하세요.")
            if st.button("주차장 조회 다시 시도",use_container_width=True):
                st.rerun()
            return
    st.subheader("② 목적지 전용·제휴 먼저 확인")
    st.caption(f"자동 비교 기준: 2시간 주차 · 주변 반경 1km · {'가상 시연 기준 ' if demo else '한국 시간 '}{start:%m/%d %H:%M}~{end:%m/%d %H:%M}")
    affiliated = [p for p in lots if affiliation(p,dest["id"])]
    if not affiliated and demo:
        st.info("가상 데이터 설정상 이 목적지의 전용·제휴 주차장은 없습니다. 주변 후보를 비교해 보세요.")
    elif not affiliated:
        st.info("전용·제휴 주차장: 확인 필요. 검색되지 않았다는 이유만으로 '없음'으로 판단하지 않습니다. 목적지에 문의해 주세요.")
    else:
        st.caption("전용·제휴라는 이유로 순위를 높이지 않습니다. 아래 주변 주차장과 같은 기준으로 비교합니다.")
    discount_ids = []
    for p in lots:
        d = (p.get("tariff") or {}).get("discount")
        if isinstance(d,dict):
            discount_ids.append(p["id"])
    picked_discounts = []
    if discount_ids:
        with st.expander("방문객 할인 조건을 충족하나요? · 직접 선택", expanded=False):
            discount_map = {p["id"]:p for p in lots}
            picked_discounts = st.multiselect("조건을 충족하는 주차장만 선택", discount_ids, default=[],
                format_func=lambda i: f"{discount_map[i]['name']} — {discount_map[i]['tariff']['discount'].get('label',UNKNOWN)}",
                key=f"discounts_{mode}_{dest['id']}")
            st.caption("영수증·인증·구매금액 등 조건을 충족한 경우만 적용됩니다. 중복 할인 미지원.")
    rows = []
    for p in lots:
        cost, note = estimate_fee(p.get("tariff"),start,end,p["id"] in picked_discounts)
        rows.append(dict(p,cost=cost,fee_note=note,distance=distance_m(dest,p),
                         status=operation_status(p.get("hours"),start,end),hours_label=hours_text(p.get("hours"),start,end)))
    for r in rows:
        if affiliation(r,dest["id"]):
            with st.expander(r["name"] + " · " + affiliation(r,dest["id"]), expanded=True):
                show_lot(r,dest["id"],demo)
    st.subheader("③ 추천 주차장 · 상위 3곳")
    criterion = st.radio("추천 기준", ["요금 우선","거리 우선","요금·거리 균형"], horizontal=True)
    st.caption("모든 거리는 목적지와의 직선거리입니다. 도보 경로·도보 시간은 제공하지 않습니다. 운영 구간 전체가 확인된 주차장만 추천합니다.")
    explanations = {
        "요금 우선":"예상요금이 낮은 순 → 동률이면 직선거리가 가까운 순. 요금 미확인 제외.",
        "거리 우선":"직선거리가 가까운 순 → 동률이면 확인된 예상요금이 낮은 순. 요금 미확인도 포함하며 표시합니다.",
        "요금·거리 균형":"운영·요금 확인 후보 안에서 요금과 거리를 각각 0~1로 정규화해 50%씩 합산합니다. 낮을수록 우선이며 동률은 요금·거리 순. 미확인 요금 제외."}
    st.caption(explanations[criterion])
    ranked = rank_lots(rows,criterion)
    top = ranked[:3]
    if not top:
        st.warning("조건을 확인할 수 있는 추천 후보가 없습니다. 운영시간·요금 확인 후 다시 비교하세요. 미확인 후보는 아래에서 볼 수 있습니다.")
    for i,r in enumerate(top,1):
        with st.container(border=True):
            st.markdown(f"**{i}순위**")
            show_lot(r,dest["id"],demo,compact=True)
            why = f"예상요금 {r['cost']:,}원 기준으로 우선" if criterion=="요금 우선" else (f"직선 {r['distance']:,}m로 가까운 순" if criterion=="거리 우선" else f"균형 점수 {r['score']:.3f} (요금 50% + 거리 50%)")
            st.caption("추천 이유: " + why + " · 등록된 시간표상 전체 이용 구간 운영")
            if r["cost"] is None:
                st.caption("주의: 요금 미확인 · 저렴하다는 의미가 아닙니다.")
    closed = [r for r in rows if r["status"]=="closed"]
    unknown = [r for r in rows if r["status"]=="unknown"]
    st.caption(f"조회 {len(rows)}곳 · 운영시간 밖 {len(closed)}곳 추천 제외 · 운영 미확인 {len(unknown)}곳 확정 추천 제외 · 실시간 잔여 자리 확인 불가")
    if rows:
        with st.expander("전체 후보 비교 · 미확인 / 운영시간 밖 포함",expanded=False):
            order = sorted(rows,key=lambda r:r["distance"])
            st.dataframe(pd.DataFrame([{"주차장":r["name"],"예상요금":f"{r['cost']:,}원" if r["cost"] is not None else UNKNOWN,
                "직선거리":f"{r['distance']:,}m","이용시간 운영":{"open":"시간표상 운영","closed":"운영시간 밖","unknown":UNKNOWN}[r["status"]],
                "운영시간":r["hours_label"],"주소":r["address"]} for r in order]), hide_index=True,use_container_width=True)
            st.caption("작은 화면에서는 아래 주차장 선택 후 세로형 상세정보를 확인하세요.")
        candidates = {r["id"]:r for r in top}
        candidates.update({r["id"]:r for r in rows})
        # top의 순위를 유지하며 미확인 후보도 상세 조회 가능
        lot_key = f"lot_{mode}_{dest['id']}"
        if st.session_state.get(lot_key) not in candidates:
            st.session_state.pop(lot_key,None)
        choice = st.selectbox("지도·상세정보를 볼 주차장",list(candidates),format_func=lambda i:candidates[i]["name"], key=lot_key)
        selected = candidates[choice]
        with st.expander("선택한 주차장 상세정보",expanded=False):
            show_lot(selected,dest["id"],demo)
            st.write("이용시간 운영: " + {"open":"등록 시간표상 운영","closed":"운영시간 밖 · 추천 제외","unknown":UNKNOWN}[selected["status"]])
        st.caption("지도: 목적지와 선택 주차장 두 지점 · 길찾기 경로가 아닙니다.")
        st.map(pd.DataFrame([{"lat":dest["lat"],"lon":dest["lon"],"color":"#176B55","size":80},
                             {"lat":selected["lat"],"lon":selected["lon"],"color":"#E87439","size":120}]),
               latitude="lat",longitude="lon",color="color",size="size",height=260)
        st.caption("초록 = 목적지 · 주황 = 선택 주차장")
        if demo:
            st.info("가상 주차장으로 잘못 이동하지 않도록 시연 모드에서는 길찾기를 연결하지 않습니다.")
        else:
            url = f"https://map.kakao.com/link/to/{quote(selected['name'],safe='')},{selected['lat']},{selected['lon']}"
            st.link_button("🧭 카카오맵에서 주차장까지 길찾기",url,type="primary",use_container_width=True)
            st.caption("지도 앱 또는 웹으로 연결됩니다. 출발지는 지도에서 설정하세요. 주차 입구 위치도 확인해 주세요.")
    st.caption("예상요금은 등록된 요금표 기준입니다. 할인 적용 및 실제 이용시간에 따라 달라질 수 있습니다.")
    if not demo:
        st.link_button("데이터 출처 · 카카오맵 REST API 안내","https://developers.kakao.com/docs/en/kakaomap/rest-api")



if __name__ == "__main__":
    main()
