import streamlit as st
import re
import urllib.parse

# 1. 페이지 기본 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 번호가 적힌 거래처만 정확하게 인식하여 마감 문자를 대량 생성합니다.")

# 핸드폰 화면 스크롤 방지 및 높이 자동 확장 CSS
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

# 2. [기존 양식 그대로] 안내 문구 기본값 정의 (단 한 글자도 수정 없음)
txt_sindo = "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다."
txt_ecosys = "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 상태페이지 선택 후 예 누르시면 한 장 나옵니다. 출력물 캡쳐 후 문자로 부탁드립니다."
txt_xerox = "기기 홈버튼 좌측(또는 우측) 인증(열쇠모양)버튼 누르시고 관리자 ID '11111' 입력 후 확정(엔터) → 기계확인(사양확인)버튼 → 리포트 설명서 인쇄 → 등록정보리포트 → 인쇄 누르시면 3장 나옵니다. 첫 장만 사진 찍어서 보내주시면 됩니다."
txt_samsung = "기기 홈화면에서 카운터(숫자로표시된것) 누르시고 사용량조회 화면 나오면 기기 상태 리포트 출력 누르시고 사용량 리포트 출력하시면 한 장 나옵니다. 출력물 사진 찍어서 문자로 부탁드립니다."
txt_hp = "기기 화면을 위에서 아래로 쓸어내리시면 톱니바퀴(설정) 버튼 나옵니다. 설정 들어가셔서 보고서 → 구성보고서 인쇄 누르시면 출력물 나옵니다. 출력물 사진 찍어서 문자로 부탁드립니다."
txt_default = "사용량 확인을 위해 복사기 카운터(사용량) 확인이 필요합니다. 화면에 나오는 카운터 숫자가 잘 보이게 사진 한 장 전송 부탁드립니다."

# 3. [기존 양식 그대로] 하단 기본 마무리 문구
txt_footer = "매번 번거롭게 해드려 죄송합니다."

# 4. 세션 상태(Session State) 버그 차단 초기화
if "custom_formats" not in st.session_state:
    st.session_state.custom_formats = {
        "신도 (D410/D420/D450 등)": txt_sindo,
        "교세라 (Ecosys 등)": txt_ecosys,
        "제록스 (V급, Ⅳ급 등)": txt_xerox,
        "삼성 (SL-X3220 등)": txt_samsung,
        "HP (이젝 등)": txt_hp,
        "기본 기종": txt_default
    }

# 지역 그룹별 상단 문구 세션 초기화 (입력값 날아가는 버그 방지)
if "msg_group_v_ss" not in st.session_state:
    st.session_state.msg_group_v_ss = "안녕하세요 퍼스트 전산입니다. 세금계산서 발행을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다."
if "msg_group_s_nn_n" not in st.session_state:
    st.session_state.msg_group_s_nn_n = "안녕하세요 퍼스트 전산입니다. 세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다. 각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."

machine_options = list(st.session_state.custom_formats.keys())

# 5. 탭 메뉴 구성 (작업 화면 / 양식 설정 화면)
tab1, tab2 = st.tabs(["📋 마감 문자 작성", "⚙️ 문자 양식 및 지역 설정"])

# ==========================================
# [TAB 2] 문자 양식 및 지역 설정 화면 (버그 수정 완)
# ==========================================
with tab2:
    st.subheader("지역 그룹별 문자 양식 설정")
    st.caption("설정 후 아래 [💾 설정 내용 안전하게 저장하기] 버튼을 누르면 절대 초기화되지 않고 유지됩니다.")
    
    # 사장님이 요청하신 지역별 그룹화 상단 문구 입력창
    input_v_ss = st.text_area(
        "■ V급 / SS급 지역 그룹 문구 (기기 총 대수 {total} 자동 적용)",
        value=st.session_state.msg_group_v_ss,
        key="input_v_ss_raw"
    )
    
    input_s_nn_n = st.text_area(
        "■ S / NN / N 지역 그룹 문구",
        value=st.session_state.msg_group_s_nn_n,
        key="input_s_nn_n_raw"
    )
    
    st.write("---")
    st.subheader("기종별 카운터 안내 문구 관리")
    
    # 기존 기종별 카운터 문구 관리창 유지
    updated_formats = {}
    for shortcut, default_val in st.session_state.custom_formats.items():
        updated_formats[shortcut] = st.text_area(f"▶ {shortcut} 안내", value=default_val, key=f"cfg_{shortcut}")
        
    # 저장 버튼 누를 때 세션 상태에 확실하게 잠금
    if st.button("💾 설정 내용 안전하게 저장하기", type="primary"):
        st.session_state.msg_group_v_ss = input_v_ss
        st.session_state.msg_group_s_nn_n = input_s_nn_n
        st.session_state.custom_formats = updated_formats
        st.success("✅ 모든 양식과 지역 설정이 안전하게 저장되었습니다! 첫 번째 탭에서 확인해 보세요.")

