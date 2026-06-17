import streamlit as st
import re
import urllib.parse
import json
import os
from collections import OrderedDict

# 1. 페이지 기본 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

# 핸드폰 화면에서 입력창 스크롤이 갇히지 않도록 높이를 자동 조절하는 CSS
st.markdown(
    """
    <style>
    div[data-testid="stTextArea"] textarea {
        overflow-y: hidden !important;
        height: auto !important;
        min-height: 150px !important;
        max-height: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. 문자 양식 기본값 정의 (요청하신 문구 반영)
default_high_msg = (
    "안녕하세요 퍼스트 전산입니다. 세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다. "
    "카운터 한장만 보내주시면 감사하겠습니다."
)
default_normal_msg = (
    "안녕하세요 퍼스트 전산입니다. 세금계산서 발행을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다. "
    "각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
)

# 기종별 기본 안내 문구
txt_sindo = "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다."
txt_ecosys = "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다."
txt_305 = "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다."
txt_5473 = "사용량확인차 문자남겼습니다 확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다."
txt_apeos = "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다."
txt_5700 = "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4번째) 누르고 시작 누르면 나옵니다. 캡쳐 후 문자로 보내주세요."
txt_default = "마감 카운터 사진 한 장 사진 찍어서 문자로 전송 부탁드립니다."

# 3. 🚨 [버그 해결 핵심] 세션 상태 안전하게 초기화 (최초 1회만 실행됨)
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

# 기종 리스트 정의
machine_options = list(st.session_state['custom_formats'].keys())

# 상단 탭 구성
tab1, tab2 = st.tabs(["📋 마감 문자 작성", "⚙️ 등급별 & 기종별 양식 설정"])

# ==========================================
# 탭 2: 등급별 및 기종별 양식 설정 (버그 잡은 구역)
# ==========================================
with tab2:
    st.header("⚙️ 문자 양식 및 기종 설정")
    st.subheader("1. 등급별(지역 그룹별) 기본 문자 설정")
    st.caption("업체명 앞에 포함된 글자(V, SS 등)를 인식하여 자동으로 아래 문구가 적용됩니다. (공통지역 삭제 완료)")
    
    # 세션 상태와 연동하여 입력창 유지
    input_high = st.text_area("🔴 높은 등급 양식 (업체명에 V, SS 포함 시)", value=st.session_state['high_group_msg'], height=100)
    input_normal = st.text_area("🔵 일반 등급 양식 (업체명에 S, NN, N 포함 혹은 그 외)", value=st.session_state['normal_group_msg'], height=100)
    
    st.subheader("2. 복사기 기종별 카운터 확인 방법 설정")
    temp_formats = {}
    for m_name, m_text in st.session_state['custom_formats'].items():
        temp_formats[m_name] = st.text_area(f"📟 {m_name} 안내 문구", value=m_text, height=80, key=f"cfg_{m_name}")
        
    # 💾 안전하게 저장하기 버튼 로직 (새로고침되어도 초기화 안 됨)
    if st.button("💾 설정 내용 안전하게 저장하기", type="primary"):
        st.session_state['high_group_msg'] = input_high
        st.session_state['normal_group_msg'] = input_normal
        st.session_state['custom_formats'] = temp_formats
        st.success("🎉 모든 설정이 안전하게 저장되었습니다! 이제 첫 화면으로 돌아가도 데이터가 유지됩니다.")
        st.rerun()

# ==========================================
# 탭 1: 마감 문자 작성 (메인 UI 구역)
# ==========================================
with tab1:
    st.title("퍼스트전산 마감 도우미 📱")
    st.caption("카톡 마감 목록을 붙여넣으면 중복 번호는 1개로 합치고 기종 목록을 예쁘게 묶어 문자를 생성합니다.")
    
    raw_input = st.text_area(
        "📝 카카오톡에서 복사한 마감 명단을 아래에 붙여넣으세요:",
        placeholder="예시:\n[홍길동] V삼정건설 010-1234-5678 (신도)\n[이순신] SS퍼스트 010-9876-5432 (교세라)",
        height=250
    )
    
    if raw_input.strip():
        # 데이터 파싱 로직
        lines = raw_input.split('\n')
        parsed_data = OrderedDict()
        
        # 정규식을 이용해 이름, 업체명, 전화번호, 기종 추출
        pattern = re.compile(r'\[([^\]]+)\]\s*([^\d\s]+(?:\s+[^\d\s]+)*)?\s*([\d-]+)\s*(?:\(([^)]+)\))?')
        
        for line in lines:
            if not line.strip():
                continue
            match = pattern.search(line)
            if match:
                manager = match.group(1).strip()
                company = match.group(2).strip() if match.group(2) else "미지정 업체"
                phone = match.group(3).strip().replace('-', '') # 하이픈 제거
                machine = match.group(4).strip() if match.group(4) else "기본 기종"
                
                if phone not in parsed_data:
                    parsed_data[phone] = {
                        "manager": manager,
                        "company": company,
                        "machines": []
                    }
                parsed_data[phone]["machines"].append(machine)
                
        if parsed_data:
            st.success(f"총 {len(parsed_data)}명의 담당자(중복 번호 통합 완료)를 추출했습니다.")
            st.write("---")
            
            # 발송 리스트 생성
            for idx, (phone, info) in enumerate(parsed_data.items(), start=1):
                comp_name = info["company"]
                machines_list = info["machines"]
                total_count = len(machines_list)
                
                # 🔍 [요청사항 반영] 업체명 앞에 붙은 등급 판별 로직
                # V 또는 SS로 시작하거나 포함하는 경우 높은 급으로 분류
                is_high_grade = False
                if re.search(r'(V|SS)', comp_name, re.IGNORECASE):
                    is_high_grade = True
                
                # UI 레이아웃 구성
                st.subheader(f"[{idx}] {comp_name} ({info['manager']} 담당자) - {phone}")
                
                # 기종 매칭 편집 구역
                selected_machines_how = []
                cols = st.columns(min(total_count, 4))
                
                for i, m_name in enumerate(machines_list):
                    with cols[i % 4]:
                        # 기존 카톡에 적혀있던 기종이 현재 기종 사전에 있으면 자동 선택
                        matched_idx = machine_options.index("기본 기종")
                        for o_idx, opt in enumerate(machine_options):
                            if m_name.lower() in opt.lower() or opt.lower() in m_name.lower():
                                matched_idx = o_idx
                                break
                        
                        u_machine = st.selectbox(
                            f"기종 {i+1} 선택",
                            options=machine_options,
                            index=matched_idx,
                            key=f"sel_{idx}_{i}"
                        )
                        # 해당 기종의 설명 가져오기
                        m_how = st.session_state['custom_formats'].get(u_machine, txt_default)
                        selected_machines_how.append((u_machine, m_how))
                
                # 🔍 [요청사항 반영] 미리보기 칸에서 유저가 2가지 양식을 직접 선택할 수 있게 버튼(라디오) 배치
                # 기본값은 업체명에 포함된 단어(V, SS)에 따라 자동으로 라디오가 먼저 체크되어 있도록 설정함
                default_radio_idx = 0 if is_high_grade else 1
                
                chosen_style = st.radio(
                    "💬 적용할 문자 양식 선택:",
                    options=["🔴 높은 등급 문구 (V, SS급)", "🔵 일반 등급 문구 (S, NN, N급 및 일반)"],
                    index=default_radio_idx,
                    key=f"style_{idx}"
                )
                
                # 선택된 스타일에 따라 상단 문구 결정
                if "높은 등급" in chosen_style:
                    base_msg = st.session_state['high_group_msg']
                else:
                    # {total} 변수가 문구 안에 있으면 실시간으로 총 대수 숫자를 채워줌
                    base_msg = st.session_state['normal_group_msg'].format(total=total_count)
                
                # 최종 통합 문자 조합
                final_msg = f"{base_msg}\n\n📌 요청 기기 목록 (총 {total_count}대):\n"
                for i, (m_type, m_instruction) in enumerate(selected_machines_how, start=1):
                    final_msg += f"{i}. 기종: {m_type}\n👉 방법: {m_instruction}\n"
                final_msg += "\n매번 번거롭게 해드려 죄송합니다."
                
                # 문자 출력창 및 복사/전송 버튼
                st.text_area("📱 완성된 마감 문자 내용", value=final_msg, height=180, key=f"txt_{idx}")
                
                # 모바일용 바로 문자 발송 링크 생성
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
        else:
            st.info("올바른 양식의 카톡 마감 데이터가 없습니다. 형식(예: [이름] 업체명 전화번호 (기종))을 확인해 주세요.")
