import streamlit as st
import re

st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 업체명 없이 기종과 카운터 추출법을 매칭하여 정확한 마감 문자를 생성합니다.")

# 세션 상태 초기화 (사장님이 주신 정확한 문구와 기종별 뽑는 방법을 기본값으로 세팅)
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
        "X3220": "기기 정면의 [카운터] 버튼을 누르시면 화면에 출력됩니다.",
        "C3525": "[메뉴] -> [카운터]를 터치하시면 화면에서 확인 가능합니다.",
        "기본 기종": "기기 화면의 카운터 메뉴에서 확인해 주시면 감사하겠습니다."
    }

tabs = st.tabs(["📝 마감 문자 대량 작성", "⚙️ 기종별 카운터 방법 설정"])

with tabs[0]:
    raw_text = st.text_area(
        "카톡방에서 복사한 내용을 여기에 통째로 붙여넣으세요:", 
        height=250, 
        placeholder="예시:\n【수도권C】\n26-05\n\n[강남구]\n17, 17S(주)피치스그룹코리아성동구 피치스도원매월마감\n01051381938"
    )
    
    if raw_text:
        # 1. 휴대폰 번호를 기준으로 각 업체의 텍스트 덩어리를 분리
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

        st.subheader(f"🔍 자동 생성된 문자 목록 (총 {len(blocks)}건)")
        
        # 2. 각 업체 덩어리별로 문자 조립 시작
        for i, block in enumerate(blocks, 1):
            with st.container():
                # 연락처 추출
                phone_match = re.search(phone_pattern, block)
                phone = phone_match.group(1) if phone_match else "연락처 없음"
                
                # 카톡 텍스트 분석해서 등록된 기종(X3220, C3525 등) 자동 찾기
                matched_machine = "기본 기종"
                for k in st.session_state.custom_formats.keys():
                    if k.lower() in block.lower():
                        matched_machine = k
                        break
                
                # 관리자용 화면 설정칸 (연락처 확인 및 기종 오작동시 수동 선택용)
                col1, col2 = st.columns(2)
                with col1:
                    u_phone = st.text_input(f"수신 연락처 ({i})", value=phone, key=f"phone_{i}")
                with col2:
                    u_machine = st.selectbox(
                        f"인식된 기종 선택 ({i})", 
                        options=list(st.session_state.custom_formats.keys()), 
                        index=list(st.session_state.custom_formats.keys()).index(matched_machine) if matched_machine in st.session_state.custom_formats else 0, 
                        key=f"mach_{i}"
                    )
                
                # 선택된 기종에 따른 카운터 뽑는 방법 가져오기
                how_to_print = st.session_state.custom_formats.get(u_machine, st.session_state.custom_formats["기본 기종"])
                
                # 사장님이 요청하신 정확한 문구 포맷으로 조립
                final_msg = (
                    f"안녕하세요 퍼스트 전산입니다\n"
                    f"마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다\n"
                    f"카운터 한장만 보내주시면 감사하겠습니다\n"
                    f"({u_machine}) - ({how_to_print})\n"
                    f"매번 번거롭게 해드려 죄송합니다"
                )
                
                # 최종 완성된 문자 출력 (우측 상단 복사 버튼 제공)
                st.text_area(f"💬 최종 복사용 문구 미리보기 ({i})", value=final_msg, height=140, key=f"msg_{i}")
                st.markdown("---")

with tabs[1]:
    st.subheader("⚙️ 기종별 카운터 사진 뽑는 방법 설정")
    st.write("각 복사기 기종에 맞는 '정확한 카운터 출력 방법 설명'을 여기에 적어두시면 첫 번째 탭 문자에 자동으로 들어갑니다.")
    
    for machine_type, method_text in list(st.session_state.custom_formats.items()):
        col_k, col_v = st.columns([1, 3])
        with col_k:
            st.markdown(f"**{machine_type}**")
        with col_v:
            st.session_state.custom_formats[machine_type] = st.text_area(f"'{machine_type}' 기종의 카운터 추출 방법", value=method_text, key=f"setting_{machine_type}", height=70)
            
    # 사장님이 현장에서 기종 새로 추가하실 수 있는 칸
    st.markdown("#### ➕ 새로운 기종 및 추출 방법 등록")
    new_mach = st.text_input("새로운 복사기 기종명 (예: N501)")
    new_method = st.text_area("그 기종의 카운터 확인 방법 설명", value="[메뉴] -> [카운터 확인] 버튼을 눌러주세요.")
    if st.button("새 기종 등록하기"):
        if new_mach:
            st.session_state.custom_formats[new_mach] = new_method
            st.rerun()
