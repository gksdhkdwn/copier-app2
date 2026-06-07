import streamlit as st
import re
import urllib.parse
import json
import os
from collections import OrderedDict

# 1. 페이지 기본 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

SETTINGS_FILE = "message_settings.json"

# 2. 안내 문구 기본값 (신규 기종 및 변경 문구 반영)
txt_sindo = "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다."
txt_ecosys = "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다."
txt_305 = "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다."
txt_5473 = "사용량확인차 문자남겼습니다 확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다."
txt_apeos = "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다."
txt_5700 = "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4장 중에 3 페이지만 문자 보냅니다.)"
txt_l5100 = "+ 누르면 Machine info 누르고 ok → Print settings ok 누른 후 go(시작버튼) 누르셔서 나오는 4장 중 3번째 장만 문자로 부탁드립니다."
txt_ricoh = "사용자도구 클릭 → 카운터 클릭 → 카운터 목록인쇄클릭 (인쇄물 출력 후 발송 부탁드립니다.)"
txt_5005 = "사양설정 > 리포트 > 기능설정리스트 확인 후 문자로 부탁드립니다."

# [신규 및 수정 문구 적용]
txt_sam_mx6 = "홈 화면에서 우측으로 넘기시고, 보고서-구성/상태 페이지-사용페이지-프린트모양 인쇄버튼 누르고 사진찍어 보내주시면 됩니다."
txt_sam_keypad = "복사기 숫자 키패드 위 카운터 클릭 후 화면에서 인쇄 눌러주시고 나온 출력물 사진찍어 보내주시면 됩니다."
txt_sam_xk47 = "설정 → 왼쪽 쭉 내리다보면 리포트 누름 → 오른쪽 사용량 정보 클릭하여 확인 후 문자로 부탁드립니다."
txt_kyocera_m2101 = "화면 맨 밑 가운데에 점3개(***)를 눌러주세요. 화살표 아래로한번-카운터 확인-기본설정-인쇄페이지 수-화살표 아래로한번 내리신 후 사진찍어 보내주시면 됩니다. (시리얼넘버도 필요하면 그 위에 상태페이지 인쇄 누르기)"
txt_hp_common = "메인화면 상단 스크롤 내려주시고 톱니바퀴 아이콘 눌러주세요. 목록 하단에 보고서 눌러주시고 상태보고서 찾아서 인쇄하신 후 사진찍어 보내주시면 됩니다."
txt_lexmark_410 = "집모양-스패너모양-보고서-장치통계-장치통계 페이지2번 사진찍어서 보내주시면 됩니다."
txt_default = "기기 화면의 카운터 메뉴에서 사용량 확인 후 사진 한 장만 문자나 카톡으로 발송 부탁드립니다."

DEFAULT_FORMATS = {
    "N500": txt_sindo, "N501": txt_sindo, "N502": txt_sindo, "N600": txt_sindo, "N601": txt_sindo,
    "D320": txt_sindo, "D400": txt_sindo, "D410": txt_sindo, "D420": txt_sindo, "D450": txt_sindo,
    "D460": txt_sindo, "D470": txt_sindo, 
    "MA2100": txt_ecosys, "M5526": txt_ecosys, "M5521": txt_ecosys, "ECOSYS": txt_ecosys, 
    "M2101": txt_kyocera_m2101,  # 신규 교세라
    "305": txt_305, "5473": txt_5473, 
    "C2263": txt_apeos, "C2265": txt_apeos, "C2061": txt_apeos, "C3067": txt_apeos, "C2260": txt_apeos, 
    "C2270": txt_apeos, "C2275": txt_apeos, "C3375": txt_apeos, "C4475": txt_apeos, "C5575": txt_apeos, 
    "C2271": txt_apeos, "C2273": txt_apeos, "C3371": txt_apeos, "C3373": txt_apeos, "C3070": txt_apeos, 
    "C3570": txt_apeos, "C4570": txt_apeos, "C5570": txt_apeos, "C7070": txt_apeos, "Apeos": txt_apeos, 
    "5700": txt_5700, "L5100": txt_l5100,
    "2554": txt_ricoh, "C3003": txt_ricoh, "C4504": txt_ricoh, "5005": txt_5005, 
    "Mx6": txt_sam_mx6, "X3220NR": txt_sam_keypad, "K3250": txt_sam_keypad, "X-9201": txt_sam_keypad, # 신규 삼성 그룹1, 2
    "X4-시리즈": txt_sam_xk47, "K4-시리즈": txt_sam_xk47, "X7-시리즈": txt_sam_xk47, "K7-시리즈": txt_sam_xk47, "SL-": txt_sam_xk47, # 삼성 그룹3
    "HP": txt_hp_common, "410": txt_lexmark_410, "Lexmark": txt_lexmark_410, # 신규 HP 및 렉스마크
    "기본 기종": txt_default
}

