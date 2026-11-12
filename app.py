# 추가 설정: 카카오모빌리티 길찾기 API 사용 등록 필요.
# Secrets: KAKAO_MOBILITY_REST_API_KEY="키" (없으면 KAKAO_REST_API_KEY 사용)
# PARKING_CSV_URL="전국주차장정보표준데이터 CSV 직접 다운로드 HTTPS 주소"
# CSV 출처: https://www.data.go.kr/data/15012896/standard.do
# 일일주차권은 일일최대요금과 다르므로 상한으로 간주하지 않습니다.
# -*- coding: utf-8 -*-
"""
목적지 근처 주차장 · Streamlit 단일 화면 앱

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
import time as clock
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
    # 실명 참고 목적지는 이름/주소만 참고했습니다. 좌표와 주차 데이터는 전부 가상입니다.
    extra = [
        ("대둔산양촌한우타운", "충청남도 논산시 양촌면 인천리 330-5", "https://maps.app.goo.gl/ZtiQ6CNFTJhKQYQF9"),
        ("논산댁네", "충청남도 논산시 중앙로218번길 6", "https://share.google/18NbRJMzn8drm6zC0"),
        ("금암광장 앞 · 사용자 지정 장소", "충청남도 계룡시 금암동 161-3 (금암광장 앞)", ""),
        ("가상 · 금암가족식당", "가상 계룡지역 가족길 10", ""),
        ("가상 · 계룡숲카페", "가상 계룡지역 숲길 20", ""),
        ("가상 · 논산호수공원", "가상 논산지역 호수길 30", ""),
        ("가상 · 양촌한옥마을", "가상 양촌지역 한옥길 40", ""),
        ("가상 · 대둔산나들이정원", "가상 나들이지역 정원길 50", ""),
        ("가상 · 어린이과학놀이터", "가상 체험지역 과학길 60", ""),
        ("가상 · 주말전통시장", "가상 시장지역 장터길 70", ""),
        ("가상 · 강변빵집", "가상 강변지역 빵집길 80", ""),
        ("가상 · 가족문화센터", "가상 문화지역 문화길 90", "")]
    for index,(name,address,source) in enumerate(extra):
        did=f"demo-extra-{index}"
        # 격리된 시연 좌표: 실제 목적지 위치로 해석하거나 길찾기에 사용하지 않습니다.
        lat,lon=36.0+index*.025,127.0
        destinations.append({"id":did,"name":"[가상 시연] "+name,"address":address+" · 지도 위치는 가상", "lat":lat,"lon":lon,"reference_url":source})
        for j,(kind,base,step,cap,offset) in enumerate([
            ("전용",1500,500,15000,.0007),
            ("주변",500,200,7000,.0025),
            ("제휴",1000,300,10000,.0015),
            ("야간",300,100,5000,.0035)]):
            lots.append({"id":f"{did}-p{j}","name":f"가상 · {name.replace('가상 · ', '')} {kind}주차장",
                "address":"가상 주차장 주소 · 실제 시설 아님", "lat":lat+offset,"lon":lon+offset,
                "hours":hours("18:00","23:00") if kind=="야간" else hours("00:00","24:00"),
                "tariff":fee(base,step,cap,ds if kind in ("전용","제휴") else None),
                "affiliations":[{"destination_id":did,"kind":kind}] if kind in ("전용","제휴") else []})
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
    st.success(f"💰 {price}　|　📍 {r['distance']:,}m")
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



@st.cache_data(ttl=3600, show_spinner=False)
def public_parking(raw):
    import io
    frame=None
    for enc in ("utf-8-sig","cp949"):
        try:
            frame=pd.read_csv(io.BytesIO(raw),encoding=enc,dtype=str).fillna("")
            break
        except UnicodeDecodeError: continue
    if frame is None or not {"위도","경도","주차장명"}.issubset(frame.columns):
        raise ValueError("전국주차장정보표준데이터 CSV가 필요합니다.")
    result=[]
    for idx,row in frame.iterrows():
        try:
            lat,lon=float(row["위도"]),float(row["경도"])
            if not (33<=lat<=39 and 124<=lon<=132): continue
        except (ValueError,TypeError): continue
        info=str(row.get("요금정보",""))
        label="무료" if info=="무료" else ""
        fields=[row.get(k,"") for k in ("주차기본시간","주차기본요금","추가단위시간","추가단위요금")]
        estimate=None
        if info=="무료": estimate=0
        elif all(str(v).strip() for v in fields):
            try:
                bt,bf,at,af=map(float,fields)
                if bt>0 and at>0 and bf>=0 and af>=0:
                    estimate=int(math.ceil(bf+math.ceil(max(0,120-bt)/at)*af))
                    label=f"기본 {bt:g}분 {bf:g}원 · 추가 {at:g}분 {af:g}원"
            except (ValueError,OverflowError): pass
        result.append({"id":"public-"+str(row.get("주차장관리번호",idx)),"name":row["주차장명"],"address":row.get("소재지도로명주소","") or row.get("소재지지번주소",""),"lat":lat,"lon":lon,"public_fee":label,"public_estimate":estimate,"public_note":row.get("특기사항",""),"verified_on":row.get("데이터기준일자",""),"source_url":"https://www.data.go.kr/data/15012896/standard.do","affiliations":[]})
    return result

@st.cache_data(ttl=300, show_spinner=False)
def driving_route(api_key, origin_lat, origin_lon, lat, lon):
    response=requests.get("https://apis-navi.kakaomobility.com/v1/directions",headers={"Authorization":"KakaoAK "+api_key},params={"origin":f"{origin_lon},{origin_lat}","destination":f"{lon},{lat}","priority":"RECOMMEND"},timeout=12)
    response.raise_for_status()
    routes=response.json().get("routes",[])
    if not routes or routes[0].get("result_code")!=0: raise ValueError("자동차 경로 없음")
    summary=routes[0]["summary"]
    return int(summary["distance"]),int(summary["duration"])

def typo_candidates(query, learned=()):
    """제한된 장소명 목록에서만 후보 제안. 임의 장소 생성/자동 확정 금지."""
    import unicodedata
    from difflib import SequenceMatcher
    known=["성심당","대둔산양촌한우타운","논산댁네","금암광장","계룡산","동학사","갑사","국립중앙박물관","국립세종수목원","대전오월드","한밭수목원","엑스포과학공원","대전신세계","롯데월드","에버랜드","경복궁","서울숲","북촌한옥마을","전주한옥마을","순천만국가정원","해운대해수욕장","광안리해수욕장","불국사","첨성대","독립기념관","현충사","공산성","부여정림사지"]
    def normalized(t):
        return unicodedata.normalize("NFD","".join(str(t).lower().split()))
    words=query.strip().split()
    variants=[(query.strip(),"")]
    if len(words)>1:
        variants.append((words[-1]," ".join(words[:-1])+" "))
    scored={}
    for name in dict.fromkeys(known+list(learned)):
        for text,prefix in variants:
            a,b=normalized(text),normalized(name)
            if not a or a==b or abs(len(a)-len(b))>6: continue
            score=SequenceMatcher(None,a,b).ratio()
            if score>=.76:
                candidate=prefix+name
                scored[candidate]=max(score,scored.get(candidate,0))
    return sorted(scored,key=lambda k:(-scored[k],k))[:3]


def main():
    st.set_page_config(page_title="목적지 근처 주차장", page_icon="🅿️", layout="centered")
    # 첫 접속 세션에만 약 3초 표시. 검색/화면 이동 시 재생하지 않습니다.
    if not st.session_state.get("intro_seen",False):
        splash=st.empty()
        # HTML을 한 줄로 전달해 들여쓰기가 코드 블록으로 해석되지 않게 합니다.
        splash_html = (
            '<style>.parking-intro{position:fixed;inset:0;z-index:999999;'
            'background:#f7faf8;display:flex;flex-direction:column;align-items:center;'
            'justify-content:center;text-align:center;padding:24px;box-sizing:border-box;}'
            '.parking-intro-icon{font-size:88px;line-height:1.2;margin-bottom:22px;}'
            '.parking-intro-title{font-family:sans-serif;font-size:27px;font-weight:700;'
            'color:#176B55;line-height:1.5;word-break:keep-all;}</style>'
            '<div class="parking-intro"><div class="parking-intro-icon">🅿️</div>'
            '<div class="parking-intro-title">근처 주차장 찾기</div></div>'
        )
        splash.markdown(splash_html,unsafe_allow_html=True)
        clock.sleep(3)
        st.session_state["intro_seen"]=True
        splash.empty()

    st.markdown("""<style>
    .block-container{max-width:620px;padding:5rem 1rem 2rem!important}
    [data-testid="stMain"]{overflow-y:auto!important}
    h1{overflow:visible!important;line-height:1.4!important}
    @media(max-width:600px){.block-container{padding-top:4.5rem!important}}
    h1{font-size:1.6rem!important}h2,h3{font-size:1.2rem!important}
    button{min-height:46px!important;white-space:normal!important}
    [data-testid="stVerticalBlock"]{gap:.65rem}
    [data-testid="stBaseButton-primary"]{background:#176B55;border-color:#176B55}
    p{overflow-wrap:anywhere}
    .st-key-criteria_tiles [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.5rem!important}
    .st-key-criteria_tiles [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important;width:0!important}
    .st-key-criteria_tiles button{width:100%!important;aspect-ratio:1 / 1;min-height:0!important;height:auto!important;border-radius:14px!important;padding:.35rem!important}
    .st-key-criteria_tiles button p{font-size:clamp(.8rem,3.3vw,1.05rem)!important;word-break:keep-all;line-height:1.4}

    </style>""",unsafe_allow_html=True)
    def go_search_home():
        st.session_state["screen"]="search"
    st.markdown('<style>.st-key-home_title button{background:transparent!important;border:0!important;padding:0!important;text-align:left!important;box-shadow:none!important;}.st-key-home_title button p{font-size:clamp(1.3rem,5.5vw,1.9rem)!important;font-weight:750!important;line-height:1.5!important;color:var(--text-color)!important;}</style>',unsafe_allow_html=True)
    with st.container(key="home_title"):
        st.button("🅿️ 목적지 근처 주차장",key="home_title_button",on_click=go_search_home,help="검색 화면으로 돌아가기")
    key=str(secret("KAKAO_REST_API_KEY", "")).strip()
    ss=st.session_state
    # 위치는 동의 후에만 요청하며 세션 메모리에만 보관합니다.
    if not ss.get("location_prompt_done",False):
        @st.dialog("📍 현재 위치 사용",dismissible=False)
        def location_notice():
            st.write("내 위치에서 주차장까지 자동차 거리와 시간을 알려드려요.")
            if not ss.get("location_request_started",False):
                if st.button("📍 현재 위치 확인하기",type="primary",use_container_width=True):
                    ss["location_request_started"]=True
                    st.rerun()
            else:
                try:
                    from streamlit_js_eval import get_geolocation
                    st.caption("현재 위치를 확인하고 있어요…")
                    # 브라우저 권한 요청은 기존 위치 구성요소가 직접 수행합니다.
                    location=get_geolocation(component_key="parking_location_request")
                    if location and isinstance(location.get("coords"),dict):
                        location=location["coords"]
                    if location and location.get("latitude") is not None and location.get("longitude") is not None:
                        lat,lon=float(location["latitude"]),float(location["longitude"])
                        if not (-90<=lat<=90 and -180<=lon<=180):
                            st.error("올바른 위치를 받지 못했습니다.")
                        else:
                            ss["user_location"]={"lat":lat,"lon":lon}
                            ss["location_prompt_done"]=True
                            st.rerun()
                    elif location and location.get("error"):
                        st.warning("위치 권한이 차단됐거나 위치를 확인하지 못했어요. 브라우저의 위치 권한을 확인해 주세요.")
                        if st.button("다시 시도",use_container_width=True):
                            ss["location_request_started"]=False
                            st.rerun()
                except ImportError:
                    st.error("위치 기능 설치가 필요합니다. 최신 requirements.txt를 적용해 주세요.")
            st.caption("위치는 파일에 저장하지 않습니다.")
        location_notice()
        st.stop()
    ss.setdefault("screen", "search")
    screen=ss["screen"]
    if screen=="search":
        demo=False
        mode="실제 장소"
        if ss.get("mobile_mode")!=mode:
            ss["mobile_mode"]=mode
            ss.pop("mobile_results",None)
            ss.pop("mobile_destination",None)
        # 안내 동의는 이 브라우저의 현재 Streamlit 세션에서 한 번만 받습니다.
        if not ss.get("mic_notice_accepted",False):
            if st.button("🎤 말로 장소 입력",use_container_width=True):
                @st.dialog("마이크 사용 안내")
                def microphone_notice():
                    st.write("마이크를 허용하고 장소를 말해 주세요. 음성이 브라우저 음성인식 서비스로 전송될 수 있습니다.")
                    st.caption("HTTPS와 지원 브라우저가 필요합니다. 인식되지 않으면 직접 입력할 수 있습니다.")
                    if st.button("확인 · 음성 입력 켜기",type="primary",use_container_width=True):
                        st.session_state["mic_notice_accepted"]=True
                        st.rerun()
                microphone_notice()
        else:
            try:
                from streamlit_mic_recorder import speech_to_text
            except ImportError:
                st.caption("음성 검색 설치 대기 중 · requirements.txt 교체 후 재배포해 주세요.")
            else:
                spoken=speech_to_text(language="ko-KR",start_prompt="🎤 말로 장소 입력",stop_prompt="⏹ 입력 마치기",just_once=True,use_container_width=True,key="parking_voice_search")
                if isinstance(spoken,str) and spoken.strip():
                    ss["mobile_query"]=spoken.strip()[:100]
        # 검색 기록은 사용자별 Streamlit 세션 메모리에만 보관합니다.
        ss.setdefault("recent_searches",[])
        def restore_recent(text):
            ss["mobile_query"]=text
            ss["recent_search_pending"]=True
            ss.pop("mobile_destination",None)
        if ss["recent_searches"]:
            with st.expander("🕘 최근 검색"):
                for index,text in enumerate(ss["recent_searches"]):
                    st.button(text,key="recent_search_"+str(index),use_container_width=True,
                              on_click=restore_recent,args=(text,))
                if st.button("기록 전체 삭제",key="clear_recent_searches"):
                    ss["recent_searches"]=[]
                    st.rerun()
        with st.form("mobile_search"):
            query=st.text_input("어디로 가세요?",placeholder="장소명 또는 지역 + 장소명",max_chars=100,key="mobile_query")
            submit=st.form_submit_button("장소 검색",type="primary",use_container_width=True)
        if submit or ss.pop("recent_search_pending",False):
            if query.strip() and key:
                term=query.strip()
                ss["recent_searches"]=[term]+[t for t in ss["recent_searches"] if t!=term]
                ss["recent_searches"]=ss["recent_searches"][:5]
            ss.pop("mobile_destination",None)
            ss["typo_suggestions"]=[]
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
                    learned=ss.setdefault("known_place_names",[])
                    learned.extend(d["place_name"] for d in docs if d.get("place_name"))
                    ss["known_place_names"]=list(dict.fromkeys(learned))[-200:]
                    if not docs:
                        for candidate in typo_candidates(query,ss["known_place_names"]):
                            try:
                                verified,_=kakao_search(key,"keyword",{"query":candidate,"size":15})
                            except (requests.RequestException,ValueError,KeyError):
                                continue
                            if verified:
                                ss["typo_suggestions"].append((candidate,[place(d) for d in verified]))
                            if len(ss["typo_suggestions"])>=2: break

                except (requests.RequestException,ValueError,KeyError):
                    ss["mobile_results"]=[]
                    st.error("검색 연결에 실패했습니다. 키와 API 권한을 확인해 주세요.")
        if not ss.get("mobile_results") and ss.get("typo_suggestions"):
            st.info("혹시 이 검색어를 찾으셨나요?")
            def accept_correction(text,found):
                ss["recent_searches"]=([text]+[t for t in ss.get("recent_searches",[]) if t!=text])[:5]
                ss["mobile_query"]=text
                ss["mobile_results"]=found
                ss["typo_suggestions"]=[]
                ss.pop("mobile_destination",None)
            for i,(candidate,found) in enumerate(ss["typo_suggestions"]):
                st.button("🔎 "+candidate+" 검색",key="typo_pick_"+str(i),
                          use_container_width=True,on_click=accept_correction,args=(candidate,found))
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
    if not demo:
        csv_url=str(secret("PARKING_CSV_URL","")).strip()
        if "public_parking" not in ss:
            try:
                # 저장소의 app.py 옆 CSV가 있으면 외부 다운로드 없이 사용합니다.
                from pathlib import Path
                folder=Path(__file__).resolve().parent
                local=folder/"parking.csv"
                candidates=[local] if local.exists() else sorted(folder.glob("*.csv"))
                if candidates:
                    raw=candidates[0].read_bytes()
                elif csv_url:
                    from urllib.parse import urlsplit, urlunsplit
                    parts=urlsplit(csv_url)
                    if parts.hostname=="github.com" and "/blob/" in parts.path:
                        csv_url=urlunsplit(("https","raw.githubusercontent.com",parts.path.replace("/blob/","/",1),"",""))
                    data_response=requests.get(csv_url,timeout=(5,30))
                    data_response.raise_for_status()
                    raw=data_response.content
                    if raw.lstrip()[:50].lower().startswith((b"<!doctype html",b"<html")):
                        raise ValueError("CSV 대신 웹페이지가 반환됐습니다. GitHub 원본 파일 주소를 확인하세요.")
                else:
                    raw=None
                if raw is not None:
                    parsed=public_parking(raw)
                    if not parsed: raise ValueError("좌표가 있는 주차장 행을 찾지 못했습니다.")
                    ss["public_parking"]=parsed
            except requests.HTTPError as exc:
                code=exc.response.status_code if exc.response is not None else "오류"
                st.warning(f"공공 CSV 다운로드 실패(HTTP {code}). 저장소에 parking.csv를 올리면 주소 설정 없이 연결됩니다.")
            except requests.RequestException:
                st.warning("공공 CSV 연결이 지연되거나 차단됐습니다. 저장소에 parking.csv를 올려 주세요.")
            except (ValueError,KeyError,OSError):
                st.warning("공공 CSV의 형식·인코딩·필수 열을 확인하지 못했습니다. 원본 CSV를 첨부해 주시면 확인할 수 있습니다.")
        public=[r for r in ss.get("public_parking",[]) if distance_m(dest,r)<=radius]
        # 공식 데이터는 독립된 주차장으로 표시. 이름만으로 카카오 결과에 요금을 붙이지 않음.
        lots=public+[r for r in lots if not any(r["name"]==v["name"] and distance_m(r,v)<30 for v in public)]
        if not ss.get("public_parking"): st.caption("공공 CSV 연결 전입니다. 카카오 검색만으로는 요금을 제공하지 않습니다.")

    picked=ss.get("mobile_discounts",[])
    rows=[]
    for lot in lots:
        cost,note=estimate_fee(lot.get("tariff"),start,end,lot["id"] in picked)
        rows.append(dict(lot,cost=cost,fee_note=note,distance=distance_m(ss.get("user_location") if not demo and ss.get("user_location") else dest,lot),status=operation_status(lot.get("hours"),start,end),hours_label=hours_text(lot.get("hours"),start,end)))
    if not demo:
        origin=ss.get("user_location")
        if not origin:
            ss["location_prompt_done"]=False
            st.rerun()
        route_key=str(secret("KAKAO_MOBILITY_REST_API_KEY",key)).strip()
        routed=[]
        failed=0
        slow_notice=st.empty()
        with slow_notice.container():
            st.markdown(
                '<style>@keyframes parkingRetryReveal{to{visibility:visible;}}'
                '.st-key-route_retry{visibility:hidden;animation:parkingRetryReveal 0s 12s forwards;}'
                '.st-key-route_retry button{background:transparent!important;border:0!important;'
                'color:#1769e0!important;text-decoration:underline;min-height:44px!important;}'
                '</style>',unsafe_allow_html=True)
            with st.container(key="route_retry"):
                st.caption("로딩이 길어지고 있어요. 현재 화면에서 다시 시도할 수 있습니다.")
                if st.button("눌러서 새로고침",key="retry_current_route"):
                    # 브라우저 재접속 없이 세션의 화면·목적지·위치를 유지합니다.
                    st.rerun()
        with st.spinner("자동차 경로를 확인하고 있어요…"):
            for r in sorted(rows,key=lambda r:r["distance"])[:15]:
                try:
                    r["distance"],r["drive_seconds"]=driving_route(route_key,origin["lat"],origin["lon"],r["lat"],r["lon"])
                    if "public_estimate" in r:
                        r["cost"]=r["public_estimate"]
                        r["fee_note"]="기본·추가요금으로 계산한 2시간 참고금액. 일일상한·무료시간·할인·특기사항은 미반영."
                    routed.append(r)
                except (requests.RequestException,ValueError,KeyError): failed+=1
        slow_notice.empty()
        rows=routed
        if failed: st.caption(f"자동차 경로를 확인하지 못한 {failed}곳 제외 · 직선거리로 대체하지 않음")
        if not rows:
            st.warning("자동차 경로 조회 실패: 위치 권한과 카카오모빌리티 길찾기 API 설정을 확인하세요.")
            return
    if ss["screen"]=="compare":
        st.caption("추천 기준")
        criteria=["요금 우선","거리 우선","요금·거리 균형"]
        ss.setdefault("mobile_criterion","요금 우선")
        # 세 버튼을 모바일에서도 한 줄로 유지합니다.
        with st.container(key="criteria_tiles"):
            columns=st.columns(3,gap="small")
            for column,label,icon in zip(columns,criteria,["₩","↔","⚖"]):
                with column:
                    if st.button(icon+" " +label,key="criterion_tile_"+label,
                                 type="primary" if ss["mobile_criterion"]==label else "secondary",
                                 use_container_width=True):
                        ss["mobile_criterion"]=label
                        st.rerun()
        criterion=ss["mobile_criterion"]
        st.info("예상요금은 2시간 기준 · 목적지 주변 1km")
        summary={"요금 우선":"낮은 요금순 · 동률이면 가까운 곳", "거리 우선":"가까운 순 · 요금 미확인 포함", "요금·거리 균형":"요금 50% + 거리 50% 균형"}[criterion]
        ranked=rank_lots(rows,criterion)[:3]
        fallback = not ranked
        if fallback:
            # 운영 여부 미확인 후보도 선택 기준대로 비교하되 영업 중으로 표시하지 않습니다.
            candidates=[dict(r,status="open",actual_status=r["status"]) for r in rows if r["status"]!="closed"]
            ranked=rank_lots(candidates,criterion)[:3]
            if ranked:
                st.warning("운영 여부 미확인 · 선택 기준으로 정렬한 검색 결과입니다.")
            elif candidates:
                st.warning("비교할 요금 정보가 없어 가까운 순으로 표시합니다.")
                ranked=sorted(candidates,key=lambda r:r["distance"])[:3]
            for r in ranked:
                r["status"]=r.pop("actual_status", "unknown")
        st.caption({"요금 우선":"요금이 낮은 순 · 동률이면 가까운 순", "거리 우선":"현재 위치에서 가까운 순", "요금·거리 균형":"요금 50% + 거리 50%로 비교"}[criterion])
        for n,r in enumerate(ranked,1):
            price=f"{r['cost']:,}원 예상" if r['cost'] is not None else "요금 미확인"
            kind=affiliation(r,dest["id"])
            with st.container(border=True):
                st.markdown(f"**{n}. {r['name']}**"+(f" · {kind}" if kind else ""))
                st.success(f"💰 {price}　|　📍 {r['distance']:,}m")
                if not demo:
                    st.caption(f"약 {math.ceil(r.get('drive_seconds',0)/60)}분")
                discount=(r.get("tariff") or {}).get("discount")
                if isinstance(discount,dict):
                    discounted,_=estimate_fee(r.get("tariff"),start,end,True)
                    if discounted is not None:
                        st.caption(f"🎁 조건 충족 시 {discounted:,}원 · {discount.get('label','조건 확인 필요')}")
                if st.button("지도·상세 →",key="detail_"+str(r["id"]),use_container_width=True):
                    ss["selected_lot"]=r["id"];ss["screen"]="detail";st.rerun()
        if not ranked: st.info("현재 조건의 후보가 없습니다. 다른 장소를 검색해 주세요.")
        st.caption("참고요금: 할인·무료시간·일일상한 미반영 · 빈자리 확인 불가")
        return
    if st.button("← 비교 결과",key="back_compare"):
        ss["screen"]="compare";st.rerun()
    choices={r["id"]:r for r in rows}
    if not choices:
        st.info("조회된 주차장이 없습니다.");return
    initial=ss.get("selected_lot")
    options=list(choices)
    # 비교 카드에서 선택한 주차장만 상세 표시합니다.
    selected_id=initial if initial in choices else options[0]
    r=choices[selected_id]
    price=f"{r['cost']:,}원 예상" if r['cost'] is not None else "요금 확인 필요"
    st.write(f"**{price} · {'가상 직선' if demo else '거리'} {r['distance']:,}m**")
    st.caption(r["address"])
    st.caption("가상 직선거리" if demo else f"현재 위치에서 약 {math.ceil(r.get('drive_seconds',0)/60)}분")
    import pydeck as pdk
    markers=[{"lat":dest["lat"],"lon":dest["lon"],"label":"목적지", "color":[23,107,85]},
             {"lat":r["lat"],"lon":r["lon"],"label":"주차장", "color":[232,116,57]}]
    if not demo and ss.get("user_location"):
        markers.append(dict(ss["user_location"],label="출발",color=[40,90,190]))
    points=pd.DataFrame(markers)
    from pydeck.data_utils import compute_view
    view=compute_view(points[["lon","lat"]].values.tolist())
    view.zoom=min(view.zoom,16)
    st.pydeck_chart(pdk.Deck(initial_view_state=view,layers=[
        pdk.Layer("ScatterplotLayer",data=points,get_position="[lon, lat]",get_fill_color="color",get_radius=12,radius_min_pixels=7,pickable=True),
        pdk.Layer("TextLayer",data=points,get_position="[lon, lat]",get_text="label",get_color="color",get_size=18,get_pixel_offset=[0,-25],get_text_anchor="middle",get_alignment_baseline="bottom",get_background_color=[255,255,255,235],background=True,font_family="Arial, sans-serif",character_set=list("목적지주차장출발 "))
    ],tooltip={"text":"{label}"},map_style="light",height=260),use_container_width=True)
    st.caption("🟢 목적지 · 🟠 주차장" + (" · 🔵 현재 위치(출발)" if not demo and ss.get("user_location") else ""))
    if not demo:
        url=f"https://map.kakao.com/link/to/{quote(r['name'],safe='')},{r['lat']},{r['lon']}"
        st.link_button("카카오맵 길찾기",url,type="primary",use_container_width=True)
    else: st.caption("가상 위치 · 길찾기는 실제 모드에서 제공")
    # 확인된 정보만 펼침 없이 표시. 정보 미제공은 한 번만 안내.
    missing=[]
    if r.get("hours_label") and "확인 필요" not in r["hours_label"]:
        st.write("운영시간: "+r["hours_label"])
    else: missing.append("운영시간")
    if r["status"]=="closed": st.warning("선택한 이용시간은 운영시간 밖입니다.")
    tariff=r.get("tariff") or {}
    if r.get("public_fee"):
        st.write("공공 요금표: "+r["public_fee"])
        st.warning("참고요금 · 할인·무료시간·일일상한 미반영")
        if r.get("public_note"): st.caption("특기사항: "+r["public_note"])
        st.caption("데이터 기준일: "+str(r.get("verified_on", "미제공")))
    if tariff.get("complete"):
        st.write(tariff_text(tariff))
    elif not r.get("public_fee"): missing.append("요금")
    discount=tariff.get("discount")
    if isinstance(discount,dict):
        st.info("🎁 "+str(discount.get("label","방문객 할인 조건 확인 필요")))
    kind=affiliation(r,dest["id"])
    if kind: st.caption("목적지와의 관계: "+str(kind))
    if missing: st.caption(" · ".join(missing)+" 정보 미제공")
    if https_url(r.get("source_url","")): st.link_button("공식 정보",r["source_url"])
    st.caption("실시간 잔여 자리 확인 불가")


if __name__ == "__main__":
    main()
