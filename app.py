import streamlit as st
import re
import urllib.parse

# 1. 페이지 기본 설정
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

# 2. [지역별 X 기기대수별 X 급별] 세션 상태 독립 초기화 (저장 버그 완벽 차단)
teams = ["A지역", "B지역", "C지역", "D지역"]

if "init_done" not in st.session_state:
    st.session_state["init_done"] = True
    
    # 4개 구역별로 1대용(2가지 급), 여러대용(2가지 급) 총 4개씩 독립 방 생성
    for team in teams:
        # 기기 1대 기준 기본값
        st.session_state[f"msg_{team}_single_v_ss"] = f"안녕하세요 퍼스트 전산 {team} 담당자입니다.\n세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다.\n카운터 한장 보내주시면 감사하겠습니다."
        st.session_state[f"msg_{team}_single_s_nn_n"] = f"안녕하세요 퍼스트 전산 {team} 담당자입니다.\n마감을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다.\n바쁘시겠지만 카운터 사진 한장 부탁드립니다."
        
        # 기기 여러 대 기준 기본값 ({total} 사용 가능)
        st.session_state[f"msg_{team}_multi_v_ss"] = f"안녕하세요 퍼스트 전산 {team} 담당자입니다.\n세금계산서 발행을 위해 보유하신 총 {{total}}대 기기의 카운터 사진이 필요하여 연락드렸습니다.\n각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
        st.session_state[f"msg_{team}_multi_s_nn_n"] = f"안녕하세요 퍼스트 전산 {team} 담당자입니다.\n마감을 위해 보유하신 총 {{total}}대 기기의 사용량 확인이 필요합니다.\n번거로우시겠지만 기기별로 카운터 사진 한장씩 전송 부탁드립니다."

    # 사장님이 요청하신 [기종별 카운터 방법 수정 사전] 완벽 복구 및 초기화
    if "custom_formats" not in st.session_state:
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

# 3. 상단 탭 구성 (메인과 설정을 깔끔하게 분리)
tab1, tab2 = st.tabs(["📋 마감 문자 작성 (메인)", "⚙️ 팀별/기기대수별 양식 및 기종 관리"])

# ---------------------------------------------------------
# [탭 2] 설정 페이지 (지역별 4가지 양식 + 기종별 카운터 방법 수정)
# ---------------------------------------------------------
with tab2:
    st.subheader("⚙️ 지역별 문구 및 기종별 카운터 안내 수정실")
    
    # 2-1. 지역별 인삿말 세부 설정
    st.markdown("### 📍 1. ABCD 지역별 / 기기대수별 / 급별 인삿말 관리")
    st.info("💡 각 지역 탭을 누르고 [기기 1대] 일 때와 [기기 여러대] 일 때의 급수별 문구를 고친 뒤 꼭 아래 저장 버튼을 누르세요.")
    
    team_setting_tabs = st.tabs([f"🏠 {t} 양식 설정" for t in teams])
    for idx, team_name in enumerate(teams):
        with team_setting_tabs[idx]:
            st.markdown(f"#### 📢 {team_name} 전용 마감 인삿말 편집")
            
            st.write("**[구분 1] 기기 딱 '1대'만 사용하는 업체용 문구**")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                s_v_ss = st.text_area(f"💎 1대용 - V급 / SS급 양식", value=st.session_state[f"msg_{team_name}_single_v_ss"], key=f"in_{team_name}_s_v")
            with col_s2:
                s_s_nn = st.text_area(f"⭐ 1대용 - S / NN / N급 양식", value=st.session_state[f"msg_{team_name}_single_s_nn_n"], key=f"in_{team_name}_s_n")
                
            st.write("**[구분 2] 기기를 '여러 대(2대 이상)' 사용하는 업체용 문구** (현재 대수가 들어갈 자리에 `{{total}}`을 꼭 적어주세요)")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                m_v_ss = st.text_area(f"💎 여러대용 - V급 / SS급 양식", value=st.session_state[f"msg_{team_name}_multi_v_ss"], key=f"in_{team_name}_m_v")
            with col_m2:
                m_s_nn = st.text_area(f"⭐ 여러대용 - S / NN / N급 ({{total}} 포함) 양식", value=st.session_state[f"msg_{team_name}_multi_s_nn_n"], key=f"in_{team_name}_m_n")
                
            if st.button(f"💾 {team_name} 문구 최종 저장", key=f"save_team_{team_name}", type="primary", use_container_width=True):
                st.session_state[f"msg_{team_name}_single_v_ss"] = s_v_ss
                st.session_state[f"msg_{team_name}_single_s_nn_n"] = s_s_nn
                st.session_state[f"msg_{team_name}_multi_v_ss"] = m_v_ss
                st.session_state[f"msg_{team_name}_multi_s_nn_n"] = m_s_nn
                st.success(f"✅ {team_name}의 4가지 세부 조건 문구가 완벽히 고정되었습니다!")

    st.markdown("---")
    
    # 2-2. 사장님이 찾으시던 기종별 카운터 안내 방법 수정 기능 복구 완료
    st.markdown("### 🖨️ 2. 기종별 카운터 확인 방법 관리 사전")
    st.info("💡 기종명을 수정하거나 확인하는 방법을 바꾸고 아래 [💾 기종 사전 정보 저장]을 누르면 즉시 반영됩니다.")
    
    updated_formats = {}
    fmt_cols = st.columns(2)
    for f_idx, (machine_key, how_to_print) in enumerate(st.session_state["custom_formats"].items()):
        target_col = fmt_cols[f_idx % 2]
        with target_col:
            updated_how = st.text_input(f"📟 {machine_key} 확인 방법", value=how_to_print, key=f"fmt_input_{machine_key}")
            updated_formats[machine_key] = updated_how
            
    if st.button("💾 기종 사전 정보 전체 저장하기", type="primary", use_container_width=True):
        st.session_state["custom_formats"] = updated_formats
        st.success("✅ 복사기 기종별 카운터 인쇄 방법 사전이 안전하게 업데이트되었습니다!")

