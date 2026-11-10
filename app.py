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
    .block-container{max-width:620px;padding:1rem 1rem 1.5rem}
    h1{font-size:1.6rem!important}h2,h3{font-size:1.2rem!important}
    button{min-height:46px!important;white-space:normal!important}
    [data-testid="stVerticalBlock"]{gap:.65rem}
    [data-testid="stBaseButton-primary"]{background:#176B55;border-color:#176B55}
    p{overflow-wrap:anywhere}
    </style>""",unsafe_allow_html=True)
    st.title("🅿️ 목적지 옆 주차장")
    key=str(secret("KAKAO_REST_API_KEY", "")).strip()
    ss=st.session_state
    ss.setdefault("screen", "search")
    screen=ss["screen"]
    st.caption({"search":"1 검색  ›  2 비교  ›  3 지도·상세", "compare":"1 검색  ›  ② 비교  ›  3 지도·상세", "detail":"1 검색  ›  2 비교  ›  ③ 지도·상세"}[screen])
    if screen=="search":
        mode=st.radio("데이터",["실제 장소", "가상 시연"],index=0 if key else 1,horizontal=True)
        demo=mode=="가상 시연"
        if ss.get("mobile_mode")!=mode:
            ss["mobile_mode"]=mode
            ss.pop("mobile_results",None)
            ss.pop("mobile_destination",None)
        if demo: st.caption("가상 데이터 · 실제 시설·요금 정보가 아닙니다.")
        # 한국어 음성 입력: 브라우저 음성인식 사용, 별도 API 키 불필요.
        # HTTPS 및 마이크 권한 필요. 음성이 브라우저 제공 음성인식 서비스로
        # 전송될 수 있습니다. 지원되지 않는 브라우저에서는 직접 입력하세요.
        try:
            from streamlit_mic_recorder import speech_to_text
        except ImportError:
            st.caption("음성 검색 설치 대기 중 · requirements.txt 교체 후 재배포해 주세요.")
        else:
            spoken = speech_to_text(
                language="ko-KR", start_prompt="🎤 말로 장소 입력",
                stop_prompt="⏹ 입력 마치기", just_once=True,
                use_container_width=True, key="parking_voice_search")
            if isinstance(spoken, str) and spoken.strip():
                ss["mobile_query"] = spoken.strip()[:100]
            with st.expander("마이크 사용 안내"):
                st.caption("마이크를 허용하고 장소를 말한 뒤 검색을 누르세요. HTTPS와 지원 브라우저가 필요합니다. 음성이 브라우저 음성인식 서비스로 전송될 수 있습니다. 작동하지 않으면 직접 입력하세요.")
        with st.form("mobile_search"):
            query=st.text_input("어디로 가세요?",placeholder="장소명 또는 지역 + 장소명",max_chars=100,key="mobile_query")
            submit=st.form_submit_button("장소 검색",type="primary",use_container_width=True)
        if submit:
            ss.pop("mobile_destination",None)
            if demo:
                ds,_=demo_data()
                q=query.strip().lower()
                ss["mobile_results"]=[d for d in ds if not q or q in d["name"].lower() or q in d["address"].lower()]
            elif not key:
                st.error("Secrets에 KAKAO_REST_API_KEY를 설정해 주세요.")
            elif not query.strip(): st.warning("장소 이름을 입력해 주세요.")
            else:
                try:
                    docs,_=kakao_search(key,"keyword",{"query":query.strip(),"size":15})
                    ss["mobile_results"]=[place(d) for d in docs]
                except (requests.RequestException,ValueError,KeyError):
                    ss["mobile_results"]=[]
                    st.error("검색 연결에 실패했습니다. 키와 API 권한을 확인해 주세요.")
        results=ss.get("mobile_results",[])
        if demo and "mobile_results" not in ss: results=demo_data()[0]
        if results:
            by_id={d["id"]:d for d in results}
            selected=st.selectbox("목적지 선택 · 주소 포함",list(by_id),format_func=lambda i:by_id[i]["name"]+" · "+by_id[i]["address"],key="mobile_destination")
            if st.button("주변 주차장 비교 →",type="primary",use_container_width=True):
                ss["destination"]=by_id[selected];ss["demo"]=demo
                ss["visit_start"]=(datetime.combine(datetime.now(KST).date(),time(12,0)) if demo else datetime.now(KST).replace(tzinfo=None,second=0,microsecond=0))
                ss.pop("mobile_lots",None);ss.pop("mobile_discounts",None)
                ss["screen"]="compare";st.rerun()
        elif "mobile_results" in ss: st.info("검색 결과가 없습니다. 지역명을 함께 입력해 보세요.")
        return
    if st.button("← 장소 다시 찾기",key="back_search"):
        ss["screen"]="search";st.rerun()
    dest=ss["destination"];demo=ss["demo"]
    start=ss["visit_start"];end=start+timedelta(minutes=120);radius=1000
    st.markdown("**"+dest["name"]+"**"+(" · 가상 데이터" if demo else ""))
    if "mobile_lots" not in ss:
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
        ss["mobile_lots"]=lots
    lots=ss["mobile_lots"]
    picked=ss.get("mobile_discounts",[])
    rows=[]
    for lot in lots:
        cost,note=estimate_fee(lot.get("tariff"),start,end,lot["id"] in picked)
        rows.append(dict(lot,cost=cost,fee_note=note,distance=distance_m(dest,lot),status=operation_status(lot.get("hours"),start,end),hours_label=hours_text(lot.get("hours"),start,end)))
    if ss["screen"]=="compare":
        criterion=st.selectbox("추천 기준",["요금 우선","거리 우선","요금·거리 균형"],key="mobile_criterion")
        st.caption("2시간 주차 · 반경 1km · 직선거리")
        ranked=rank_lots(rows,criterion)[:3]
        for n,r in enumerate(ranked,1):
            price=f"{r['cost']:,}원" if r['cost'] is not None else "요금 미확인"
            kind=affiliation(r,dest["id"])
            label=f"{n}. {r['name']}"+(f" · {kind}" if kind else "")
            with st.container(border=True):
                st.markdown("**"+label+"**")
                st.write(f"{price} 예상 · 직선 {r['distance']:,}m")
                if st.button("지도·상세 →",key="detail_"+str(r["id"]),use_container_width=True):
                    ss["selected_lot"]=r["id"];ss["screen"]="detail";st.rerun()
        if not ranked:
            st.info("운영·요금이 확인된 추천 후보가 없습니다.")
        if rows and st.button("전체 후보·전용/제휴 보기 →",use_container_width=True):
            ss["selected_lot"]=rows[0]["id"];ss["screen"]="detail";st.rerun()
        if not rows: st.info("주변 검색 결과가 없습니다.")
        with st.expander("추천 기준·제외 사유"):
            st.write({"요금 우선":"요금이 낮은 순, 동률이면 가까운 순입니다.","거리 우선":"직선거리가 가까운 순입니다. 요금 미확인 후보도 포함합니다.","요금·거리 균형":"확인된 요금·거리를 각각 0~1로 정규화해 50%씩 반영합니다."}[criterion])
            st.caption("운영시간 밖·운영 미확인 후보는 추천에서 제외합니다. 요금 우선·균형은 요금 미확인도 제외합니다. 전용·제휴 여부는 가산하지 않습니다.")
            st.caption(f"비교 시간 {start:%m/%d %H:%M}~{end:%H:%M} · 실시간 잔여 자리 확인 불가")
        return
    if st.button("← 비교 결과",key="back_compare"):
        ss["screen"]="compare";st.rerun()
    choices={r["id"]:r for r in rows}
    if not choices:
        st.info("조회된 주차장이 없습니다.");return
    initial=ss.get("selected_lot")
    options=list(choices)
    selected_id=st.selectbox("주차장",options,index=options.index(initial) if initial in options else 0,format_func=lambda i:choices[i]["name"]+(" · "+affiliation(choices[i],dest["id"]) if affiliation(choices[i],dest["id"]) else ""))
    r=choices[selected_id]
    price=f"{r['cost']:,}원 예상" if r['cost'] is not None else "요금 확인 필요"
    st.write(f"**{price} · 직선 {r['distance']:,}m**")
    st.caption(r["address"])
    st.map(pd.DataFrame([{"lat":dest["lat"],"lon":dest["lon"],"color":"#176B55","size":18},{"lat":r["lat"],"lon":r["lon"],"color":"#E87439","size":24}]),latitude="lat",longitude="lon",color="color",size="size",height=200)
    if not demo:
        url=f"https://map.kakao.com/link/to/{quote(r['name'],safe='')},{r['lat']},{r['lon']}"
        st.link_button("카카오맵 길찾기",url,type="primary",use_container_width=True)
    else: st.caption("가상 위치 · 길찾기는 실제 모드에서 제공")
    with st.expander("운영시간·요금·방문객 할인"):
        st.write("운영시간: "+r["hours_label"])
        st.write("이용 구간: "+{"open":"시간표상 운영","closed":"운영시간 밖","unknown":"확인 필요"}[r["status"]])
        st.write(tariff_text(r.get("tariff")))
        discount=(r.get("tariff") or {}).get("discount")
        if isinstance(discount,dict):
            checked=st.checkbox(str(discount.get("label","방문객 할인 조건 충족")),value=r["id"] in picked,key="apply_discount_"+str(r["id"]))
            if checked != (r["id"] in picked):
                ss["mobile_discounts"]=list((set(picked)|{r["id"]}) if checked else (set(picked)-{r["id"]}));st.rerun()
        else: st.caption("방문객 할인: 확인 필요" if not (r.get("tariff") or {}).get("complete") else "등록된 할인 없음")
        st.caption(r["fee_note"])
        st.caption("전용·제휴: "+str(affiliation(r,dest["id"]) or ("없음 (가상 설정)" if demo else "확인 필요")))
        if https_url(r.get("source_url","")): st.link_button("요금·운영 정보 출처",r["source_url"])
    st.caption("초록: 목적지 · 주황: 주차장 / 실시간 잔여 자리 확인 불가")


if __name__ == "__main__":
    main()