DEFAULT_TEMPLATES = {
    "single_greeting": (
        "안녕하세요 퍼스트 전산입니다.\n"
        "마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다.\n"
        "카운터 한장만 보내주시면 감사하겠습니다."
    ),
    "single_closing": "매번 번거롭게 해드려 죄송합니다.",
    "multi_greeting": (
        "안녕하세요 퍼스트 전산입니다.\n"
        "마감을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다.\n"
        "각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
    ),
    "multi_closing": "매번 번거롭게 해드려 죄송합니다.",
}

TITLE_LIST = [
    '회장', '부회장', '사장', '부사장', '대표이사', '대표', '전무이사', '전무',
    '상무이사', '상무', '본부장', '부서장', '실장', '팀장', '부장', '차장', '과장',
    '대리', '주임', '사원', '이사', '원장', '점장', '점주', '매니저', '소장', '계장',
    '담당자', '담당', '기사', '선생', '박사', '사모', '여사', '회계', '경리'
]
TITLE_RE = '(?:' + '|'.join(TITLE_LIST) + ')(?:님)?'
NAME_RE = r'[가-힣]{2,4}'
PHONE_RE = r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}'

NON_NAME_WORDS = {
    '분기마감', '매월마감', '매월방문', '매주방문', '매주마감', '격주방문',
    '격주마감', '월말마감', '월말방문', '분기', '마감', '방문', '매월',
    '매주', '격주', '월말', '계약', '결제', '영업', '관리', '인쇄', '출력', '점검', '신규',
    '갱신', '해지', '카운터', '문자', '자료', '발송', '확인', '안내', '미수', '부착', '미부착', 
    '유지보수', '유지', '보수', '서비스', '오른쪽', '왼쪽', '비서실', '회의실', '사무실', '관리실', 
    '영업실', '본사', '지사', '지점', '매장', '연락처', '전화', '핸드폰', '전화번호', '대표번호', 
    '연락', '문의', '담당자', '복합기', '키맨', '경영', '재무', '인사', '총무', '구매', '생산', 
    '품질', '기술', '연구', '개발', '기획', '전산', '시설', '경비',
}

def _find_name_after(after):
    stripped = re.sub(r'^[\s:\-/,·()]+', '', after)
    for length in (3, 2, 4):
        if len(stripped) >= length:
            cand = stripped[:length]
            if re.fullmatch(rf'[가-힣]{{{length}}}', cand):
                if length < len(stripped) and re.match(r'[가-힣]', stripped[length]):
                    continue
                if cand not in NON_NAME_WORDS:
                    return cand
    return None

def _find_name_before(before):
    stripped = re.sub(r'[\s:\-/,·()]+$', '', before)
    for length in (3, 2, 4):
        if len(stripped) >= length:
            cand = stripped[-length:]
            if re.fullmatch(rf'[가-힣]{{{length}}}', cand):
                if length < len(stripped) and re.match(r'[가-힣]', stripped[-length-1]):
                    continue
                if cand not in NON_NAME_WORDS:
                    return cand
    return None

def load_settings():
    machines = DEFAULT_FORMATS.copy()
    templates = DEFAULT_TEMPLATES.copy()
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict) and ("machines" in loaded or "templates" in loaded):
                if isinstance(loaded.get("machines"), dict):
                    machines.update(loaded["machines"])
                if isinstance(loaded.get("templates"), dict):
                    templates.update(loaded["templates"])
            elif isinstance(loaded, dict):
                machines.update(loaded)
    except Exception:
        pass
    return machines, templates

