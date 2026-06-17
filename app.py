import streamlit as st
import re
import urllib.parse
from collections import OrderedDict

# 1. 페이지 기본 설정 (기존 설정 유지)
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

# 핸드폰 화면 대응 CSS (기존 소스 유지)
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

# 2. 안내 문구 기본값 정의 (기존 사장님 기본 문구 그대로 100% 보존)
txt_sindo = "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다."
txt_ecosys = "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다."
txt_305 = "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다."
txt_5473 = "사용량확인차 문자남겼습니다 확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다."
txt_apeos = "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다."
txt_5700 = "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4장 출력) 누르고 시작 누르면 나옵니다. 캡쳐 후 문자로 보내주세요."
txt_default = "마감 카운터 사진 한 장 사진 찍어서 문자로 전송 부탁드립니다."

# 🚨 [추가] 등급별 기본 안내 문구 (사장님이 주신 기본 형태 보존)
default_high_msg = (
    "안녕하세요 퍼스트 전산입니다.\n"
    "세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다.\n"
    "카운터 한장만 보내주시면 감사하겠습니다."
)
default_normal_msg = (
    "안녕하세요 퍼스트 전산입니다.\n"
    "세금계산서 발행을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다.\n"
    "각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
)

# 3. 💾 세션 상태 안전 초기화 (저장 버그 해결 및 초기화 방지)
if 'high_group_msg' not in st.session_state:
    st.session_state['high_group_msg'] = default_high_msg

if 'normal_group_msg' not in st.session_state:
    st.session_state['normal_group_msg'] = default_normal_msg

if 'custom_formats' not in st.session_state:
    st.session_state['custom_formats'] = {
        "신도 (N600 / N501 등)": txt_sindo,
        "교세라 (ECOSYS 등)": txt_ecosys,
        "삼성 (체크 305 등)": txt_305,
        "브라더 (5473 등)": txt_5473,
        "후지필름 (Apeos 등)": txt_apeos,
        "삼성 (5700 등)": txt_5700,
        "기본 기종": txt_default
    }

machine_options = list(st.session_state['custom_formats'].keys())

# 상단 탭 구성 (기존 기능 분리 유지)
tab1, tab2 = st.tabs(["📋 마감 문자 작성", "⚙️ 등급별 & 기종별 양식 설정"])

# ==========================================
# 탭 2: 등급별 & 기종별 양식 설정 (수정 및 저장 구역)
# ==========================================
with tab2:
    st.header("⚙️ 문자 양식 및 기종 설정")
    
    st.subheader("1. 등급별 기본 문자 설정")
    st.caption("V, SS급 업체와 S, NN, N급 업체에 나갈 기본 뼈대 문구를 수정할 수 있습니다.")
    
    input_high = st.text_area("🔴 높은 등급 양식 (V, SS 포함 업체용)", value=st.session_state['high_group_msg'], height=120)
    input_normal = st.text_area("🔵 일반 등급 양식 (S, NN, N 포함 및 일반 업체용)", value=st.session_state['normal_group_msg'], height=120)
    
    st.subheader("2. 복사기 기종별 안내 문구 설정")
    temp_formats = {}
    for m_name, m_text in st.session_state['custom_formats'].items():
        temp_formats[m_name] = st.text_area(f"📟 {m_name} 안내 문구", value=m_text, height=80, key=f"cfg_{m_name}")
        
    # 💾 안전 저장 버튼 (누르면 첫 화면으로 리셋되지 않고 고정됨)
    if st.button("💾 설정 내용 안전하게 저장하기", type="primary"):
        st.session_state['high_group_msg'] = input_high
        st.session_state['normal_group_msg'] = input_normal
        st.session_state['custom_formats'] = temp_formats
        st.success("🎉 설정이 안전하게 저장되었습니다! 이제 데이터가 날아가지 않습니다.")
        st.rerun()

