import streamlit as st
import re
import urllib.parse

# 1. 페이지 기본 설정 및 스타일 (와이드 모드)
st.set_page_config(page_title="퍼스트전산 마감 도우미", layout="wide")

# 모바일 환경 대응 커스텀 CSS (텍스트 에어리아 스크롤 및 꽉 차는 버튼)
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 14px !important;
    }
    div.stButton > button {
        width: 100% !important;
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 고정된 기종별 카운터 안내 문구 데이터 (기본값 설정)
DEFAULT_FORMATS = {
    "D451 / D450": "화면 우측의 [카운터] 버튼을 누르신 후 화면에 나오는 [사용량 확인] 전체 화면을 촬영해 주세요.",
    "X-9201 / X3220": "기기 조작부 우측 하단의 [카운터] 물리 버튼을 누르신 후 화면에 출력되는 카운터 정보를 촬영해 주세요.",
    "MP-C2003 / MP 2554": "[사용자도구/카운터] 클릭 ➡️ 화면의 [카운터] 클릭 ➡️ [카운터 목록인쇄]를 눌러 출력된 인쇄물을 촬영해 주세요.",
    "ECOSYS 시리즈": "기기 화면 좌측 하단 [시스템메뉴/카운터] ➡️ [리포트] ➡️ [리포트 인쇄] ➡️ [스테이터스페이지 인쇄] 후 출력물을 촬영해 주세요.",
    "N500 / N501 / N600": "[메뉴] ➡️ [카운터] 버튼을 누르신 후 화면 전체를 촬영하여 보내주세요.",
    "5700 카운터": "오른쪽 위 [연장] 표시 ➡️ [모든 설정] ➡️ [보고서 인쇄] ➡️ [프린터 설정] 출력 후 4장 중 3번째 페이지만 촬영해 주세요.",
    "L5100 시리즈": "[+] 버튼 ➡️ [Machine Info] ➡️ [OK] ➡️ [Print Settings] ➡️ [OK] ➡️ [GO(시작)] 누른 후 3번째 장을 촬영해 주세요.",
    "5005d": "[사양설정] ➡️ [리포트] ➡️ [기능설정리스트]를 눌러 출력된 화면을 촬영해 주세요."
}

# 세션 상태에 사용자 정의 포맷이 없으면 기본값으로 초기화
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = DEFAULT_FORMATS.copy()

st.title("📱 퍼스트전산 마감 도우미 (통합 발송 지원)")

# ⭐ 중요: 사장님이 말씀하신 "고칠 수 있는 뒤의 화면"을 탭 메뉴로 분리했습니다!
tabs = st.tabs(["📋 마감 문자 작성", "⚙️ 기종별 사전 리스트"])

# --- TAB 1: 마감 문자 작성 화면 ---
with tabs[0]:
    st.subheader("1. 카카오톡 마감 정보 입력")
    raw_text = st.text_area(
        "카톡방에서 복사한 마감 명단을 아래에 붙여넣어 주세요.",
        placeholder="여기에 복사한 텍스트를 붙여넣으세요...",
        height=200
    )
    
    # 입력 내용 전체 초기화 기능
    if st.button("🗑️ 입력 내용 전체 초기화", key="btn_clear_all"):
        st.rerun()

    if raw_text.strip():
        st.subheader("2. 추출 및 통합 문자 발송 목록")
        
        # 연락처(전화번호) 정규식 추출
        phone_pattern = r"010[-.\s]?\d{3,4}[-.\s]?\d{4}"
        lines = raw_text.split('\n')
        
        parsed_data = []
        current_phone = None
        current_machines = []
        
        # 텍스트 라인별 순회하며 번호 및 기종 파싱
        for line in lines:
            if not line.strip():
                continue
            
            # 연락처 탐색
            phones = re.findall(phone_pattern, line)
            if phones:
                # 새로운 번호가 나오면 이전 데이터 저장
                if current_phone and current_machines:
                    parsed_data.append({"phone": current_phone, "machines": current_machines})
                current_phone = phones[0].replace(" ", "").replace("-", "")
                current_machines = []
            
            # 현재 기종 사전 리스트에 등록된 기종이 문장에 포함되어 있는지 대조
            for machine_key in st.session_state.custom_formats.keys():
                # 다중 기종 인식을 위해 슬래시(/)나 공백 분리 매칭 지원
                sub_keys = [k.strip() for k in machine_key.split('/')]
                for sk in sub_keys:
                    if sk.lower() in line.lower() and machine_key not in current_machines:
                        current_machines.append(machine_key)
        
        # 마지막 남은 잔여 데이터 처리
        if current_phone and current_machines:
            parsed_data.append({"phone": current_phone, "machines": current_machines})
            
        # 화면에 결과 출력 및 문자 발송 링크 생성
        if not parsed_data:
            st.warning("⚠️ 텍스트에서 올바른 전화번호와 등록된 기종 정보를 찾지 못했습니다. 기종별 사전 리스트에 등록된 기명이 포함되어 있는지 확인해 주세요.")
        else:
            for idx, item in enumerate(parsed_data):
                target_phone = item["phone"]
                machines_list = item["machines"]
                
                # 문자 내용 통합 조립 시작
                msg_body = "안녕하세요, 퍼스트전산입니다.\n한 달 동안 사용하신 기기의 마감 진행을 위해 카운터 사진 요청드립니다.\n\n"
                msg_body += f"📌 고객님께서 사용 중인 기기 목록 (총 {len(machines_list)}대):\n"
                
                for i, m_key in enumerate(machines_list, 1):
                    detail_guide = st.session_state.custom_formats.get(m_key, "기기 카운터를 확인해 주세요.")
                    msg_body += f"{i}. {m_key}: {detail_guide}\n"
                
                msg_body += "\n매번 번거롭게 해드려 죄송하며, 협조해 주셔서 늘 감사드립니다! 🙏"
                
                # 개별 업체별 레이아웃 구성
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text_input(f"수신 연락처 ({idx+1})", value=target_phone, key=f"phone_show_{idx}")
                        st.text_area(f"발송될 안내 문자 미리보기 ({idx+1})", value=msg_body, height=140, key=f"msg_show_{idx}")
                    with col2:
                        st.write("")
                        st.write("")
                        # 모바일용 SMS 전송인식 링크 생성 (sms:번호?body=내용)
                        encoded_msg = urllib.parse.quote(msg_body)
                        sms_url = f"sms:{target_phone}?body={encoded_msg}"
                        
                        st.markdown(f'<a href="{sms_url}" target="_blank"><button style="width:100%; background-color:#007BFF; color:white; font-weight:bold; border-radius:8px; padding:12px; border:none; cursor:pointer;">✉️ 문자 전송하기</button></a>', unsafe_allow_html=True)
                st.markdown("---")

# --- TAB 2: 기종별 사전 리스트 관리 화면 (사장님이 찾으시던 설정창) ---
with tabs[1]:
    st.subheader("⚙️ 복사기 기종 및 문자 양식 직접 수정")
    st.info("💡 이곳에서 문구를 수정하거나 아래 칸에 기종을 새로 추가하시면, 앞의 마감 창에서 해당 기종을 인식할 때 바뀐 문구로 자동 조합됩니다.")
    
    # 기존 사전 데이터 리스트 출력 및 실시간 수정
    updated_formats = {}
    for m_name, m_guide in list(st.session_state.custom_formats.items()):
        st.markdown(f"**🔹 기종 이름: {m_name}**")
        # 입력창들의 키(Key) 이름이 겹쳐 뻗지 않도록 고유 고유 ID 부여
        new_guide = st.text_area("카운터 확인 안내 문구", value=m_guide, key=f"setting_input_{m_name}", height=70)
        updated_formats[m_name] = new_guide
    
    # 동적 업데이트 반영
    st.session_state.custom_formats = updated_formats
    
    st.markdown("---")
    st.subheader("➕ 새로운 복사기 기종 추가하기")
    
    col_add1, col_add2 = st.columns([1, 2])
    with col_add1:
        new_machine_name = st.text_input("새로운 기종 이름 입력", placeholder="예: SCX-6545")
    with col_add2:
        new_machine_guide = st.text_input("해당 기종의 카운터 확인 방법 입력", placeholder="예: 계수기 버튼을 누르고 화면을 찍어주세요.")
        
    if st.button("✨ 새 기종 사전에 등록하기", key="btn_add_new_machine"):
        if new_machine_name.strip() and new_machine_guide.strip():
            st.session_state.custom_formats[new_machine_name.strip()] = new_machine_guide.strip()
            st.success(f"✅ [{new_machine_name}] 기종이 사전에 정상적으로 추가되었습니다!")
            st.rerun()
        else:
            st.error("⚠️ 기종 이름과 안내 문구를 모두 입력한 후 버튼을 눌러주세요.")
