import streamlit as st
import re
import urllib.parse

# 1. 페이지 기본 설정 (기존 방식 유지)
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

# 핸드폰 화면 스크롤 방지 및 높이 자동 확장 CSS
st.markdown(
    """
    <style>
    div[data-testid="stTextArea"] textarea {
        overflow-y: hidden !important;
        height: auto !important;
        min-height: 120px !important;
        max-height: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. [팀별 X 급별] 문자 양식 세션 상태 독립 초기화 (저장 버그 차단)
teams = ["A지역", "B지역", "C지역", "D지역"]

if "init_done" not in st.session_state:
    st.session_state["init_done"] = True
    
    # 각 팀별로 2가지 급수 인삿말을 각각 독립적으로 저장할 수 있도록 방을 만듭니다.
    for team in teams:
        st.session_state[f"msg_{team}_v_ss"] = (
            f"안녕하세요 퍼스트 전산 {team} 담당자입니다.\n"
            "세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다.\n"
            "각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
        )
        st.session_state[f"msg_{team}_s_nn_n"] = (
            f"안녕하세요 퍼스트 전산 {team} 담당자입니다.\n"
            "세금계산서 발행을 위해 보유하신 총 {{total}}대 기기의 카운터 사진이 필요하여 연락드렸습니다.\n"
            "각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
        )

    # 기종별 기본 안내 문구 사전 (기존 데이터)
    st.session_state["custom_formats"] = {
        "N500": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작",
        "N501": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작",
        "D320": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작",
        "MA2100": "시스템메뉴/카운터 버튼 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄",
        "305": "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok",
        "C2263": "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 화면 캡쳐",
        "X3220NR": "기기 우측 카운터 누름 -> 화면 인쇄 버튼 클릭",
        "SL-": "설정 → 왼쪽 리포트 누름 → 오른쪽 사용량 정보 클릭",
        "기본 기종": "기기 화면의 카운터 메뉴에서 사용량 확인"
    }

# 3. 📋 기존 방식대로 상단 탭 구성 (메인 화면과 설정 페이지 완벽 분리)
tab1, tab2 = st.tabs(["📋 마감 문자 작성 (메인)", "⚙️ 팀별/급별 문자 양식 설정"])

# ---------------------------------------------------------
# [탭 2] 팀별 문자 양식 설정 페이지 (각 팀마다 들어와서 개별 수정 및 저장)
# ---------------------------------------------------------
with tab2:
    st.subheader("⚙️ [ABCD] 팀별 / 급별 문자 인삿말 관리")
    st.info("💡 수정하고 싶은 팀의 탭을 선택하고 인삿말을 고친 뒤, 해당 팀의 [💾 저장] 버튼을 누르면 완전히 고정됩니다.")
    
    # 설정창 내부에 각 지역팀별 탭을 따로 만들어 팀끼리 뒤틀리지 않게 격리
    team_setting_tabs = st.tabs([f"📍 {t} 설정" for t in teams])
    
    for idx, team_name in enumerate(teams):
        with team_setting_tabs[idx]:
            st.markdown(f"### 📢 {team_name} 전용 인삿말 수정")
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                v_ss_in = st.text_area(
                    f"💎 {team_name} - V급 / SS급 인삿말 양식", 
                    value=st.session_state[f"msg_{team_name}_v_ss"],
                    key=f"input_{team_name}_v_ss"
                )
            with col_t2:
                s_nn_n_in = st.text_area(
                    f"⭐ {team_name} - S / NN / N급 인삿말 양식 ({{total}} 포함)", 
                    value=st.session_state[f"msg_{team_name}_s_nn_n"],
                    key=f"input_{team_name}_s_nn_n"
                )
                
            if st.button(f"💾 {team_name} 인삿말 안전하게 저장하기", key=f"save_btn_{team_name}", type="primary", use_container_width=True):
                st.session_state[f"msg_{team_name}_v_ss"] = v_ss_in
                st.session_state[f"msg_{team_name}_s_nn_n"] = s_nn_n_in
                st.success(f"✅ {team_name}의 2가지 급별 인삿말이 안전하게 저장되었습니다!")

# ---------------------------------------------------------
# [탭 1] 마감 문자 작성 메인 화면 (자기 팀 선택 후 문자 발송)
# ---------------------------------------------------------
with tab1:
    st.title("퍼스트전산 마감 도우미 📱")
    
    # 🔥 [핵심 기능] 메인화면에서 로그인하듯 자기 팀 지역 선택
    st.markdown("### 👤 작업 팀 선택")
    selected_work_team = st.selectbox(
        "현재 마감 문자를 발송할 우리 팀(지역)을 선택하세요:", 
        options=teams,
        help="선택한 팀의 설정 페이지에 저장된 인삿말 양식으로 문자가 생성됩니다."
    )
    
    st.markdown("---")

    def clear_text_area():
        st.session_state["text_input_area"] = ""

    raw_text = st.text_area(f"[{selected_work_team}] 카톡 내용 붙여넣기:", key="text_input_area")

    col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
    with col_btn1:
        st.button("🗑️ 입력 내용 전체 초기화", on_click=clear_text_area, use_container_width=True)
    with col_btn2:
        analyze_clicked = st.button("🔍 마감 문자 변환하기", type="primary", use_container_width=True)

    st.markdown("---")

    if raw_text and raw_text.strip():
        # 1. 기존 방식의 카톡 텍스트 블록 분리 정규식 로직
        split_pattern = r'((?<=\n)\d+(?:\s*,\s*)\d*[A-Z] )|(^\d+(?:\s*,\s*)\d*[A-Z] )'
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
            
        valid_blocks = [b.strip() for b in blocks if len(b.strip()) > 5]
        if not valid_blocks:
            valid_blocks = [raw_text.strip()]
            
        machine_options = list(st.session_state.custom_formats.keys())
        level_options = ["V급 / SS급", "S / NN / N"]  # 팀 내부의 2가지 급수 선택지
        
        # 2. 기존 핵심 로직: 연락처별 업체 및 기기 정보 중복 데이터 통합 처리
        customer_map = {}
        
        for idx, block in enumerate(valid_blocks, 1):
            p_matches = sorted(list(set(re.findall(r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}', block))))
            phone_key = ", ".join(p_matches) if p_matches else f"NO_PHONE_{idx}"
            
            # 업체명 추출
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            detected_name = "거래처 확인 바람"
            if lines:
                first_line = lines[0]
                name_part = re.sub(r'^\d+(?:\s*,\s*)\d*[A-Za-z]*', '', first_line).strip()
                detected_name = name_part.split('매월마감')[0].strip() if name_part else first_line
            
            # 기종 자동 매칭
            matched_machine = "기본 기종"
            block_lower = block.lower()
            for k in machine_options:
                if k != "기본 기종" and k.lower() in block_lower:
                    matched_machine = k
                    break
            
            # 본문을 분석하여 V급 계열인지 S급 계열인지 2가지로 자동 1차 분류
            detected_level = "S / NN / N"
            if any(x in block for x in ["V", "v", "SS", "ss"]):
                detected_level = "V급 / SS급"

            if phone_key not in customer_map:
                customer_map[phone_key] = {
                    "name": detected_name,
                    "phones": p_matches,
                    "level": detected_level,
                    "machines": [matched_machine],
                    "raw_blocks": [block]
                }
            else:
                customer_map[phone_key]["machines"].append(matched_machine)
                customer_map[phone_key]["raw_blocks"].append(block)

        # 세션 고정 바인딩 (문법 오류 수정 완료)
        sms_data_list = []
        for i, (p_key, c_info) in enumerate(customer_map.items(), 1):
            if f"final_nm_{i}" not in st.session_state:
                st.session_state[f"final_nm_{i}"] = c_info["name"]
            if f"final_phs_{i}" not in st.session_state:
                st.session_state[f"final_phs_{i}"] = c_info["phones"]
            if f"final_level_{i}" not in st.session_state:
                st.session_state[f"final_level_{i}"] = c_info["level"]
            if f"final_mcs_{i}" not in st.session_state:
                st.session_state[f"final_mcs_{i}"] = c_info["machines"]
                
            sms_data_list.append({"index": i, "phone_key": p_key})

        # 3. 상단 모바일 즉시 전송 버튼 목록 (선택한 팀의 인삿말로 조합)
        st.subheader(f"🚀 {selected_work_team} 마감 문자 발송 목록 (총 {len(sms_data_list)}건)")
        btn_cols = st.columns(4)
        
        for idx, s_info in enumerate(sms_data_list):
            i = s_info["index"]
            cur_name = st.session_state.get(f"nm_{i}_f", st.session_state[f"final_nm_{i}"])
            cur_phones = st.session_state.get(f"phs_{i}_f", st.session_state[f"final_phs_{i}"])
            cur_level = st.session_state.get(f"lv_{i}_f", st.session_state[f"final_level_{i}"])
            cur_machines = st.session_state.get(f"mcs_{i}_f", st.session_state[f"final_mcs_{i}"])
            
            total_devices = len(cur_machines)
            
            # 🔥 메인에서 선택한 [현재 작업 팀]의 [해당 급수 인삿말]을 매칭하여 동적으로 가져옴
            if cur_level == "V급 / SS급":
                base_msg = st.session_state[f"msg_{selected_work_team}_v_ss"]
            else:
                base_msg = st.session_state[f"msg_{selected_work_team}_s_nn_n"].replace("{total}", str(total_devices))
                
            # 기존 기종 통합 포맷 출력 빌드
            machine_details = ""
            if total_devices == 1:
                m_item = cur_machines[0]
                m_how = st.session_state["custom_formats"].get(m_item, "기본 사용량 확인")
                machine_details = f"▶ 기종: {m_item}\n▶ 방법: {m_how}"
            else:
                machine_details = "📌 고객님께서 사용 중인 기기 목록:\n"
                for m_idx, m_item in enumerate(cur_machines, 1):
                    m_how = st.session_state["custom_formats"].get(m_item, "기본 사용량 확인")
                    machine_details += f"{m_idx}. {m_item}: {m_how}\n"
                    
            cur_msg = f"{base_msg}\n\n{machine_details.strip()}"
            
            col_target = btn_cols[idx % 4]
            with col_target:
                if cur_phones:
                    phone_suffix = f" ({len(cur_phones)}개)" if len(cur_phones) > 1 else ""
                    if st.button(f"💬 {cur_name}{phone_suffix} 발송", key=f"popup_btn_{i}", use_container_width=True):
                        
                        @st.dialog(f"📱 {cur_name}님 문자 최종 확인 ({selected_work_team})")
                        def send_dialog(name=cur_name, phones=cur_phones, msg=cur_msg):
                            st.warning("⚠️ 전송 번호와 문구를 최종 확인하세요.")
                            selected_phone = phones[0]
                            if len(phones) > 1:
                                selected_phone = st.radio("📞 발송할 번호 선택:", options=phones, key=f"sel_ph_{i}")
                            else:
                                st.write(f"📱 수신 번호: {phones[0]}")
                                
                            st.code(msg, language=None)
                            clean_phone = re.sub(r'[^0-9]', '', selected_phone)
                            
                            st.markdown(
                                f'<a href="sms:{clean_phone}?body={urllib.parse.quote(msg)}" target="_self" '
                                f'style="display: block; width: 100%; text-align: center; padding: 0.8rem; '
                                f'background-color: #00CC66; color: white; text-decoration: none; '
                                f'border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 15px;">'
                                f'✅ 확인완료: 지금 바로 문자 앱으로 보내기 </a>', 
                                unsafe_allow_html=True
                            )
                        send_dialog()
                else:
                    st.button(f"❌ {cur_name} (번호없음)", disabled=True, use_container_width=True, key=f"disabled_btn_{i}")

        # 4. 하단 상세 편집 목록 (기존 방식 유지 + 팀 내부 급수 라디오/선택박스 연동)
        st.markdown("---")
        st.subheader("🔍 상세 정보 편집 및 급별 인삿말 실시간 확인")
        
        for idx, s_info in enumerate(sms_data_list):
            i = s_info["index"]
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 2])
                
                with col1:
                    u_name = st.text_input(f"업체명 ({i})", value=st.session_state[f"final_nm_{i}"], key=f"nm_{i}_f")
                with col2:
                    joined_phs = ", ".join(st.session_state[f"final_phs_{i}"])
                    u_phone_str = st.text_input(f"연락처 목록 ({i})", value=joined_phs, key=f"ph_str_{i}")
                    st.session_state[f"phs_{i}_f"] = [p.strip() for p in u_phone_str.split(",") if p.strip()]
                with col3:
                    # 🔥 여기서 해당 거래처를 어느 급으로 보낼지 2가지 중 고를 수 있게 수정
                    d_lv_idx = level_options.index(st.session_state[f"final_level_{i}"])
                    u_level = st.selectbox(f"인삿말 양식 급 선택 ({i})", options=level_options, index=d_lv_idx, key=f"lv_{i}_f")
                
                cur_machines = st.session_state[f"final_mcs_{i}"]
                total_devices = len(cur_machines)
                
                # 선택된 급수에 맞는 현재 팀의 인삿말 미리보기 빌드
                if u_level == "V급 / SS급":
                    indiv_base = st.session_state[f"msg_{selected_work_team}_v_ss"]
                else:
                    indiv_base = st.session_state[f"msg_{selected_work_team}_s_nn_n"].replace("{total}", str(total_devices))
                    
                machine_details = ""
                if total_devices == 1:
                    m_item = cur_machines[0]
                    m_how = st.session_state["custom_formats"].get(m_item, "기본 사용량 확인")
                    machine_details = f"▶ 기종: {m_item}\n▶ 방법: {m_how}"
                else:
                    machine_details = "📌 고객님께서 사용 중인 기기 목록:\n"
                    for m_idx, m_item in enumerate(cur_machines, 1):
                        m_how = st.session_state["custom_formats"].get(m_item, "기본 사용량 확인")
                        machine_details += f"{m_idx}. {m_item}: {m_how}\n"
                        
                final_msg = f"{indiv_base}\n\n{machine_details.strip()}"
                
                st.write(f"💬 최종 문구 미리보기 ({i})")
                st.code(final_msg, language=None)
                st.markdown("<br>", unsafe_allow_html=True)
                
    elif analyze_clicked:
        st.warning("⚠️ 붙여넣은 카톡 내용이 없습니다. 내용을 입력해 주세요.")