def save_settings(machines, templates):
    try:
        data = {"machines": machines, "templates": templates}
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"설정 저장 실패: {e}")
        return False

def normalize_company_name(name):
    if not name:
        return name
    name = re.split(r'[/／]', name, maxsplit=1)[0]
    schedule_keywords = ['매월마감', '매월방문', '매주방문', '매주마감', '격주방문', '격주마감', '월말마감', '월말방문']
    earliest = len(name)
    for kw in schedule_keywords:
        idx = name.find(kw)
        if 0 <= idx < earliest:
            earliest = idx
    if earliest < len(name):
        name = name[:earliest]
    name = re.sub(r'[\s·,]+$', '', name).strip()
    return name

def extract_contacts(block):
    results = []
    phone_matches = list(re.finditer(PHONE_RE, block))
    seen = set()
    
    for idx, m in enumerate(phone_matches):
        phone_raw = m.group(0)
        clean = re.sub(r'[^0-9]', '', phone_raw)
        if clean in seen:
            continue
        seen.add(clean)
        
        before_start = phone_matches[idx-1].end() if idx > 0 else max(0, m.start() - 60)
        before = block[before_start:m.start()]
        after_end = phone_matches[idx+1].start() if idx + 1 < len(phone_matches) else min(len(block), m.end() + 40)
        after = block[m.end():after_end]
        
        label = ""
        ma = re.search(rf'^\s*[:\-\s/,·()]*\s*({NAME_RE})\s*({TITLE_RE})', after)
        if ma and ma.group(1) not in NON_NAME_WORDS:
            label = f"{ma.group(1)} {ma.group(2)}"
        if not label:
            ma = re.search(rf'(?:^|[\s/,:·\-()])({NAME_RE})\s*({TITLE_RE})\s*[:\-\s/()]*$', before)
            if ma and ma.group(1) not in NON_NAME_WORDS:
                label = f"{ma.group(1)} {ma.group(2)}"
        if not label:
            ma = re.search(rf'^\s*[:\-\s/,·()]*\s*({TITLE_RE})\s+({NAME_RE})', after)
            if ma and ma.group(2) not in NON_NAME_WORDS:
                label = f"{ma.group(2)} {ma.group(1)}"
        if not label:
            ma = re.search(rf'({TITLE_RE})\s+({NAME_RE})\s*[:\-\s/()]*$', before)
            if ma and ma.group(2) not in NON_NAME_WORDS:
                label = f"{ma.group(2)} {ma.group(1)}"
        if not label:
            name = _find_name_after(after)
            if name: label = name
        if not label:
            name = _find_name_before(before)
            if name: label = name
        if not label:
            ma = re.search(rf'^\s*[:\-\s/,·()]*\s*({TITLE_RE})', after)
            if ma: label = ma.group(1)
        if not label:
            ma = re.search(rf'(?:^|[\s/,:·\-()])({TITLE_RE})\s*[:\-\s/()]*$', before)
            if ma: label = ma.group(1)
        
        results.append({"phone": clean, "label": label})
    return results

def build_message(machines_list, machine_formats, templates):
    model_counts = OrderedDict()
    for m in machines_list:
        model_counts[m] = model_counts.get(m, 0) + 1
    
    unique_models = list(model_counts.keys())
    total_units = sum(model_counts.values())
    single_closing = templates.get("single_closing", DEFAULT_TEMPLATES["single_closing"])
    
    if len(unique_models) == 1 and total_units == 1:
        m = unique_models[0]
        how = machine_formats.get(m, txt_default)
        if "안녕하세요" in how or "사용량확인차" in how:
            return f"{how}\n(기종: {m})\n{single_closing}"
        greeting = templates.get("single_greeting", DEFAULT_TEMPLATES["single_greeting"])
        return f"{greeting}\n\n▶ 기종: {m}\n▶ 방법: {how}\n\n{single_closing}"
    
    raw_greeting = templates.get("multi_greeting", DEFAULT_TEMPLATES["multi_greeting"])
    greeting = raw_greeting.replace("{total}", str(total_units))
    closing = templates.get("multi_closing", DEFAULT_TEMPLATES["multi_closing"])
    
    lines = [greeting, ""]
    for idx, (m, count) in enumerate(model_counts.items(), 1):
        how = machine_formats.get(m, txt_default)
        suffix = f" ({count}대)" if count > 1 else ""
        lines.append(f"▶ 기종{idx}: {m}{suffix}")
        lines.append(f"    방법: {how}\n")
    lines.append(closing)
    return "\n".join(lines)


