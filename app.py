import streamlit as st
import re
import urllib.parse
import json
import os
from collections import OrderedDict

# 1. 페이지 기본 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

# 설정 파일 경로 (영구 저장)
SETTINGS_FILE = "message_settings.json"

# 2. 안내 문구 기본값 정의
txt_sindo = "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다."
txt_ecosys = "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다."
txt_305 = "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다."
txt_5473 = "사용량확인차 문자남겼습니다 확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다."
txt_apeos = "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다."
txt_5700 = "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4장 중에 3 페이지만 문자 보냅니다.)"
txt_l5100 = "+ 누르면 Machine info 누르고 ok → Print settings ok 누른 후 go(시작버튼) 누르셔서 나오는 4장 중 3번째 장만 문자로 부탑드립니다."
txt_ricoh = "사용자도구 클릭 → 카운터 클릭 → 카운터 목록인쇄클릭 (인쇄물 출력 후 발송 부탁드립니다.)"
txt_5005 = "사양설정 > 리포트 > 기능설정리스트 확인 후 문자로 부탁드립니다."
txt_x3220 = "기기 우측 버튼 보시면 카운터 누름 -> 화면 인쇄 버튼 클릭하여 확인 후 문자로 부탁드립니다."
txt_samsung = "설정 → 왼쪽 쭉 내리다보면 리포트 누름 → 오른쪽 사용량 정보 클릭하여 확인 후 문자로 부탁드립니다."
txt_default = "기기 화면의 카운터 메뉴에서 사용량 확인 후 사진 한 장만 문자나 카톡으로 발송 부탁드립니다."

DEFAULT_FORMATS = {
    "N500": txt_sindo, "N501": txt_sindo, "N502": txt_sindo, "N600": txt_sindo, "N601": txt_sindo,
    "D320": txt_sindo, "D400": txt_sindo, "D410": txt_sindo, "D420": txt_sindo, "D450": txt_sindo,
    "D460": txt_sindo, "D470": txt_sindo, "MA2100": txt_ecosys, "M5526": txt_ecosys, "M5521": txt_ecosys,
    "ECOSYS": txt_ecosys, "305": txt_305, "5473": txt_5473, "C2263": txt_apeos, "C2265": txt_apeos,
    "C2061": txt_apeos, "C3067": txt_apeos, "C2260": txt_apeos, "C2270": txt_apeos, "C2275": txt_apeos,
    "C3375": txt_apeos, "C4475": txt_apeos, "C5575": txt_apeos, "C2271": txt_apeos, "C2273": txt_apeos,
    "C3371": txt_apeos, "C3373": txt_apeos, "C3070": txt_apeos, "C3570": txt_apeos, "C4570": txt_apeos,
    "C5570": txt_apeos, "C7070": txt_apeos, "Apeos": txt_apeos, "5700": txt_5700, "L5100": txt_l5100,
    "2554": txt_ricoh, "C3003": txt_ricoh, "C4504": txt_ricoh, "5005": txt_5005, "X3220NR": txt_x3220,
    "X-9201": txt_x3220, "SL-": txt_samsung, "기본 기종": txt_default
}


# 3. 설정 파일 로드/저장 함수
def load_settings():
    """JSON 파일에서 설정 로드, 없으면 기본값 사용"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                merged = DEFAULT_FORMATS.copy()
                merged.update(loaded)
                return merged
    except Exception:
        pass
    return DEFAULT_FORMATS.copy()


def save_settings(formats):
    """JSON 파일로 설정 영구 저장"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(formats, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"설정 저장 실패: {e}")
        return False


