import streamlit as st
import re

st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 여러 업체의 맞춤형 안내 문자를 한 번에 자동으로 만들어 드립니다.")

# 세션 상태 초기화
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
        "기본 기종": "안녕하세요 퍼스트전산입니다. {업체명} {기종} 마감 문자 발송드립니다.",
        "X3220": "안녕하세요 퍼스트전산입니다. {업체명} X3220 기종 마감일 안내입니다. 담당자 연락처: {고객연락처}"
    }

tabs = st.tabs(["📝 마감 문자 대량 작성", "⚙️ 기종 및 문구 설정"])

with tabs[0]:
    raw_text = st.text_area("카톡방에서 복사한 내용을 여기에 통째로 붙여넣으세요:", height=200, placeholder="예시:\n【수도권C】\n26-05\n\n[강남구]\n17, 17S(주)피치스그룹코리아성동구 피치스도원매월마감\n01051381938\n\n【지방A】\n[부산]\n(주)대박상사 매월마감\n01012345678")
    
    if raw_text:
        # 1. 폰번호(010...)를 기준으로 각 업체의 덩어리를 분리하는 정규식
        # 번호가 끝나고 다음 텍스트가 나오기 전까지 분할하거나, 폰번호 자체를 경계로 삼음
        blocks = []
        
        # 단순 줄바꿈이나 특정 패턴을 기준으로 데이터 파싱 시도
        # 폰번호 양식 매칭 (예: 01012345678 또는 010-1234-5678)
        phone_pattern = r'(01[016789][-.\s]?\d{3,4}[-.\s]?\d{4})'
        
        # 텍스트 내에서 모든 휴대폰 번호의 위치를 찾음
        matches = list(re.finditer(phone_pattern, raw_text))
        
        start_idx = 0
        for match in matches:
            end_idx = match.end()
            # 휴대폰 번호가 포함된 하나의 덩어리를 추출
            block_text = raw_text[start_idx:end_idx].strip()
            if block_text:
                blocks.append(block_text)
            start_idx = end_idx
            
        # 만약 번호 기준 분할이 안 되었거나 남은 텍스트가 있으면 전체를 처리하도록 보완
        if not blocks and raw_text.strip():
            blocks = [raw_text.strip()]
        elif start_idx < len(raw_text) and raw_text[start_idx:].strip():
            # 마지막 폰번호 이후에 남은 텍스트가 있다면 이전 블록에 합치거나 새로 추가
            if blocks:
                blocks[-1] = blocks[-1] + "\n" + raw_text[start_idx:].strip()

        st.subheader(r"🔍 자동 인식된 업체 목록 (총 {}건)".format(len(blocks)))
        
        # 각 블록(업체)별로 반복문 돌면서 화면에 표출
        for i, block in enumerate(blocks, 1):
            with st.container():
                st.markdown(f"### 🏢 업체 {i}")
                
                # 전화번호 추출
                phone_match = re.search(phone_pattern, block)
                phone = phone_match.group(1) if phone_match else "연락처 없음"
                
                # 가짜로 업체명과 기종 추출하는 로직 (기존 카톡 패턴 기반)
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                
                company = "알 수 없는 업체"
                machine = "기본 기종"
                
                # 괄호 나 기종명 단어 찾기
                for line in lines:
                    if '주)' in line or '(' in line or '회사' in line or '상사' in line:
                        company = line
                        break
                    elif len(line) > 3 and not re.search(phone_pattern, line) and '【' not in line and '[' not in line:
                        company = line
                
                # 기종 매칭 테스트
                for k in st.session_state.custom_formats.keys():
                    if k.lower() in block.lower():
                        machine = k
                        break
                
                # 사용자 수정 입력칸 (가로로 배치)
                col1, col2, col3 = st.columns(3)
                with col1:
                    u_company = st.text_input(f"업체명 수정 ({i})", value=company, key=f"comp_{i}")
                with col2:
                    u_phone = st.text_input(f"연락처 수정 ({i})", value=phone, key=f"phone_{i}")
                with col3:
                    u_machine = st.selectbox(f"기종 선택 ({i})", options=list(st.session_state.custom_formats.keys()), index=list(st.session_state.custom_formats.keys()).index(machine) if machine in st.session_state.custom_formats else 0, key=f"mach_{i}")
                
                # 문자 미리보기 및 복사
                fmt = st.session_state.custom_formats.get(u_machine, st.session_state.custom_formats["기본 기종"])
                final_msg = fmt.format(업체명=u_company, 고객연락처=u_phone, 기종=u_machine)
                
                st.text_area(f"📋 최종 발송 문구 미리보기 ({i}) - 아래 상자 우측 상단 버튼으로 복사 가능", value=final_msg, height=100, key=f"msg_{i}")
                st.markdown("---")

with tabs[1]:
    st.subheader("⚙️ 기종별 맞춤 문구 설정")
    st.write("여기서 기종을 추가하거나 기종별 문구를 수정할 수 있습니다.")
    
    for machine_type, text_format in list(st.session_state.custom_formats.items()):
        col_k, col_v = st.columns([1, 3])
        with col_k:
            st.markdown(f"**{machine_type}**")
        with col_v:
            st.session_state.custom_formats[machine_type] = st.text_area(f"{machine_type} 문구 양식", value=text_format, key=f"setting_{machine_type}", height=70)
            
    # 새 기종 추가
    st.markdown("#### ➕ 새 기종 추가")
    new_mach = st.text_input("새로운 기종명 (예: C3525)")
    new_fmt = st.text_area("새 기종의 문자 양식 (힌트: {업체명}, {기종}, {고객연락처} 라고 적으면 그 자리에 자동으로 들어갑니다)", value="안녕하세요 {업체명} 마감 문자입니다.")
    if st.button("기종 추가하기"):
        if new_mach:
            st.session_state.custom_formats[new_mach] = new_fmt
            st.rerun()