# 7. 세션 상태 초기화
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

if "custom_formats" not in st.session_state or "custom_templates" not in st.session_state:
    loaded_m, loaded_t = load_settings()
    st.session_state.custom_formats = loaded_m
    st.session_state.custom_templates = loaded_t

if "contact_labels" not in st.session_state:
    st.session_state.contact_labels = {}


# 8. 상단 헤더 + 네비게이션
nav_col1, nav_col2 = st.columns([7, 2])
with nav_col1:
    st.title("퍼스트전산 마감 도우미 📱")
with nav_col2:
    st.write("")
    st.write("")
    if st.session_state.current_page == "main":
        if st.button("⚙️ 문구 설정", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
    else:
        if st.button("🏠 메인으로", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()


# ============================================================
# 설정 페이지
# ============================================================
if st.session_state.current_page == "settings":
    st.caption("문자 양식과 기종별 안내 문구를 수정합니다. **저장하기**를 눌러야 다음 접속 시에도 유지됩니다.")
    edited_templates = st.session_state.custom_templates.copy()
    edited_machines = st.session_state.custom_formats.copy()
    
    with st.expander("📝 문자 양식 (인사말/마무리말) 편집", expanded=True):
        st.caption("💡 통합 발송 인사말에서 `{total}`을 쓰면 자동으로 기기 총 대수로 치환됩니다.")
        
        st.markdown("##### 📄 단일 기기 발송용")
        edited_templates["single_greeting"] = st.text_area(
            "인사말 (단일)",
            value=edited_templates.get("single_greeting", DEFAULT_TEMPLATES["single_greeting"]),
            height=120, key="edit_tpl_single_greeting"
        )
        edited_templates["single_closing"] = st.text_area(
            "마무리말 (단일)",
            value=edited_templates.get("single_closing", DEFAULT_TEMPLATES["single_closing"]),
            height=70, key="edit_tpl_single_closing"
        )
        
        st.markdown("---")
        st.markdown("##### 📚 여러 기기 통합 발송용")
        edited_templates["multi_greeting"] = st.text_area(
            "인사말 (통합) — `{total}` 사용 가능",
            value=edited_templates.get("multi_greeting", DEFAULT_TEMPLATES["multi_greeting"]),
            height=120, key="edit_tpl_multi_greeting"
        )
        edited_templates["multi_closing"] = st.text_area(
            "마무리말 (통합)",
            value=edited_templates.get("multi_closing", DEFAULT_TEMPLATES["multi_closing"]),
            height=70, key="edit_tpl_multi_closing"
        )
        
        st.markdown("---")
        st.markdown("##### 📱 실시간 미리보기")
        c1, c2 = st.columns(2)
        with c1:
            st.caption("🟢 단일 기기 예시 (D400)")
            try: p1 = build_message(["D400"], edited_machines, edited_templates)
            except Exception as e: p1 = f"⚠️ 양식 오류: {e}"
            st.code(p1, language=None)
        with c2:
            st.caption("🔵 통합 발송 예시 (D400 2대 + C2263)")
            try: p2 = build_message(["D400", "D400", "C2263"], edited_machines, edited_templates)
            except Exception as e: p2 = f"⚠️ 양식 오류: {e}"
            st.code(p2, language=None)
    
    machine_groups = {
        "📠 신도리코 (N/D 시리즈)": ["N500", "N501", "N502", "N600", "N601", "D320", "D400", "D410", "D420", "D450", "D460", "D470"],
        "📠 교세라 (ECOSYS / M2101)": ["MA2100", "M5526", "M5521", "ECOSYS", "M2101"],
        "📠 후지 Apeos (C 시리즈)": ["C2263", "C2265", "C2061", "C3067", "C2260", "C2270", "C2275", "C3375", "C4475", "C5575", "C2271", "C2273", "C3371", "C3373", "C3070", "C3570", "C4570", "C5570", "C7070", "Apeos"],
        "📠 리코": ["2554", "C3003", "C4504"],
        "📠 삼성 복합기 (신규 반영)": ["Mx6", "X3220NR", "K3250", "X-9201", "X4-시리즈", "K4-시리즈", "X7-시리즈", "K7-시리즈", "SL-"],
        "📠 HP / 렉스마크 / 브라더": ["HP", "410", "Lexmark", "5700", "L5100"],
        "📠 기타 단일 모델": ["305", "5473", "5005"],
        "📠 공통 / 기본값": ["기본 기종"]
    }
    
    st.markdown("### 🔧 기종별 안내 문구 (방법 설명)")
    for group_name, machines in machine_groups.items():
        with st.expander(group_name, expanded=False):
            for m in machines:
                if m in edited_machines:
                    edited_machines[m] = st.text_area(
                        f"**{m}**", value=edited_machines[m],
                        height=100, key=f"edit_setting_{m}"
                    )
    
    st.markdown("---")
    col_s1, col_s2, _ = st.columns([2, 2, 4])
    with col_s1:
        if st.button("💾 변경사항 저장", type="primary", use_container_width=True):
            st.session_state.custom_formats = edited_machines
            st.session_state.custom_templates = edited_templates
            if save_settings(edited_machines, edited_templates):
                st.success("✅ 저장 완료!")
    with col_s2:
        if st.button("🔄 기본값 복원", use_container_width=True):
            st.session_state.custom_formats = DEFAULT_FORMATS.copy()
            st.session_state.custom_templates = DEFAULT_TEMPLATES.copy()
            save_settings(DEFAULT_FORMATS, DEFAULT_TEMPLATES)
            for m in DEFAULT_FORMATS:
                k = f"edit_setting_{m}"
                if k in st.session_state: del st.session_state[k]
            for tk in ["edit_tpl_single_greeting", "edit_tpl_single_closing", "edit_tpl_multi_greeting", "edit_tpl_multi_closing"]:
                if tk in st.session_state: del st.session_state[tk]
            st.success("✅ 기본값으로 복원되었습니다.")
            st.rerun()


# ============================================================
# 메인 페이지
# ============================================================
else:
    st.caption("카톡 내용을 붙여넣으면 거래처별로 마감 문자를 생성합니다. **수신 연락처(번호)가 같으면 다른 이름의 업체도 자동 통합됩니다.**")
    
    st.markdown(
        """<style>
        div[data-testid="stTextArea"] textarea {
            overflow-y: hidden !important; height: auto !important;
            min-height: 200px !important; max-height: none !important;
        }</style>""",
        unsafe_allow_html=True
    )
    
    def clear_text_area():
        st.session_state["text_input_area"] = ""
        keys_to_delete = [k for k in list(st.session_state.keys())
                          if k.startswith(("final_nm_", "final_ph_", "final_mc_", "nm_", "ph_", "mc_"))]
        for k in keys_to_delete:
            del st.session_state[k]
        st.session_state.contact_labels = {}
    
    raw_text = st.text_area("카톡 내용 붙여넣기:", key="text_input_area")
    
    col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
    with col_btn1:
        st.button("🗑️ 입력 내용 전체 초기화", on_click=clear_text_area, use_container_width=True)
    with col_btn2:
        analyze_clicked = st.button("🔍 마감 문자 변환하기", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    if raw_text and raw_text.strip():
        split_pattern = r'((?<=\n)\d+(?:\s*,\s*)\d*[A-Z]*)|(^\d+(?:\s*,\s*)\d*[A-Z]*)'
        raw_parts = re.split(split_pattern, raw_text)
        
        blocks, current_block = [], ""
        for part in raw_parts:
            if part is None: continue
            if re.match(r'^\d+(?:\s*,\s*)', part.strip()):
                if current_block.strip(): blocks.append(current_block.strip())
                current_block = part
            else:
                current_block += part
        if current_block.strip(): blocks.append(current_block.strip())
        
        valid_blocks = [b.strip() for b in blocks if len(b.strip()) > 5 and re.match(r'^\d+(?:\s*,\s*)', b.strip())]
        if not valid_blocks:
            valid_blocks = [raw_text.strip()]
        
        machine_options = list(st.session_state.custom_formats.keys())
        exclude_machines = ["기본 기종", "X3220NR", "K3250", "X-9201", "Mx6", "X4-시리즈", "K4-시리즈", "X7-시리즈", "K7-시리즈", "SL-", "HP", "410", "Lexmark"]
        
        sms_data_list = []
        for i, block in enumerate(valid_blocks, 1):
            contacts = extract_contacts(block)
            clean_phones = [c["phone"] for c in contacts]
            
            for c in contacts:
                if c["label"] and c["phone"] not in st.session_state.contact_labels:
                    st.session_state.contact_labels[c["phone"]] = c["label"]
            
            detected_phone_str = ", ".join(clean_phones) if clean_phones else ""
            
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            detected_name = "거래처 확인 바람"
            if lines:
                first_line = lines[0]
                name_part = re.sub(r'^\d+(?:\s*,\s*)\d*[A-Za-z]*', '', first_line).strip()
                detected_name = name_part.split('매월마감')[0].strip() if name_part else first_line
            
            # [개선된 기종 매칭 알고리즘]
            matched_machine = "기본 기종"
            block_lower = block.lower()
            
            # 1. 삼성 계열 타겟팅
            if "mx6" in block_lower or "mx-6" in block_lower: matched_machine = "Mx6"
            elif "3250" in block_lower: matched_machine = "K3250"
            elif "3220" in block_lower: matched_machine = "X3220NR"
            elif "9201" in block_lower: matched_machine = "X-9201"
            elif re.search(r'[xk]-?4\d{3}', block_lower) or "x4" in block_lower or "k4" in block_lower: matched_machine = "X4-시리즈"
            elif re.search(r'[xk]-?7\d{3}', block_lower) or "x7" in block_lower or "k7" in block_lower: matched_machine = "X7-시리즈"
            elif "sl-" in block_lower: matched_machine = "SL-"
            # 2. 교세라 M2101 및 타 기종
            elif "m2101" in block_lower: matched_machine = "M2101"
            elif "ma2100" in block_lower: matched_machine = "MA2100"
            # 3. HP 및 렉스마크
            elif "hp" in block_lower: matched_machine = "HP"
            elif "410" in block_lower: matched_machine = "410"
            elif "lexmark" in block_lower or "렉스마크" in block_lower: matched_machine = "Lexmark"
            # 4. 리코 등 기타
            elif "mp-c2003" in block_lower or "c2003" in block_lower: matched_machine = "C3003"
            else:
                for k in machine_options:
                    if k not in exclude_machines and k.lower() in block_lower:
                        matched_machine = k
                        break
            
            if f"final_nm_{i}" not in st.session_state: st.session_state[f"final_nm_{i}"] = detected_name
            if f"final_ph_{i}" not in st.session_state: st.session_state[f"final_ph_{i}"] = detected_phone_str
            if f"final_mc_{i}" not in st.session_state: st.session_state[f"final_mc_{i}"] = matched_machine
            
            sms_data_list.append({"index": i, "block_raw": block})
        
        # 💡 [핵심 알고리즘 고도화]: 연락처(Phone) 기준 매칭 그룹화 
        # 전화번호 유무에 따라 그룹 생성 후, 중복 번호가 있는 업체들은 전부 하나로 묶음
        grouped = OrderedDict()  # group_id -> data
        phone_to_group_id = {}   # clean_phone -> group_id
        no_phone_counter = 0
        
        for s_info in sms_data_list:
            i = s_info["index"]
            cur_name = st.session_state.get(f"nm_{i}_first", st.session_state[f"final_nm_{i}"]).strip()
            cur_phone = st.session_state.get(f"ph_{i}_first", st.session_state[f"final_ph_{i}"])
            cur_machine = st.session_state.get(f"mc_{i}_first", st.session_state[f"final_mc_{i}"])
            
            # 현재 블록에서 깨끗한 숫자 번호 추출
            block_phones = []
            for p in re.split(r'[\s,]+', cur_phone):
                p_clean = re.sub(r'[^0-9]', '', p.strip())
                if p_clean: block_phones.append(p_clean)
            
            target_group_id = None
            # 기 추출된 번호 정보 중 겹치는 그룹이 있는지 조회
            for p_clean in block_phones:
                if p_clean in phone_to_group_id:
                    target_group_id = phone_to_group_id[p_clean]
                    break
            
            # 겹치는 번호가 없다면 업체명 정규화 텍스트 기반 혹은 임의 ID 발급
            if not target_group_id:
                if block_phones:
                    target_group_id = normalize_company_name(cur_name)
                else:
                    no_phone_counter += 1
                    target_group_id = f"NO_PHONE_GROUP_{no_phone_counter}"
            
            if target_group_id not in grouped:
                grouped[target_group_id] = {
                    "display_name": normalize_company_name(cur_name) if "NO_PHONE" not in str(target_group_id) else cur_name,
                    "phones": [],
                    "machines": [],
                    "indices": [],
                    "original_names": []
                }
            
            # 해당 그룹에 번호 연동 및 역방향 인덱스 맵 업데이트
            for p_clean in block_phones:
                if p_clean not in grouped[target_group_id]["phones"]:
                    grouped[target_group_id]["phones"].append(p_clean)
                phone_to_group_id[p_clean] = target_group_id
                
            grouped[target_group_id]["machines"].append(cur_machine)
            grouped[target_group_id]["indices"].append(i)
            
            if cur_name not in grouped[target_group_id]["original_names"]:
                grouped[target_group_id]["original_names"].append(cur_name)
        
        group_keys = list(grouped.keys())
        total_groups = len(group_keys)
        total_machines = sum(len(grouped[n]["machines"]) for n in group_keys)
        
        st.subheader(f"🚀 거래처별 발송 버튼 (총 {total_groups}개 업체 / {total_machines}대 기기)")
        st.info("💡 업체명(광운 왼쪽방, 광운 오른쪽방 등)이 달라도 수신 번호가 같으면 자동으로 한 곳에 묶여 발송됩니다.")
        
        def format_phone_with_name(phone):
            label = st.session_state.contact_labels.get(phone, "")
            formatted_p = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}" if len(phone) == 11 else phone
            if label: return f"👤 {label}  📞 {formatted_p}"
            return f"📞 {formatted_p}"
        
        @st.dialog("📱 문자 전송 대상 및 내용 확인")
        def show_send_popup(name, phones_list, msg, original_names=None):
            st.warning("⚠️ 수신 번호를 확인 후 하단의 최종 전송 버튼을 눌러주세요.")
            st.write(f"**대표 업체명:** {name}")
            
            if original_names and len(original_names) > 1:
                with st.expander(f"📍 통합된 상세 위치/지점 이름 ({len(original_names)}개)", expanded=True):
                    for n in original_names:
                        st.markdown(f"- {n}")
            
            selected_number = ""
            if len(phones_list) > 1:
                st.info(f"💡 번호 {len(phones_list)}개 발견. 발송할 담당자를 선택해 주세요:")
                selected_number = st.radio(
                    "수신 연락처 선택",
                    options=phones_list,
                    format_func=format_phone_with_name,
                    index=0
                )
            elif len(phones_list) == 1:
                p = phones_list[0]
                label = st.session_state.contact_labels.get(p, "")
                formatted_p = f"{p[:3]}-{p[3:7]}-{p[7:]}" if len(p) == 11 else p
                if label: st.write(f"**수신:** 👤 {label}  📞 {formatted_p}")
                else: st.write(f"**수신 번호:** 📞 {formatted_p}")
                selected_number = p
            else:
                st.error("❌ 등록된 수신 번호가 없습니다.")
            
            st.write("**📱 최종 전송 문구 미리보기:**")
            st.code(msg, language=None)
            
            if selected_number:
                target_num = re.sub(r'[^0-9]', '', selected_number)
                target_label = st.session_state.contact_labels.get(target_num, "")
                btn_text = f"✅ [{target_label}] 에게 전송" if target_label else f"✅ [{target_num}] 번호로 전송"
                st.markdown(
                    f'<a href="sms:{target_num}?body={urllib.parse.quote(msg)}" target="_self" '
                    f'style="display: block; width: 100%; text-align: center; padding: 0.8rem; '
                    f'background-color: #00CC66; color: white; text-decoration: none; '
                    f'border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 15px;">'
                    f'{btn_text}</a>',
                    unsafe_allow_html=True
                )
        
        btn_cols = st.columns(4)
        for g_idx, gkey in enumerate(group_keys):
            info = grouped[gkey]
            phones = info["phones"]
            machines = info["machines"]
            display_name = info["display_name"]
            original_names = info["original_names"]
            
            msg = build_message(machines, st.session_state.custom_formats, st.session_state.custom_templates)
            col_target = btn_cols[g_idx % 4]
            with col_target:
                if phones:
                    n_machines = len(machines)
                    n_phones = len(phones)
                    
                    if len(original_names) > 1:
                        btn_label = f"💬 {display_name} ({len(original_names)}개 처 통합됨)"
                    elif n_machines > 1:
                        btn_label = f"💬 {display_name} (기기 {n_machines}대 통합)"
                    else:
                        btn_label = f"💬 {display_name} 발송"
                    
                    if st.button(btn_label, key=f"group_btn_{g_idx}", use_container_width=True):
                        show_send_popup(display_name, phones, msg, original_names)
                else:
                    st.button(f"❌ {display_name} (번호없음)", disabled=True,
                              use_container_width=True, key=f"group_disabled_btn_{g_idx}")
        
        st.markdown("---")
        st.subheader("🔍 상세 정보 편집")
        
        for s_info in sms_data_list:
            i = s_info["index"]
            with st.container():
                col1, col2, col3 = st.columns([2, 1.5, 1])
                with col1:
                    st.text_input(f"업체명 ({i})", value=st.session_state[f"final_nm_{i}"], key=f"nm_{i}_first")
                with col2:
                    st.text_input(f"연락처 ({i}) - 쉼표로 구분", value=st.session_state[f"final_ph_{i}"], key=f"ph_{i}_first")
                    phones_in_block = re.split(r'[\s,]+', st.session_state.get(f"ph_{i}_first", ""))
                    labels_info = []
                    for p in phones_in_block:
                        p_clean = re.sub(r'[^0-9]', '', p.strip())
                        if p_clean:
                            lbl = st.session_state.contact_labels.get(p_clean, "")
                            if lbl:
                                fp = f"{p_clean[:3]}-{p_clean[3:7]}-{p_clean[7:]}" if len(p_clean) == 11 else p_clean
                                labels_info.append(f"{lbl}({fp})")
                    if labels_info: st.caption("👤 " + " · ".join(labels_info))
                with col3:
                    d_idx = machine_options.index(st.session_state[f"final_mc_{i}"]) if st.session_state[f"final_mc_{i}"] in machine_options else machine_options.index("기본 기종")
                    st.selectbox(f"기종 ({i})", options=machine_options, index=d_idx, key=f"mc_{i}_first")
                
                u_machine = st.session_state[f"mc_{i}_first"]
                single_msg = build_message([u_machine], st.session_state.custom_formats, st.session_state.custom_templates)
                st.write(f"💬 **개별 미리보기 ({i})** — 통합 전 단일 기기 기준")
                st.code(single_msg, language=None)
                st.markdown("<br>", unsafe_allow_html=True)
    elif analyze_clicked:
        st.warning("⚠️ 붙여넣은 카톡 내용이 비어있습니다.")