# 4. 통합 문구 생성 함수
def build_message(machines_list, formats):
    """기종 1개 또는 여러 개 받아서 통합 문구 생성. 동일 모델은 자동 묶음."""
    # 동일 모델은 카운트로 묶기
    model_counts = OrderedDict()
    for m in machines_list:
        model_counts[m] = model_counts.get(m, 0) + 1
    
    unique_models = list(model_counts.keys())
    total_units = sum(model_counts.values())
    
    # 단일 기기 (기존 로직 유지)
    if len(unique_models) == 1 and total_units == 1:
        m = unique_models[0]
        how = formats.get(m, txt_default)
        if "안녕하세요" in how or "사용량확인차" in how:
            return f"{how}\n(기종: {m})\n매번 번거롭게 해드려 죄송합니다."
        return (
            "안녕하세요 퍼스트 전산입니다.\n"
            "마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다.\n"
            "카운터 한장만 보내주시면 감사하겠습니다.\n\n"
            f"▶ 기종: {m}\n"
            f"▶ 방법: {how}\n\n"
            "매번 번거롭게 해드려 죄송합니다."
        )
    
    # 여러 대 통합 문구
    lines = [
        "안녕하세요 퍼스트 전산입니다.",
        f"마감을 위해 보유하신 총 {total_units}대 기기의 카운터 사진이 필요하여 연락드렸습니다.",
        "각 기기별 카운터 한장씩 보내주시면 감사하겠습니다.\n",
    ]
    for idx, (m, count) in enumerate(model_counts.items(), 1):
        how = formats.get(m, txt_default)
        suffix = f" ({count}대)" if count > 1 else ""
        lines.append(f"▶ 기종{idx}: {m}{suffix}")
        lines.append(f"   방법: {how}\n")
    lines.append("매번 번거롭게 해드려 죄송합니다.")
    return "\n".join(lines)


# 5. 세션 상태 초기화
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = load_settings()


# 6. 상단 헤더 + 페이지 이동 버튼
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
    st.caption("기종별 안내 문구를 수정합니다. **저장하기**를 눌러야 다음 접속 시에도 유지됩니다.")
    
    machine_groups = {
        "📠 신도리코 (N/D 시리즈)": ["N500", "N501", "N502", "N600", "N601", "D320", "D400", "D410", "D420", "D450", "D460", "D470"],
        "📠 교세라 ECOSYS": ["MA2100", "M5526", "M5521", "ECOSYS"],
        "📠 후지 Apeos (C 시리즈)": ["C2263", "C2265", "C2061", "C3067", "C2260", "C2270", "C2275", "C3375", "C4475", "C5575", "C2271", "C2273", "C3371", "C3373", "C3070", "C3570", "C4570", "C5570", "C7070", "Apeos"],
        "📠 리코": ["2554", "C3003", "C4504"],
        "📠 삼성/제록스/HP/엡손": ["X3220NR", "X-9201", "SL-", "5700", "L5100"],
        "📠 기타 단일 모델": ["305", "5473", "5005"],
        "📠 공통 / 기본값": ["기본 기종"]
    }
    
    st.markdown("---")
    
    edited = st.session_state.custom_formats.copy()
    
    for group_name, machines in machine_groups.items():
        with st.expander(group_name, expanded=False):
            for m in machines:
                if m in edited:
                    edited[m] = st.text_area(
                        f"**{m}**",
                        value=edited[m],
                        height=100,
                        key=f"edit_setting_{m}"
                    )
    
    st.markdown("---")
    
    col_s1, col_s2, _ = st.columns([2, 2, 4])
    with col_s1:
        if st.button("💾 변경사항 저장", type="primary", use_container_width=True):
            st.session_state.custom_formats = edited
            if save_settings(edited):
                st.success("✅ 저장 완료! 메인페이지에 즉시 반영됩니다.")
    with col_s2:
        if st.button("🔄 기본값 복원", use_container_width=True):
            st.session_state.custom_formats = DEFAULT_FORMATS.copy()
            save_settings(DEFAULT_FORMATS)
            # 위젯 상태도 초기화
            for m in DEFAULT_FORMATS:
                k = f"edit_setting_{m}"
                if k in st.session_state:
                    del st.session_state[k]
            st.success("✅ 기본값으로 복원되었습니다.")
            st.rerun()


