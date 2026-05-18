import streamlit as st
import re

st.set_page_config(
    page_title="퍼스트전산 마감 도우미", 
    page_icon="📱", 
    layout="wide"
)
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 정확한 마감 문자를 대량 생성합니다.")

# 기종별 데이터 기본 세팅
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
        # 하이픈 포함 010 번호 추출 정규식 보완
        phone_pattern = r'(01[016789][-.\s]?\d{3,4}[-.\s]?\d{4})'
        
        # [송파구], 【수도권】 같은 지역 대괄호 기준으로 덩어리를 1차 분리해봅니다.
        # 만약 대괄호가 없으면 기존처럼 폰번호 기준으로 분리합니다.
        raw_blocks = re.split(r'(\[.*?\]|【.*?】)', raw_text)
        
        blocks = []
        current_block = ""
        
        for part in raw_blocks:
            if re.match(r'(\[.*?\]|【.*?】)', part):
                if current_block.strip():
                    blocks.append(current_block.strip())
                current_block = part
            else:
                current_block += part
        if current_block.strip():
            blocks.append(current_block.strip())
            
        # 만약 대괄호 기준으로 분리가 전혀 안 되었다면 원본 텍스트를 통째로 하나로 처리
        if len(blocks) <= 1:
            blocks = [raw_text.strip()]

        st.subheader(f"🔍 자동 생성된 마감 문자 목록 (총 {len(blocks)}건)")
        
        for i, block in enumerate(blocks, 1):
            if not block.strip():
                continue
                
            with st.container():
                # 블록 내에서 휴대폰 번호 찾기 (하이픈 있어도 매칭 가능)
                phone_match = re.search(phone_pattern, block)
                phone = phone_match.group(1) if phone_match else "연락처 없음"
                
                # 대소문자 상관없이 기종 포함 여부 체크 (예: SL-X3220NR 안에 X3220이 있는지 감지)
                matched_machine = "기본 기종"
                for k in st.session_state.custom_formats.keys():
                    if k != "기본 기종" and k.lower() in block.lower():
                        matched_machine = k
                        break
                
                col1, col2 = st.columns(2)
                with col1:
                    u_phone = st.text_input(
                        f"수신 연락처 ({i})", 
                        value=phone, 
                        key=f"phone_{i}"
                    )
                with col2:
                    u_machine = st.selectbox(
                        f"자동 인식된 기종 ({i})", 
                        options=list(st.session_state.custom_formats.keys()), 
                        index=list(st.session_state.custom_formats.keys()).index(matched_machine),
                        key=f"mach_{i}"
                    )
                
                formats_dict = st.session_state.custom_formats
                how_to_print = formats_dict.get(u_machine, formats_dict["기본 기종"])
                
                if "안녕하세요" in how_to_print or "안녕하십니까" in how_to_print:
                    final_msg = f"{how_to_print}\n- 기종: {u_machine}\n매번 번거롭게 해드려 죄송합니다."
                else:
                    final_msg = (
                        f"안녕하세요 퍼스트 전산입니다\n"
                        f"마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다\n"
                        f"카운터 한장만 보내주시면 감사하겠습니다\n"
                        f"({u_machine}) - {how_to_print}\n"
                        f"매번 번거롭게 해드려 죄송합니다"
                    )
                
                st.text_area(
                    f"💬 최종 복사용 문구 미리보기 ({i})", 
                    value=final_msg, 
                    height=130, 
                    key=f"msg_{i}"
                )
                st.markdown("---")

with tabs[1]:
    st.subheader("⚙️ 등록된 퍼스트전산 기종별 사전 리스트")
    
    for machine_type, method_text in list(st.session_state.custom_formats.items()):
        col_k, col_v = st.columns([1, 3])
        with col_k:
            st.markdown(f"**{machine_type}**")
        with col_v:
            st.session_state.custom_formats[machine_type] = st.text_area(
                f"'{machine_type}' 확인 방법", 
                value=method_text, 
                key=f"setting_{machine_type}", 
                height=70
            )
            
    st.markdown("#### ➕ 추후 새로운 기종이 늘어나면 등록하는 곳")
    new_mach = st.text_input("새로운 기종 이름 입력 (예: C2260)")
    new_method = st.text_area(
        "해당 기종의 카운터 확인 방법 설명", 
        value="[메뉴] 버튼 클릭 후 화면상의 카운터를 확인하세요."
    )
    if st.button("사전에 기종 추가하기"):
        if new_mach:
            st.session_state.custom_formats[new_mach] = new_method
            st.rerun()
