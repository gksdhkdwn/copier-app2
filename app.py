import streamlit as st
import re
import urllib.parse

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="퍼스트전산 마감 도우미",
    page_icon="📱",
    layout="wide"
)

st.title("퍼스트전산 마감 도우미 📱")
st.caption("마감 문자를 대량 생성합니다.")

# 2. 안내 문구 기본값 정의
txt_sindo = (
    "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → "
    "목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. "
    "인쇄물 캡쳐본 문자로 부탁드립니다."
)
txt_ecosys = (
    "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 "
    "누르신 후 → 리포트 → 리포트 인쇄 → "
    "스테이터스페이지 인쇄 하시면 출력물이 나옵니다. "
    "캡쳐 후 문자로 부탁드립니다."
)
txt_305 = (
    "1. 기계확인/사양설정 → 2. 리포트 → "
    "프린터사용량 ok 누르신 후 "
    "리포트 캡쳐본 문자로 부탁드립니다."
)
txt_5473 = (
    "사용량확인차 문자남겼습니다 확인방법 - "
    "장치설정 > 보고서 > 시스템 > 인쇄집계결과 > "
    "예 > 확인 누르면 출력물 하나 나옵니다 "
    "출력물 사진찍어서 문자발송 부탁드립니다."
)
txt_apeos = (
    "기계확인 버튼 → 사용매수 확인 눌러서 "
    "일련번호와 현재사용매수 나온 화면 "
    "캡쳐 후 문자로 부탁드립니다."
)
txt_5700 = (
    "(오른쪽 위) 연장 표시 → 모든 설정 → "
    "(밑으로 내리고) 보고서 인쇄 → (밑으로) "
    "프린터 설정 (4장 중에 3 페이지만 문자)"
)
txt_l5100 = (
    "+ 누르면 Machine info 누르고 ok → "
    "Print settings ok 누른 후 go(시작버튼) "
    "누르셔서 나오는 4장 중 3번째 장만 문자"
)
txt_ricoh = (
    "사용자도구 클릭 → 카운터 클릭 → "
    "카운터 목록인쇄클릭 "
    "(인쇄물 출력 후 발송 부탁드립니다.)"
)
txt_5005 = (
    "사양설정 > 리포트 > 기능설정리스트 "
    "확인 후 문자로 부탁드립니다."
)
txt_x3220 = (
    "기기 우측 버튼 보시면 카운터 누름 -> "
    "화면 인쇄 버튼 클릭하여 확인 후 "
    "문자로 부탁드립니다."
)
txt_samsung = (
    "설정 → 왼쪽 축 내리다보면 리포트 누름 → "
    "오른쪽 사용량 정보 클릭하여 확인 후 "
    "문자로 부탁드립니다."
)
txt_default = (
    "기기 화면의 카운터 메뉴에서 사용량 "
    "확인 후 사진 한 장만 문자나 카톡으로 "
    "발송 부탁드립니다."
)

# 3. 안전한 세션 독립 구조 세팅
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
        "N500": txt_sindo, "N501": txt_sindo,
        "N502": txt_sindo, "N600": txt_sindo,
        "N601": txt_sindo, "D320": txt_sindo,
        "D400": txt_sindo, "D410": txt_sindo,
        "D420": txt_sindo, "D450": txt_sindo,
        "D460": txt_sindo, "D470": txt_sindo,
        "MA2100": txt_ecosys, "M5526": txt_ecosys,
        "M5521": txt_ecosys, "ECOSYS": txt_ecosys,
        "305": txt_305, "5473": txt_5473,
        "C2263": txt_apeos, "C2265": txt_apeos,
        "C2061": txt_apeos, "C3067": txt_apeos,
        "C2260": txt_apeos, "C2270": txt_apeos,
        "C2275": txt_apeos, "C3375": txt_apeos,
        "C4475": txt_apeos, "C5575": txt_apeos,
        "C2271": txt_apeos, "C2273": txt_apeos,
        "C3371": txt_apeos, "C3373": txt_apeos,
        "C3070": txt_apeos, "C3570": txt_apeos,
        "C4570": txt_apeos, "C5570": txt_apeos,
        "C7070": txt_apeos, "Apeos": txt_apeos,
        "5700": txt_5700, "L5100": txt_l5100,
        "2554": txt_ricoh, "C3003": txt_ricoh,
        "C4504": txt_ricoh, "5005": txt_5005, 
        "X3220NR": txt_x3220, "X-9201": txt_x3220, 
        "SL-": txt_samsung, "기본 기종": txt_default
    }