# ---------------------------------------------------------
# [탭 1] 메인 문자 작성 화면 (실시간 기기 대수 및 급수 매칭 시스템)
# ---------------------------------------------------------
with tab1:
    st.title("퍼스트전산 마감 도우미 📱")
    
    st.markdown("### 👤 작업 구역(팀) 선택")
    selected_work_team = st.selectbox(
        "현재 마감 작업을 진행할 팀을 선택하세요:", 
        options=teams,
        help="선택한 지역팀의 [1대/여러대 X 급별] 맞춤형 양식 창고가 열립니다."
    )
    
    st.markdown("---")

    def clear_text_area():
        st.session_state["text_input_area"] = ""

    raw_text = st.text_area(f"[{selected_work_team}] 카톡 정산 내용 붙여넣기:", key="text_input_area")

    col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
    with col_btn1:
        st.button("🗑️ 입력 내용 전체 초기화", on_click=clear_text_area, use_container_width=True)
    with col_btn2:
        analyze_clicked = st.button("🔍 마감 문자 변환하기", type="primary", use_container_width=True)

    st.markdown("---")

    if raw_text and raw_text.strip():
        # 카톡 정규식 파싱 로직
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
        level_options = ["V급 / SS급 계열", "S / NN / N급 계열"]
        
        # 연락처 통합 맵핑 구축
        customer_map = {}
        for idx, block in enumerate(valid_blocks, 1):
            p_matches = sorted(list(set(re.findall(r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}', block))))
            phone_key = ", ".join(p_matches) if p_matches else f"NO_PHONE_{idx}"
            
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            detected_name = "거래처 확인 바람"
            if lines:
                first_line = lines[0]
                name_part = re.sub(r'^\d+(?:\s*,\s*)\d*[A-Za-z]*', '', first_line).strip()
                detected_name = name_part.split('매월마감')[0].strip() if name_part else first_line
            
            matched_machine = "기본 기종"
            block_lower = block.lower()
            for k in machine_options:
                if k != "기본 기종" and k.lower() in block_lower:
                    matched_machine = k
                    break
            
            # 본문 속 문자로 등급 자동 1차 분류
            detected_level = "S / NN / N급 계열"
            if any(x in block for x in ["V", "v", "SS", "ss"]):
                detected_level = "V급 / SS급 계열"

            if phone_key not in customer_map:
                customer_map[phone_key] = {
                    "name": detected_name,
                    "phones": p_matches,
                    "level": detected_level,
                    "machines": [matched_machine]
                }
            else:
                customer_map[phone_key]["machines"].append(matched_machine)

        # 데이터 세션 동적 고정 바인딩
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

        # 💥 발송 상단 레이아웃 출력 목록
        st.subheader(f"🚀 {selected_work_team} 즉시 문자 발송 버튼 리스트 (총 {len(sms_data_list)}건)")
        btn_cols = st.columns(4)
        
        for idx, s_info in enumerate(sms_data_list):
            i = s_info["index"]
            cur_name = st.session_state.get(f"nm_{i}_f", st.session_state[f"final_nm_{i}"])
            cur_phones = st.session_state.get(f"phs_{i}_f", st.session_state[f"final_phs_{i}"])
            cur_level = st.session_state.get(f"lv_{i}_f", st.session_state[f"final_level_{i}"])
            cur_machines = st.session_state.get(f"mcs_{i}_f", st.session_state[f"final_mcs_{i}"])
            
            total_devices = len(cur_machines)
            
            # 🔥 [대수 판별 핵심 로직] 1대냐 여러대냐에 따라 세션에서 불러오는 베이스 인삿말 타겟을 자동 전환
            if total_devices == 1:
                if cur_level == "V급 / SS급 계열":
                    base_msg = st.session_state[f"msg_{selected_work_team}_single_v_ss"]
                else:
                    base_msg = st.session_state[f"msg_{selected_work_team}_single_s_nn_n"]
            else:
                if cur_level == "V급 / SS급 계열":
                    base_msg = st.session_state[f"msg_{selected_work_team}_multi_v_ss"].replace("{total}", str(total_devices))
                else:
                    base_msg = st.session_state[f"msg_{selected_work_team}_multi_s_nn_n"].replace("{total}", str(total_devices))
                    
            # 하단 복구된 기종별 인쇄/확정 매칭 가이드 빌드
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
                        
                        @st.dialog(f"📱 {cur_name}님 문자 전송 ({selected_work_team} - 기기 {total_devices}대)")
                        def send_dialog(name=cur_name, phones=cur_phones, msg=cur_msg):
                            st.warning("⚠️ 전송 번호와 양식을 확인하세요.")
                            selected_phone = phones[0]
                            if len(phones) > 1:
                                selected_phone = st.radio("📞 발송 번호 고르기:", options=phones, key=f"sel_ph_{i}")
                            else:
                                st.write(f"📱 수신 번호: {phones[0]}")
                                
                            st.code(msg, language=None)
                            clean_phone = re.sub(r'[^0-9]', '', selected_phone)
                            
                            st.markdown(
                                f'<a href="sms:{clean_phone}?body={urllib.parse.quote(msg)}" target="_self" '
                                f'style="display: block; width: 100%; text-align: center; padding: 0.8rem; '
                                f'background-color: #00CC66; color: white; text-decoration: none; '
                                f'border-radius: 8px; font-weight: bold; font-size: 18px; margin-top: 15px;">'
                                f'✅ 문자 전송하기 </a>', 
                                unsafe_allow_html=True
                            )
                        send_dialog()
                else:
                    st.button(f"❌ {cur_name} (번호없음)", disabled=True, use_container_width=True, key=f"disabled_btn_{i}")

        # 5. 하단 상세 정보 수정 및 등급 선택 섹션
        st.markdown("---")
        st.subheader("🔍 거래처별 상세 정보 확인 및 급수 변경")
        
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
                    # 🔥 메인 화면 하단 편집기에서 사장님이 거래처 등급을 수동으로 바로 조절 가능하게 한 드롭다운
                    d_lv_idx = level_options.index(st.session_state[f"final_level_{i}"])
                    u_level = st.selectbox(f"인삿말 급수 변경 ({i})", options=level_options, index=d_lv_idx, key=f"lv_{i}_f")
                
                cur_machines = st.session_state[f"final_mcs_{i}"]
                total_devices = len(cur_machines)
                
                # 실시간 보기용 메시지 리빌드 빌더
                if total_devices == 1:
                    if u_level == "V급 / SS급 계열":
                        indiv_base = st.session_state[f"msg_{selected_work_team}_single_v_ss"]
                    else:
                        indiv_base = st.session_state[f"msg_{selected_work_team}_single_s_nn_n"]
                else:
                    if u_level == "V급 / SS급 계열":
                        indiv_base = st.session_state[f"msg_{selected_work_team}_multi_v_ss"].replace("{total}", str(total_devices))
                    else:
                        indiv_base = st.session_state[f"msg_{selected_work_team}_multi_s_nn_n"].replace("{total}", str(total_devices))
                        
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
                
                st.write(f"💬 최종 전송 문구 미리보기 (기기 {total_devices}대 파악됨)")
                st.code(final_msg, language=None)
                st.markdown("<br>", unsafe_allow_html=True)
                
    elif analyze_clicked:
        st.warning("⚠️ 붙여넣은 카톡 정산 내역이 없습니다. 내용을 복사해 넣어주세요.")