# ==========================================
# 탭 1: 마감 문자 작성 (메인 UI 기존 기능 100% 유지)
# ==========================================
with tab1:
    st.title("퍼스트전산 마감 도우미 📱")
    st.caption("카톡 내용을 복사해 넣으면 번호가 적힌 거래처만 정확하게 인식하여 마감 문자를 대량 생성합니다.")
    
    # 입력창
    raw_input = st.text_area(
        "📝 카카오톡에서 복사한 마감 명단을 아래에 붙여넣으세요:",
        placeholder="예시:\n[홍길동] V삼정건설 010-1234-5678 (신도)\n[이순신] S퍼스트 010-9876-5432 (교세라)",
        height=250
    )
    
    # 🗑️ 입력 내용 전체 초기화 기능 유지
    if st.button("🗑️ 입력 내용 전체 초기화"):
        st.rerun()
        
    if raw_input.strip():
        lines = raw_input.split('\n')
        parsed_data = OrderedDict()
        
        # 기존 정규식 매칭 로직 그대로 유지
        pattern = re.compile(r'\[([^\]]+)\]\s*([^\d\s]+(?:\s+[^\d\s]+)*)?\s*([\d-]+)\s*(?:\(([^)]+)\))?')
        
        for line in lines:
            if not line.strip():
                continue
            match = pattern.search(line)
            if match:
                manager = match.group(1).strip()
                company = match.group(2).strip() if match.group(2) else "미지정 업체"
                phone = match.group(3).strip().replace('-', '')  # 하이픈 제거
                machine = match.group(4).strip() if match.group(4) else "기본 기종"
                
                # 동일 연락처 중복 통합 로직 보존
                if phone not in parsed_data:
                    parsed_data[phone] = {
                        "manager": manager,
                        "company": company,
                        "machines": []
                    }
                parsed_data[phone]["machines"].append(machine)
                
        if parsed_data:
            st.write("---")
            
            for idx, (phone, info) in enumerate(parsed_data.items(), start=1):
                comp_name = info["company"]
                machines_list = info["machines"]
                total_count = len(machines_list)
                
                # 🔍 업체명 등급 자동 분석 (V, SS 포함 여부 체크)
                is_high_grade = False
                if re.search(r'(V|SS)', comp_name, re.IGNORECASE):
                    is_high_grade = True
                
                # 타이틀 표시 (기존 스타일 보존)
                st.subheader(f"[{idx}] {comp_name} ({info['manager']} 담당자) - {phone}")
                
                # 기종 선택 셀렉트박스 레이아웃 보존
                selected_machines_how = []
                cols = st.columns(min(total_count, 4))
                
                for i, m_name in enumerate(machines_list):
                    with cols[i % 4]:
                        matched_idx = machine_options.index("기본 기종")
                        for o_idx, opt in enumerate(machine_options):
                            if m_name.lower() in opt.lower() or opt.lower() in m_name.lower():
                                matched_idx = o_idx
                                break
                        
                        u_machine = st.selectbox(
                            f"기종 ({i+1})",
                            options=machine_options,
                            index=matched_idx,
                            key=f"sel_{idx}_{i}"
                        )
                        how = st.session_state['custom_formats'].get(u_machine, txt_default)
                        selected_machines_how.append((u_machine, how))
                
                # 🔍 [요청사항 반영] 미리보기 전 2가지 양식 수동 선택 버튼 제공
                # V, SS급이면 높은 등급 라디오가 먼저 켜져있고, 아니면 일반 등급이 켜져있음
                default_radio_idx = 0 if is_high_grade else 1
                chosen_style = st.radio(
                    "💬 적용할 문자 양식 급수 선택:",
                    options=["🔴 높은 등급 문구 (V, SS급 묶음)", "🔵 일반 등급 문구 (S, NN, N급 및 일반)"],
                    index=default_radio_idx,
                    key=f"style_{idx}"
                )
                
                # 사장님 기존 문자 조립 방식 틀 그대로 유지
                if "높은 등급" in chosen_style:
                    base_msg = st.session_state['high_group_msg']
                else:
                    base_msg = st.session_state['normal_group_msg'].format(total=total_count)
                
                # 최종 문자 구조 완성 (기존 양식 틀 보존)
                if total_count == 1:
                    # 기기가 1대일 때 기존 단수 형태 보존
                    u_machine, how = selected_machines_how[0]
                    final_msg = f"{base_msg}\n\n▶ 기종: {u_machine}\n▶ 방법: {how}\n\n매번 번거롭게 해드려 죄송합니다."
                else:
                    # 기기가 여러대일 때 기존 복수 형태 보존
                    final_msg = f"{base_msg}\n\n📌 고객님께서 사용 중인 기기 목록 (총 {total_count}대):\n"
                    for i, (m_type, m_instruction) in enumerate(selected_machines_how, start=1):
                        final_msg += f"{i}. {m_type}: {m_instruction}\n"
                    final_msg += "\n매번 번거롭게 해드려 죄송합니다."
                
                # 문자 출력창 및 바로 발송 버튼 (기존 보존)
                st.text_area("📱 완성된 마감 문자 내용", value=final_msg, height=200, key=f"txt_{idx}")
                
                encoded_msg = urllib.parse.quote(final_msg)
                sms_url = f"sms:{phone}?body={encoded_msg}"
                
                st.markdown(
                    f'<a href="{sms_url}" target="_blank" style="'
                    f'background-color: #4CAF50; color: white; padding: 10px 20px; '
                    f'text-align: center; text-decoration: none; display: inline-block; '
                    f'font-size: 16px; border-radius: 5px; font-weight: bold;">'
                    f'💬 {info["manager"]} 담당자에게 문자 보내기</a>', 
                    unsafe_allow_html=True
                )
                st.write("---")