# ============================================================
# 메인 페이지
# ============================================================
else:
    st.caption("카톡 내용을 복사해 넣으면 거래처별로 마감 문자를 생성합니다. **동일 업체명은 한 통으로 자동 통합됩니다.**")
    
    # 텍스트영역 자동확장 CSS
    st.markdown(
        """
        <style>
        div[data-testid="stTextArea"] textarea {
            overflow-y: hidden !important;
            height: auto !important;
            min-height: 200px !important;
            max-height: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    def clear_text_area():
        st.session_state["text_input_area"] = ""
        # 관련 세션 상태도 함께 정리
        keys_to_delete = [k for k in list(st.session_state.keys())
                          if k.startswith(("final_nm_", "final_ph_", "final_mc_", "nm_", "ph_", "mc_"))]
        for k in keys_to_delete:
            del st.session_state[k]
    
    raw_text = st.text_area("카톡 내용 붙여넣기:", key="text_input_area")
    
    col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
    with col_btn1:
        st.button("🗑️ 입력 내용 전체 초기화", on_click=clear_text_area, use_container_width=True)
    with col_btn2:
        analyze_clicked = st.button("🔍 마감 문자 변환하기", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    if raw_text and raw_text.strip():
        # ── 블록 분리 ──
        split_pattern = r'((?<=\n)\d+(?:\s*,\s*)\d*[A-Z]*)|(^\d+(?:\s*,\s*)\d*[A-Z]*)'
        raw_parts = re.split(split_pattern, raw_text)
        
        blocks, current_block = [], ""
        for part in raw_parts:
            if part is None:
                continue
            if re.match(r'^\d+(?:\s*,\s*)', part.strip()):
                if current_block.strip():
                    blocks.append(current_block.strip())
                current_block = part
            else:
                current_block += part
        if current_block.strip():
            blocks.append(current_block.strip())
        
        valid_blocks = [b.strip() for b in blocks if len(b.strip()) > 5 and re.match(r'^\d+(?:\s*,\s*)', b.strip())]
        if not valid_blocks:
            valid_blocks = [raw_text.strip()]
        
        machine_options = list(st.session_state.custom_formats.keys())
        exclude_machines = ["기본 기종", "X3220NR", "X-9201", "SL-"]
        
        # ── 블록별 정보 추출 ──
        sms_data_list = []
        for i, block in enumerate(valid_blocks, 1):
            p_matches = re.findall(r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}', block)
            clean_phones = []
            for p in p_matches:
                c_p = re.sub(r'[^0-9]', '', p)
                if c_p not in clean_phones:
                    clean_phones.append(c_p)
            detected_phone_str = ", ".join(clean_phones) if clean_phones else ""
            
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            detected_name = "거래처 확인 바람"
            if lines:
                first_line = lines[0]
                name_part = re.sub(r'^\d+(?:\s*,\s*)\d*[A-Za-z]*', '', first_line).strip()
                detected_name = name_part.split('매월마감')[0].strip() if name_part else first_line
            
            matched_machine = "기본 기종"
            block_lower = block.lower()
            if "9201" in block_lower: matched_machine = "X-9201"
            elif "3220" in block_lower: matched_machine = "X3220NR"
            elif "sl-" in block_lower: matched_machine = "SL-"
            elif "ma2100" in block_lower: matched_machine = "MA2100"
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
        
        # ── 💡 [핵심 신규 로직] 업체명 기준으로 그룹화 ──
        grouped = OrderedDict()  # name -> {phones: [], machines: [], indices: []}
        
        for s_info in sms_data_list:
            i = s_info["index"]
            # 사용자가 편집한 값이 있으면 우선 사용, 없으면 자동 감지값 사용
            cur_name = st.session_state.get(f"nm_{i}_first", st.session_state[f"final_nm_{i}"]).strip()
            cur_phone = st.session_state.get(f"ph_{i}_first", st.session_state[f"final_ph_{i}"])
            cur_machine = st.session_state.get(f"mc_{i}_first", st.session_state[f"final_mc_{i}"])
            
            if cur_name not in grouped:
                grouped[cur_name] = {"phones": [], "machines": [], "indices": []}
            
            # 전화번호 정리 (하이픈 제거 후 중복 제거)
            for p in re.split(r'[\s,]+', cur_phone):
                p_clean = re.sub(r'[^0-9]', '', p.strip())
                if p_clean and p_clean not in grouped[cur_name]["phones"]:
                    grouped[cur_name]["phones"].append(p_clean)
            grouped[cur_name]["machines"].append(cur_machine)
            grouped[cur_name]["indices"].append(i)
        
        group_names = list(grouped.keys())
        total_groups = len(group_names)
        total_machines = sum(len(grouped[n]["machines"]) for n in group_names)
        
        st.subheader(f"🚀 거래처별 발송 버튼 (총 {total_groups}개 업체 / {total_machines}대 기기)")
        st.info("💡 동일 업체명은 자동으로 **한 통의 문자**로 통합됩니다. 버튼을 누르면 번호 선택 팝업이 표시됩니다.")
        
        # 팝업 다이얼로그
        @st.dialog("📱 문자 전송 대상 및 내용 확인")
        def show_send_popup(name, phones_list, msg):
            st.warning("⚠️ 수신 번호를 확인 후 하단의 최종 전송 버튼을 눌러주세요.")
            st.write(f"**업체명:** {name}")
            
            selected_number = ""
            if len(phones_list) > 1:
                st.info(f"💡 번호 {len(phones_list)}개 발견. 발송할 번호를 선택해 주세요:")
                selected_number = st.radio("수신 연락처 선택", options=phones_list, index=0)
            elif len(phones_list) == 1:
                st.write(f"**수신 번호:** {phones_list[0]}")
                selected_number = phones_list[0]
            else:
                st.error("❌ 등록된 수신 번호가 없습니다.")
            
            st.write("**📱 최종 전송 문구 미리보기:**")
            st.code(msg, language=None)
            
            if selected_number:
                target_num = re.sub(r'[^0-9]', '', selected_number)
                st.markdown(
                    f'<a href="sms:{target_num}?body={urllib.parse.quote(msg)}" target="_self" '
                    f'style="display: block; width: 100%; text-align: center; padding: 0.8rem; '
                    f'background-color: #00CC66; color: white; text-decoration: none; '
                    f'border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 15px;">'
                    f'✅ [{target_num}] 번호로 즉시 보내기</a>',
                    unsafe_allow_html=True
                )
        
        # 거래처별 버튼 4열 배치
        btn_cols = st.columns(4)
        for g_idx, name in enumerate(group_names):
            info = grouped[name]
            phones = info["phones"]
            machines = info["machines"]
            
            msg = build_message(machines, st.session_state.custom_formats)
            
            col_target = btn_cols[g_idx % 4]
            with col_target:
                if phones:
                    n_machines = len(machines)
                    n_phones = len(phones)
                    
                    if n_machines > 1 and n_phones > 1:
                        btn_label = f"💬 {name} (기기 {n_machines}대 / 번호 {n_phones}개)"
                    elif n_machines > 1:
                        btn_label = f"💬 {name} (기기 {n_machines}대 통합)"
                    elif n_phones > 1:
                        btn_label = f"💬 {name} (번호 {n_phones}개)"
                    else:
                        btn_label = f"💬 {name} 발송"
                    
                    if st.button(btn_label, key=f"group_btn_{g_idx}", use_container_width=True):
                        show_send_popup(name, phones, msg)
                else:
                    st.button(f"❌ {name} (번호없음)", disabled=True, use_container_width=True, key=f"group_disabled_btn_{g_idx}")
        
        st.markdown("---")
        st.subheader("🔍 상세 정보 편집")
        st.caption("💡 **업체명을 동일하게 수정하면 자동으로 통합됩니다.** 수정 즉시 위의 발송 버튼이 갱신됩니다.")
        
        for s_info in sms_data_list:
            i = s_info["index"]
            with st.container():
                col1, col2, col3 = st.columns([2, 1.5, 1])
                with col1:
                    st.text_input(f"업체명 ({i})", value=st.session_state[f"final_nm_{i}"], key=f"nm_{i}_first")
                with col2:
                    st.text_input(f"연락처 ({i}) - 쉼표로 구분", value=st.session_state[f"final_ph_{i}"], key=f"ph_{i}_first")
                with col3:
                    d_idx = machine_options.index(st.session_state[f"final_mc_{i}"]) if st.session_state[f"final_mc_{i}"] in machine_options else machine_options.index("기본 기종")
                    st.selectbox(f"기종 ({i})", options=machine_options, index=d_idx, key=f"mc_{i}_first")
                
                u_machine = st.session_state[f"mc_{i}_first"]
                single_msg = build_message([u_machine], st.session_state.custom_formats)
                
                st.write(f"💬 **개별 미리보기 ({i})** — 통합 전 단일 기기 기준")
                st.code(single_msg, language=None)
                st.markdown("<br>", unsafe_allow_html=True)
    elif analyze_clicked:
        st.warning("⚠️ 붙여넣은 카톡 내용이 비어있습니다. 내용을 입력한 후 버튼을 눌러주세요.")
