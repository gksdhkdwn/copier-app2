import streamlit as st
import re

st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 등록된 10대 기종 사전과 매칭하여 정확한 마감 문자를 대량 생성합니다.")

# 세션 상태 초기화 (기종별 데이터)
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
        "D410": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
        "D420": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
        "D450": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
        "D320": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
        "N501": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
        "신도": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
        "ECOSYS": "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다.",
        "305": "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다.",
        "5473": "장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예를 누르시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다.",
        "APEOS": "사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다.",
        "5700": "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (3/4 페이지) 확인 후 문자로 부탁드립니다.",
        "L5100": "+ 누르면 Machine info 누르고 ok → Print settings ok 누른 후 go(시작버튼) 누르셔서 나오는 4장 중 3번째 장만 문자로 부탁드립니다.",
        "리코": "홈화면에서 우측 가운데 어플클릭(네모) → 사용자도구 클릭 → 카운터 클릭 → 카운터 목록인쇄클릭 (인쇄물 출력 후 발송) 또는 화면에 나오는 사용매수 캡처 후 발송 부탁드립니다.",
        "5005": "사양설정 > 리포트 > 기능설정리스트 확인 후 문자로 부탁드립니다.",
        "기본 기종": "기기 화면의 카운터 메뉴에서 사용량 확인 후 사진 한 장만 문자나 카톡으로 발송 부탁드립니다."
    }

tabs = st.tabs(["📝 마감 문자 대량 작성", "⚙️ 기종별 카운터 방법 사전"])

with tabs[0]:
    raw_text = st.text_area(
        "카톡방에서 복사한 내용을 여기에 통째로 붙여넣으세요:", 
        height=250
    )
    
    if raw_text:
        phone_pattern = r'(01[016789][-.\s]?\d{3,4}[-.\s]?\d{4})'
        blocks = []
        matches = list(re.finditer(phone_pattern, raw_text))
        
        start_idx = 0
        for match in matches:
            end_idx = match.end()
            block_text = raw_text[start_idx:end_idx].strip()
            if block_text:
                blocks.append(block_text)
            start_idx = end_idx
            
        if not blocks and raw_text.strip():
            blocks = [raw_text.strip()]
        elif start_idx < len(raw_text) and raw_text[start_idx:].strip():
            if blocks:
                blocks[-1] = blocks[-1] + "\n" + raw_text[start_idx:].strip()

        st.subheader(f"🔍 자동 생성된 마감 문자 목록 (총 {len(blocks)}건)")
        
        for i, block in enumerate(blocks, 1):
            with st.container():
                phone_match = re.search(phone_pattern, block)
                phone = phone_match.group(1) if phone_match else "연락처 없음"
                
                matched_machine = "기본 기종"
                for k in st.session_state.custom_formats.keys():
                    if k.lower() in block.lower():
                        matched_machine = k
                        break
                
                col1, col2 = st.columns(2)
                with col
