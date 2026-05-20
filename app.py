import streamlit as st
import re
import urllib.parse

# 1. 페이지 기본 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 번호가 적힌 거래처만 정확하게 인식하여 마감 문자를 대량 생성합니다. (복수 번호 지원)")

# 핸드폰에서 손가락이 갇히지 않도록 내부 스크롤을 원천 차단하고 높이를 완전 자동 확장하는 CSS
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

# 3. 세션 상태 사전 초기화
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
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

# 입력창 초기화용 안전 함수 정의
def clear_text_area():
    st.session_state["text_input_area"] = ""

# 최종 텍스트 바인딩
raw_text = st.text_area("카톡 내용 붙여넣기:", key="text_input_area")

# 4. 버튼 영역
col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
with col_btn1:
    st.button("🗑️ 입력 내용 전체 초기화", on_click=clear_text_area, use_container_width=True)
        
with col_btn2:
    analyze_clicked = st.button("🔍 마감 문자 변환하기", type="primary", use_container_width=True)

st.markdown("---")

# 5. 분석 로직 가동
if raw_text and raw_text.strip():
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
    
    sms_data_list = []
    for i, block in enumerate(valid_blocks, 1):
        # 💡 [변경 포인트] 블록 내의 모든 연락처 패턴 추출 (중복 제거)
        p_matches = re.findall(r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}', block)
        # 하이픈 제거하여 깔끔하게 정리한 번호 리스트 생성
        clean_phones = []
        for p in p_matches:
            c_p = re.sub(r'[^0-9]', '', p)
            if c_p not in clean_phones:
                clean_phones.append(c_p)
        
        # 화면에 보여주기 위한 기본 문자열 콤마 조합
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
        
        # 고정 키값 바인딩
        if f"final_nm_{i}" not in st.session_state: st.session_state[f"final_nm_{i}"] = detected_name
        if f"final_ph_{i}" not in st.session_state: st.session_state[f"final_ph_{i}"] = detected_phone_str
        if f"final_mc_{i}" not in st.session_state: st.session_state[f"final_mc_{i}"] = matched_machine

        sms_data_list.append({"index": i, "block_raw": block})

    st.subheader(f"🚀 모바일 즉시 전송 버튼 목록 (총 {len(sms_data_list)}건)")
    st.info("💡 아래 업체 버튼을 누르면 내용 최종 확인 및 번호 선택 팝업창이 나타납니다.")
    
    # 💡 팝업을 띄울 때 쓸 다이얼로그 함수 정의
    @st.dialog("📱 문자 전송 대상 및 내용 확인")
    def show_send_popup(name, phone_input, msg):
        st.warning("⚠️ 수신 번호를 확인 및 선택 후 하단의 최종 전송을 눌러주세요.")
        
        # 콤마나 공백으로 분리하여 번호 목록 추출
        nums = [n.strip() for n in re.split(r'[\s,]+', phone_input) if n.strip()]
        
        selected_number = ""
        if len(nums) > 1:
            st.info(f"💡 번호가 {len(nums)}개 발견되었습니다. 발송할 번호를 선택해 주세요:")
            # 라디오 버튼으로 고를 수 있게 제공
            selected_number = st.radio("수신 연락처 선택", options=nums, index=0)
        elif len(nums) == 1:
            st.write(f"**수신 번호:** {nums[0]}")
            selected_number = nums[0]
        else:
            st.error("❌ 등록된 수신 번호가 없습니다. 하단에서 번호를 입력해 주세요.")
        
        st.write("**📱 최종 전송 문구 미리보기:**")
        st.code(msg, language=None)
        
        if selected_number:
            # 안전하게 하이픈 등 숫자 이외의 문자 제거
            target_num = re.sub(r'[^0-9]', '', selected_number)
            st.markdown(
                f'<a href="sms:{target_num}?body={urllib.parse.quote(msg)}" target="_self" '
                f'style="display: block; width: 100%; text-align: center; padding: 0.8rem; '
                f'background-color: #00CC66; color: white; text-decoration: none; '
                f'border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 15px;">'
                f'✅ 확인완료: [{target_num}] 번호로 즉시 보내기</a>', 
                unsafe_allow_html=True
            )

    btn_cols = st.columns(4)
    for idx, s_info in enumerate(sms_data_list):
        i = s_info["index"]
        cur_name = st.session_state.get(f"nm_{i}_first", st.session_state[f"final_nm_{i}"])
        cur_phone_str = st.session_state.get(f"ph_{i}_first", st.session_state[f"final_ph_{i}"])
        cur_machine = st.session_state.get(f"mc_{i}_first", st.session_state[f"final_mc_{i}"])
        
        cur_how = st.session_state.custom_formats.get(cur_machine, txt_default)
        if "안녕하세요" in cur_how or "사용량확인차" in cur_how:
            cur_msg = f"{cur_how}\n(기종: {cur_machine})\n매번 번거롭게 해드려 죄송합니다."
        else:
            cur_msg = f"안녕하세요 퍼스트 전산입니다.\n마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다.\n카운터 한장만 보내주시면 감사하겠습니다.\n\n▶ 기종: {cur_machine}\n▶ 방법: {cur_how}\n\n매번 번거롭게 해드려 죄송합니다."

        col_target = btn_cols[idx % 4]
        with col_target:
            if cur_phone_str.strip():
                # 💡 여러 개의 번호가 감지된 경우 버튼에 (번호 여러개) 표시 추가하여 한눈에 보이기
                phone_count = len([n for n in re.split(r'[\s,]+', cur_phone_str) if n.strip()])
                btn_label = f"💬 {cur_name} ({phone_count}개)" if phone_count > 1 else f"💬 {cur_name} 발송"
                
                if st.button(btn_label, key=f"popup_btn_{i}", use_container_width=True):
                    show_send_popup(cur_name, cur_phone_str, cur_msg)
            else:
                st.button(f"❌ {cur_name} (번호없음)", disabled=True, use_container_width=True, key=f"disabled_btn_{i}")

    st.markdown("---")
    st.subheader("🔍 상세 정보 편집 및 개별 문구 확인")
    
    for s_info in sms_data_list:
        i = s_info["index"]
        with st.container():
            col1, col2, col3 = st.columns([2, 1.5, 1])
            with col1: u_name = st.text_input(f"업체명 ({i})", value=st.session_state[f"final_nm_{i}"], key=f"nm_{i}_first")
            with col2: u_phone = st.text_input(f"연락처 ({i}) - 여러개는 쉼표(,) 구분", value=st.session_state[f"final_ph_{i}"], key=f"ph_{i}_first")
            with col3:
                d_idx = machine_options.index(st.session_state[f"final_mc_{i}"]) if st.session_state[f"final_mc_{i}"] in machine_options else machine_options.index("기본 기종")
                u_machine = st.selectbox(f"기종 ({i})", options=machine_options, index=d_idx, key=f"mc_{i}_first")
                
            how = st.session_state.custom_formats.get(u_machine, txt_default)
            if "안녕하세요" in how or "사용량확인차" in how:
                final_msg = f"{how}\n(기종: {u_machine})\n매번 번거롭게 해드려 죄송합니다."
            else:
                final_msg = f"안녕하세요 퍼스트 전산입니다.\n마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다.\n카운터 한장만 보내주시면 감사하겠습니다.\n\n▶ 기종: {u_machine}\n▶ 방법: {how}\n\n매번 번거롭게 해드려 죄송합니다."
                
            st.write(f"💬 **최종 문구 미리보기 ({i})**")
            st.code(final_msg, language=None)
            st.markdown("<br>", unsafe_allow_html=True)
elif analyze_clicked:
    st.warning("⚠️ 붙여넣은 카톡 내용이 비어있습니다. 내용을 입력한 후 버튼을 눌러주세요.")