# 4. 상단 탭 구성
tabs = st.tabs([
    "📝 마감 문자 대량 작성", 
    "⚙️ 기종별 카운터 방법 사전"
])

with tabs[0]:
    raw_text = st.text_area(
        "카톡 내용 붙여넣기:", 
        height=250
    )
    
    if raw_text:
        raw_blocks = re.split(
            r'(\[.*?\]|【.*?】)', 
            raw_text
        )
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
            
        valid_blocks = [
            b.strip() for b in blocks 
            if len(b.strip()) > 5
        ]
        if not valid_blocks:
            valid_blocks = [raw_text.strip()]

        # [수정] 절대로 잘리지 않도록 안전하게 분할 포맷팅 처리
        total_cnt = len(valid_blocks)
        title_text = f"🔍 목록 (총 {total_cnt}건)"
        st.subheader(title_text)
        
        machine_options = list(
            st.session_state.custom_formats.keys()
        )
        exclude_machines = ["기본 기종", "X3220NR", "X-9201", "SL-"]
        
        for i, block in enumerate(valid_blocks, 1):
            with st.container():
                # 연락처 추출
                p_matches = re.findall(
                    r'01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}', 
                    block
                )
                detected_phone = (
                    p_matches[0] if p_matches else ""
                )
                
                # 업체명 추출
                lines = [
                    l.strip() for l in block.split('\n') 
                    if l.strip()
                ]
                
                has_bracket = False
                if lines:
                    if '[' in lines[0] or '【' in lines[0]:
                        has_bracket = True
                        
                if lines and len(lines) > 1 and has_bracket:
                    detected_name = lines[1]
                elif lines:
                    detected_name = lines[0]
                else:
                    detected_name = "거래처 확인 바람"
                
                # 기종 자동 매칭
                matched_machine = "기본 기종"
                block_lower = block.lower()
                
                if "9201" in block_lower:
                    matched_machine = "X-9201"
                elif "3220" in block_lower:
                    matched_machine = "X3220NR"
                elif "sl-" in block_lower:
                    matched_machine = "SL-"
                else:
                    for k in machine_options:
                        if k not in exclude_machines and k.lower() in block_lower:
                            matched_machine = k
                            break
                
                # 위젯 ID 중복 방지 입력 UI
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    u_name = st.text_input(
                        f"업체명 ({i})", 
                        value=detected_name, 
                        key=f"nm_{i}_{matched_machine}"
                    )
                with col2:
                    u_phone = st.text_input(
                        f"연락처 ({i})", 
                        value=detected_phone, 
                        key=f"ph_{i}_{matched_machine}"
                    )
                with col3:
                    if matched_machine in machine_options:
                        d_idx = machine_options.index(
                            matched_machine
                        )
                    else:
                        d_idx = machine_options.index(
                            "기본 기종"
                        )
                    u_machine = st.selectbox(
                        f"기종 ({i})", 
                        options=machine_options, 
                        index=d_idx, 
                        key=f"mc_{i}_{matched_machine}"
                    )
                
                # 세션 연동 문구 처리
                how = st.session_state.custom_formats.get(
                    u_machine, txt_default
                )
                
                is_long_txt = (
                    "안녕하세요" in how or 
                    "사용량확인차" in how
                )
                if is_long_txt:
                    final_msg = (
                        f"{how}\n(기종: {u_machine})\n"
                        f"매번 번거롭게 해드려