# ==========================================
# [TAB 1] 마감 문자 작성 (메인 화면)
# ==========================================
with tab1:
    st.subheader("카톡 내용 붙여넣기")
    raw_text = st.text_area("여기에 카카오톡 정산 또는 마감 목록 내용을 통째로 붙여넣으세요.", placeholder="여기에 내용을 입력하면 실시간으로 문자가 변환됩니다.", key="main_input_text")
    
    if raw_text.strip():
        # 연락처(숫자, 하이픈) 패턴 추출 로직
        lines = raw_text.split('\n')
        parsed_data = []
        
        for line in lines:
            if not line.strip():
                continue
            phone_match = re.findall(r'[\d-]{9,14}', line)
            if phone_match:
                clean_line = line
                for p in phone_match:
                    clean_line = clean_line.replace(p, '').strip()
                clean_line = re.sub(r'\s+', ' ', clean_line)
                
                parsed_data.append({
                    "original": line,
                    "name_info": clean_line,
                    "phones": phone_match
                })
                
        if parsed_data:
            st.write("---")
            st.success(r"f'총 {len(parsed_data)}개의 거래처 연락처를 찾았습니다.'")
            
            # 전화번호 기준으로 중복 처리하여 1개로 합치기 (통합 발송 로직)
            phone_to_items = {}
            for idx, item in enumerate(parsed_data):
                primary_phone = item["phones"][0]
                if primary_phone not in phone_to_items:
                    phone_to_items[primary_phone] = []
                phone_to_items[primary_phone].append(item)
                
            st.subheader("📱 생성된 통합 마감 문자 리스트")
            
            # 번호별로 묶인 데이터 순회하며 문자 생성
            for p_idx, (phone, group) in enumerate(phone_to_items.items()):
                total_machines = len(group)
                rep_item = group[0]
                
                # 거래처명에서 지역 추출 (V, SS, S, NN, N 판단용)
                name_text = rep_item["name_info"]
                
                # 1. 지역별 상단 인사말 선택 로직 (기존 양식 기반)
                if any(region in name_text for region in ["V급", "V", "SS급", "SS"]):
                    # V급, SS급 문구 (총 대수 반영)
                    header_msg = st.session_state.msg_group_v_ss.replace("{total}", str(total_machines))
                elif any(region in name_text for region in ["S급", "S", "NN급", "NN", "N급", "N"]):
                    # S, NN, N 문구
                    header_msg = st.session_state.msg_group_s_nn_n
                else:
                    # 매칭되는 지역이 없을 때의 기본 기본 인사말 기본값
                    header_msg = "안녕하세요 퍼스트 전산입니다.\n마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다."
                
                st.write(f"### 👤 거래처 정보: {name_text} ({phone})")
                
                # 2. 기종 선택 및 안내 본문 생성 (동일 번호 내 기기가 여러 대일 경우 묶어서 출력)
                machine_details_list = []
                
                # 화면에 기종 선택 드롭다운 띄워주기
                if total_machines > 1:
                    st.caption(f"💡 이 담당자는 총 {total_machines}대의 기기를 사용 중입니다. 각각 기종을 선택해 주세요.")
                
                for i, item in enumerate(group):
                    # 자동 기종 매칭 로직
                    d_idx = machine_options.index("기본 기종")
                    for m_opt in machine_options:
                        if m_opt != "기본 기종" and m_opt.split()[0] in item["original"]:
                            d_idx = machine_options.index(m_opt)
                            break
                            
                    # 기종 선택 셀렉트박스 (세션 충돌 방지 고유 키 적용)
                    u_machine = st.selectbox(
                        f"[{i+1}번 기기] 기종 선택 ({item['name_info'][:15]})",
                        options=machine_options,
                        index=d_idx,
                        key=f"mc_{p_idx}_{i}"
                    )
                    
                    how = st.session_state.custom_formats.get(u_machine, txt_default)
                    machine_details_list.append(f"▶ 기종: {u_machine}\n▶ 방법: {how}")
                
                # 3. 전체 문자 최종 결합 (상단인사말 + 기기별안내 + 기존 하단문구)
                all_machines_body = "\n\n".join(machine_details_list)
                final_msg = f"{header_msg}\n\n{all_machines_body}\n\n{txt_footer}"
                
                # 결과 출력창 및 바로 보내기 버튼
                st.text_area("📋 완성된 문자 내용 (그대로 복사 가능)", value=final_msg, height=250, key=f"txt_res_{p_idx}")
                
                # 모바일 바로 발송 링크 버튼
                encoded_msg = urllib.parse.quote(final_msg)
                sms_url = f"sms:{phone}?body={encoded_msg}"
                st.markdown(f'<a href="{sms_url}" target="_blank"><button style="background-color:#4CAF50; color:white; border:none; padding:10px 20px; text-align:center; text-decoration:none; display:inline-block; font-size:16px; margin:4px 2px; cursor:pointer; border-radius:8px;">📱 {phone} 번호로 문자 바로 발송하기</button></a>', unsafe_allow_html=True)
                st.write("---")
        else:
            st.info("입력된 내용에서 올바른 전화번호 형식을 찾지 못했습니다. 카톡 정산 목록을 통째로 다시 확인해 주세요.")
