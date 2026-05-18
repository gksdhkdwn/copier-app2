import streamlit as st
import re

st.set_page_config(
    page_title="퍼스트전산 마감 도우미", 
    page_icon="📱", 
    layout="wide"
)
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 세부 기종 사전과 매칭하여 정확한 마감 문자를 대량 생성합니다.")

# 안내 문구 안전하게 변수 등록
txt_sindo = "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다."
txt_ecosys = "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다."
txt_305 = "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다."
txt_5473 = "사용량확인차 문자남겼습니다 사용량 확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다."
txt_apeos = "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다."
txt_5700 = "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4장 중에 3 페이지만 문자 보냅니다.)"
txt_l5100 = "+ 누르면 Machine info 누르고 ok → Print settings ok 누른 후 go(시작버튼) 누르셔서 나오는 4장 중 3번째 장만 문자로 부탁드립니다."
txt_ricoh = "사용자도구 클릭 → 카운터 클릭 → 카운터 목록인쇄클릭 (인쇄물 출력 후 발송 부탁드립니다.)"
txt_5005 = "사양설정 > 리포트 > 기능설정리스트 확인 후 문자로 부탁드립니다."
txt_x3220 = "기기 우측 버튼 보시면 카운터 누름 -> 화면 인쇄 버튼 클릭하여 확인 후 문자로 부탁드립니다."
txt_samsung = "설정 → 왼쪽 쭉 내리다보면 리포트 누름 → 오른쪽 사용량 정보 클릭하여 확인 후 문자로 부탁드립니다."
txt_default = "기기 화면의 카운터 메뉴에서 사용량 확인 후 사진 한 장만 문자나 카톡으로 발송 부탁드립니다."

# 기종 매칭 사전 조립
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
        "N500": txt_sindo, "N501": txt_sindo, "N502": txt_sindo,
        "N600": txt_sindo, "N601": txt_sindo, "D320": txt_sindo,
        "D400": txt_sindo, "D410": txt_sindo, "D420": txt_sindo,
        "D450": txt_sindo, "D460": txt_sindo, "D470": txt_sindo,
        "MA2100": txt_ecosys, "M5526": txt_ecosys, "M5521": txt_ecosys, "ECOSYS": txt_ecosys,
        "305": txt_305, "5473": txt_5473,
        "C2263": txt_apeos, "C2265": txt_apeos, "C2061": txt_apeos, "C3067": txt_apeos,
        "C2260": txt_apeos, "C2270": txt_apeos, "C2275": txt_apeos, "C3375": txt_apeos,
        "C4475": txt_apeos, "C5575": txt_apeos, "C2271": txt_apeos, "C2273": txt_apeos,
        "C3371": txt_apeos, "C3373": txt_apeos, "C3070": txt_apeos, "C3570": txt_apeos,
        "C4570": txt_apeos, "C5570": txt_apeos, "C7070": txt_apeos, "Apeos": txt_apeos,
        "5700": txt_5700, "L5100": txt_l5100,
        "2554": txt_ricoh, "C3003": txt_ricoh, "C4504": txt_ricoh, "5005": txt_5005,
        "X3220NR": txt_x3220, "SL-": txt_samsung, "기본 기종": txt_default
    }

tabs = st.tabs(["📝 마감 문자 대량 작성", "⚙️ 기종별 카운터 방법 사전"])

with tabs[0]:
    raw_text = st.text_area(
        "카톡방에서 복사한 내용을 여기에 통째로 붙여넣으세요:", 
        height=250
    )
    
    if raw_text:
        # 대괄호([])나 【】 기준으로 거래처 블록 쪼개기
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
            
        if len(blocks) <= 1:
            blocks = [raw_text.strip()]

        st.subheader(f"🔍 자동 생성된 마감 문자 목록 (총 {len(blocks)}건)")
        
        machine_options = list(st.session_state.custom_formats.keys())
        
        for i, block in enumerate(blocks, 1):
            if not block.strip():
                continue
                
            with st.container():
                # 휴대폰 번호 추출 (하이픈 제거하고 숫자만 매칭하는 패턴까지 유연하게 처리)
                phone_matches = re.findall(r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}', block)
                detected_phone = phone_matches[0] if phone_matches else "연락처 없음"
                
                # 거래처명 추출 (첫 줄에서 지역구 제외하고 추출 시도)
                lines = [l.strip() for l in block.split('\n') if l.strip()]
                detected_name = "거래처 확인 바람"
                if lines:
                    if re.match(r'(\[.*?\]|【.*?】)', lines[0]) and len(lines) > 1:
                        detected_name = lines[1]
                    else:
                        detected_name = lines[0]
                
                # 기종 자동 매칭 로직
                matched_machine = "기본 기종"
                block_lower = block.lower()
                
                if "x3220" in block_lower:
                    matched_machine = "X3220NR"
                elif "sl-" in block_lower:
                    matched_machine = "SL-"
                else:
                    for k in machine_options:
                        if k not in ["기본 기종", "X3220NR", "SL-"] and k.lower() in block_lower:
                            matched_machine = k
                            break
                
                # 3단 UI 레이아웃 구성
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    u_name = st.text_input(f"업체명 ({i})", value=detected_name, key=f"nm_{i}")
                with col2:
                    u_phone = st.text_input(f"고객 연락처 ({i})", value=detected_phone, key=f"ph_{i}")
                with col3:
                    default_idx = machine_options.index(matched_machine) if matched_machine in machine_options else machine_options.index("기본 기종")
                    u_machine = st.selectbox(f"복사기 기종 ({i})", options=machine_options, index=default_idx, key=f"mc_{i}")
                
                how_to_print = st.session_state.custom_formats.get(u_machine, txt_default)
                
                # 최종 전송 문구 포맷 조립
                if "안녕하세요" in how_to_print or "사용량확인차" in how_to_print:
                    final_msg = f"{how_to_print}\n(기종: {u_machine})\n매번 번거롭게 해드려 죄송합니다."
                else:
                    final_msg = (
                        f"안녕하세요 퍼스트 전산입니다.\n"
                        f"마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다.\n"
                        f"카운터 한장만 보내주시면 감사하겠습니다.\n\n"
                        f"▶ 기종: {u_machine}\n"
                        f"▶ 방법: {how_to_print}\n\n"
                        f"매번 번거롭게 해드려 죄송합니다."
                    )
                
                st.text_area(f"💬 최종 발송 문구 미리보기 ({i})", value=final_msg, height=140, key=f"txt_{i}")
                st.markdown("---")

with tabs[1]:
    st.subheader("⚙️ 등록된 퍼스트전산 기종별 사전 리스트")
    machine_items = list(st.session_state.custom_formats.items())
