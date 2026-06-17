import streamlit as st
import re
import urllib.parse
import json
import os
from collections import OrderedDict

# 1. 페이지 기본 설정 및 핸드폰 화면 최적화 CSS
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

st.markdown(
    """
    <style>
    div[data-testid="stTextArea"] textarea {
        overflow-y: hidden !important;
        height: auto !important;
        min-height: 120px !important;
        max-height: none !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

SETTINGS_FILE = "message_settings.json"

# 2. 안내 문구 및 설정 기본값 정의
default_settings = {
    # 단일 기기 등급별 분리 양식
    "txt_single_v_ss": "안녕하세요 퍼스트 전산입니다.\n세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다.\n카운터 한장만 보내주시면 감사하겠습니다.\n바쁘시겠지만 협조 부탁드립니다.",
    "txt_single_s_nn_n": "안녕하세요 퍼스트 전산입니다.\n세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다.\n카운터 한장만 보내주시면 감사하겠습니다.",
    
    # 여러 기기 등급별 분리 양식
    "txt_multi_v_ss": "안녕하세요 퍼스트 전산입니다.\n세금계산서 발행을 위해 보유하신 총 {total}대 기기의 마감 카운터 사진이 필요하여 연락드렸습니다.\n각 기기별 카운터 한장씩 확인 후 사진 전송을 부탁드립니다.\n감사합니다.",
    "txt_multi_s_nn_n": "안녕하세요 퍼스트 전산입니다.\n세금계산서 발행을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다.\n각 기기별 카운터 한장씩 보내주시면 감사하겠습니다.",
    
    # 기종별 기본 설명 사전
    "txt_sindo": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
    "txt_ecosys": "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다.",
    "txt_305": "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다.",
    "txt_5473": "사용량확인차 문자남겼습니다\n확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다.",
    "txt_apeos": "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다.",
    "txt_5700": "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4장 출력) 나온 종이 사진 찍어서 보내주세요."
}

# 설정 파일 로드 함수
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # 신규 필드가 없을 경우를 대비해 기본값 병합
                for k, v in default_settings.items():
                    if k not in saved:
                        saved[k] = v
                return saved
        except:
            return default_settings
    return default_settings

# 설정 파일 저장 함수
def save_settings(settings_dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

# 세션 상태에 설정 데이터 보관
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

# 3. 탭 메뉴 구성 (기존 레이아웃 엄격히 유지)
tab1, tab2 = st.tabs(["📋 마감 문자 작성", "⚙️ 기종 및 등급별 문구 설정"])

# 데이터 클렌징 및 정밀 파싱 함수 (직급 없는 이름 완벽 대응)
def parse_kakao_text(text):
    lines = text.strip().split("\n")
    records = []
    
    # 기종 인식을 위한 키워드 정의
    machine_map = {
        "신도": "신도", "sindo": "신도",
        "에코시스": "에코시스", "ecosys": "에코시스",
        "305": "305",
        "5473": "5473",
        "apeos": "Apeos", "아페오스": "Apeos",
        "5700": "5700"
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 정규식으로 전화번호 찾기
        phone_match = re.search(r"(\d{2,3}-\d{3,4}-\d{4})", line)
        if not phone_match:
            continue
            
        phone = phone_match.group(1)
        
        # 전화번호 기준 앞부분과 뒷부분 분할분석
        phone_start_idx = line.find(phone)
        part_before = line[:phone_start_idx].strip()
        part_after = line[phone_start_idx + len(phone):].strip()
        
        # 1. 업체명 추출 (보통 줄 맨 앞 단어)
        tokens_before = part_before.split()
        if tokens_before:
            company = tokens_before[0]
            # 숫자 순번 제거 (예: '1.', '2)' 등)
            company = re.sub(r"^\d+[\.\s\)]+", "", company)
        else:
            company = "고객사"
            
        # 등급 자동 판별 (V, SS 포함 여부 체크)
        comp_upper = company.upper()
        if "V" in comp_upper or "SS" in comp_upper:
            detected_grade = "V/SS급"
        else:
            detected_grade = "S/NN/N급"
            
        # 2. 이름 및 직급 파싱 (번호 뒷부분을 최우선 정밀 분석)
        name = ""
        title = ""
        tokens_after = part_after.split()
        
        # 직급 리스트 사전 정의
        known_titles = ["사장", "대표", "대리", "과장", "부장", "차장", "주임", "계장", "실장", "팀장", "소장", "직원", "담당자", "총무", "기사님", "님"]
        
        if tokens_after:
            # 번호 바로 뒤 첫 단어가 기종 키워드가 아니라면 이름 또는 이름+직급으로 추정
            first_token = tokens_after[0]
            is_machine_kw = any(k in first_token.lower() for k in machine_map.keys())
            
            if not is_machine_kw:
                # 패턴 A: '홍길동대리' 처럼 붙어있는 경우 처리
                title_found = False
                for t_title in known_titles:
                    if t_title in first_token and first_token.index(t_title) > 1:
                        idx = first_token.index(t_title)
                        name = first_token[:idx]
                        title = first_token[idx:]
                        title_found = True
                        break
                
                # 패턴 B: '홍길동 대리' 또는 '홍길동' 처럼 직급이 없거나 떨어진 경우
                if not title_found:
                    # 한글/영문 2~4글자 범위면 이름으로 간주
                    if re.match(r"^[가-힣a-zA-Z]{2,4}$", first_token):
                        name = first_token
                        # 그 다음 단어가 직급 사전에 있는지 검사
                        if len(tokens_after) > 1 and tokens_after[1] in known_titles:
                            title = tokens_after[1]
        
        # 번호 뒷부분에서 이름을 못 찾았을 때 번호 앞부분 패자부활전 분석
        if not name and len(tokens_before) > 1:
            for tok in tokens_before[1:]:
                if re.match(r"^[가-힣a-zA-Z]{2,4}$", tok) and not any(k in tok.lower() for k in machine_map.keys()):
                    name = tok
                    break
                    
        # 3. 기종 매핑 추출
        machine_type = "기본 기종"
        for kw, official_name in machine_map.items():
            if kw.lower() in line.lower():
                machine_type = official_name
                break
                
        records.append({
            "company": company,
            "phone": phone,
            "name": name,
            "title": title,
            "machine": machine_type,
            "grade": detected_grade
        })
        
    return records

# ==================== TAB 1: 마감 문자 작성 화면 ====================
with tab1:
    st.title("퍼스트전산 마감 도우미 📱")
    st.caption("카톡 내용을 복사해 넣으면 번호와 이름(직급유무 무관)을 정확히 인식해 등급별 마감 문자를 생성합니다.")
    
    # 세션 기반 입력창 데이터 보존 처리
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
        
    raw_text = st.text_area(
        "카카오톡 정산 및 마감 명단을 아래에 붙여넣으세요:",
        value=st.session_state.input_text,
        placeholder="예시:\n1. V삼정건설 홍길동 010-1234-5678 신도\n2. 일반테크 김철수 과장 010-9876-5432 에코시스",
        key="text_area_input"
    )
    st.session_state.input_text = raw_text
    
    # 입력 초기화 버튼 구현
    if st.button("🗑️ 입력 내용 전체 초기화"):
        st.session_state.input_text = ""
        st.rerun()
        
    if raw_text.strip():
        parsed_items = parse_kakao_text(raw_text)
        
        if not parsed_items:
            st.warning("⚠️ 인식 가능한 전화번호 패턴을 찾지 못했습니다. 번호 형식을 확인해주세요. (예: 010-1234-5678)")
        else:
            # 동일 전화번호(담당자) 기준 그룹화 처리 (문자 통합 발송 기능)
            grouped_data = OrderedDict()
            for item in parsed_items:
                ph = item["phone"]
                if ph not in grouped_data:
                    grouped_data[ph] = {
                        "company": item["company"],
                        "name": item["name"],
                        "title": item["title"],
                        "grade": item["grade"],
                        "machines": []
                    }
                grouped_data[ph]["machines"].append(item["machine"])
                
            st.success(f"🎯 총 {len(grouped_data)}명의 담당자 마감 문구가 통합 변환되었습니다.")
            st.write("---")
            
            # 루프를 돌며 각 업체별 미리보기 창 렌더링
            for idx, (phone, info) in enumerate(grouped_data.items()):
                comp = info["company"]
                nm = info["name"]
                tt = info["title"]
                auto_grade = info["grade"]
                machines = info["machines"]
                total_machines = len(machines)
                
                # 직급 유무에 따른 동적 성함 문구 바인딩 (직급 없어도 이름만 있으면 출력 완료)
                greeting_name = ""
                if nm:
                    if tt:
                        greeting_name = f"{nm} {tt}님 "
                    else:
                        greeting_name = f"{nm}님 "
                
                # 등급 양식 선택 스위치 세션 보존형 정의 (단일/여러기기 급대로 2가지 선택 완벽 구현)
                grade_key = f"select_grade_{phone}_{idx}"
                if grade_key not in st.session_state:
                    st.session_state[grade_key] = "🔴 높은 등급 문구 (V, SS급)" if auto_grade == "V/SS급" else "🔵 일반 등급 문구 (S, NN, N급 및 일반)"
                
                # 가로 레이아웃 정렬로 선택 버튼 배치
                col1, col2 = st.columns([2, 5])
                with col1:
                    st.markdown(f"### **{comp}**")
                    st.caption(f"📞 {phone} | 👤 {greeting_name if greeting_name else '직원미지정'}")
                with col2:
                    chosen_grade_ui = st.radio(
                        "문구 양식 등급 강제 선택:",
                        options=["🔴 높은 등급 문구 (V, SS급)", "🔵 일반 등급 문구 (S, NN, N급 및 일반)"],
                        key=grade_key,
                        horizontal=True
                    )
                
                # 선택된 등급에 부합하는 동적 마감 뼈대 본문 선택
                s = st.session_state.settings
                if total_machines == 1:
                    # 단일 기기 케이스
                    base_msg = s["txt_single_v_ss"] if "높은 등급" in chosen_grade_ui else s["txt_single_s_nn_n"]
                else:
                    # 여러 기기 케이스
                    base_msg = s["txt_multi_v_ss"] if "높은 등급" in chosen_grade_ui else s["txt_multi_s_nn_n"]
                    base_msg = base_msg.replace("{total}", str(total_machines))
                
                # 기본 본문 첫머리에 고객 성함 웰컴 안내 믹싱 처리
                if greeting_name and "안녕하세요" in base_msg:
                    base_msg = base_msg.replace("안녕하세요", f"안녕하세요 {greeting_name.strip()}")
                
                # 하단부 복사기 기종별 정밀 카운터 설명 결합 로직
                if total_machines == 1:
                    m_type = machines[0]
                    # 사전 매핑 코드 조회
                    if m_type == "신도": how_txt = s["txt_sindo"]
                    elif m_type == "에코시스": how_txt = s["txt_ecosys"]
                    elif m_type == "305": how_txt = s["txt_305"]
                    elif m_type == "5473": how_txt = s["txt_5473"]
                    elif m_type == "Apeos": how_txt = s["txt_apeos"]
                    elif m_type == "5700": how_txt = s["txt_5700"]
                    else: how_txt = "카운터 화면 사진을 찍어서 보내주세요."
                    
                    final_message = f"{base_msg}\n\n▶ 기종: {m_type}\n▶ 방법: {how_txt}\n\n매번 번거롭게 해드려 죄송합니다."
                else:
                    # 여러 대의 기기 통합 안내문 생성
                    final_message = f"{base_msg}\n\n📌 고객님께서 사용 중인 기기 목록 (총 {total_machines}대):\n"
                    for m_idx, m_type in enumerate(machines, 1):
                        if m_type == "신도": how_txt = s["txt_sindo"]
                        elif m_type == "에코시스": how_txt = s["txt_ecosys"]
                        elif m_type == "305": how_txt = s["txt_305"]
                        elif m_type == "5473": how_txt = s["txt_5473"]
                        elif m_type == "Apeos": how_txt = s["txt_apeos"]
                        elif m_type == "5700": how_txt = s["txt_5700"]
                        else: how_txt = "카운터 사진을 부탁드립니다."
                        
                        final_message += f"\n{m_idx}. {m_type}:\n   → {how_txt}\n"
                    final_message += "\n매번 번거롭게 해드려 죄송합니다."
                
                # 최종 조립 결과 대형 텍스트 영역에 표출 (모바일 복사 최적화)
                st.text_area(f"변환된 완성형 문자 (전체선택 Ctrl+A 후 복사 가능)", value=final_message, key=f"final_area_{phone}_{idx}", height=220)
                
                # 모바일 스마트폰 다이렉트 연동 링크 원클릭 제공
                encoded_text = urllib.parse.quote(final_message)
                sms_href = f"sms:{phone}?body={encoded_text}"
                st.markdown(f'<a href="{sms_href}" style="display:inline-block; padding:8px 16px; background-color:#25D366; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📱 모바일 문자 전송창 열기</a>', unsafe_allow_html=True)
                st.write("---")

# ==================== TAB 2: 문자 양식 및 기종 설정 ====================
with tab2:
    st.subheader("⚙️ 문자 발송 기본 양식 사전 설정")
    st.write("단일기기와 여러기기 보유 업체 유형별로 등급 문구를 개별적으로 관리할 수 있습니다.")
    
    s = st.session_state.settings
    
    # 2열 분할 레이아웃으로 효율적인 양식 편집창 배치
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("#### **[단일 기기] 기본 문구 설정**")
        new_single_v_ss = st.text_area("🔴 단일 기기 - V, SS급 최고존엄 기본 문구", value=s["txt_single_v_ss"], height=130)
        new_single_s_nn_n = st.text_area("🔵 단일 기기 - S, NN, N급 및 일반 기본 문구", value=s["txt_single_s_nn_n"], height=130)
        
    with sc2:
        st.markdown("#### **[여러 기기] 기본 문구 설정**")
        st.caption("※ `{total}` 표기 자리에 기기 대수가 숫자로 자동 변환되어 들어갑니다. 절대로 지우지 마세요!")
        new_multi_v_ss = st.text_area("🔴 여러 기기 - V, SS급 최고존엄 기본 문구", value=s["txt_multi_v_ss"], height=130)
        new_multi_s_nn_n = st.text_area("🔵 여러 기기 - S, NN, N급 및 일반 기본 문구", value=s["txt_multi_s_nn_n"], height=130)
        
    st.write("---")
    st.markdown("#### **⚙️ 복사기 기종별 카운터 확인법 문구 사전**")
    
    # 기종별 안내 문구 렌더링
    new_sindo = st.text_area("▶ 신도리코 (sindo)", value=s["txt_sindo"], height=80)
    new_ecosys = st.text_area("▶ 교세라 에코시스 (ecosys)", value=s["txt_ecosys"], height=80)
    new_305 = st.text_area("▶ 신도리코 305급", value=s["txt_305"], height=80)
    new_5473 = st.text_area("▶ 삼성 5473 계열", value=s["txt_5473"], height=80)
    new_apeos = st.text_area("▶ 후지제록스 아페오스 (Apeos)", value=s["txt_apeos"], height=80)
    new_5700 = st.text_area("▶ 제록스 5700 계열", value=s["txt_5700"], height=80)
    
    # 변경 내용 일괄 세이브 디스크 저장 버튼 구현
    if st.button("💾 기종 및 등급별 모든 설정값 영구 저장하기"):
        updated_settings = {
            "txt_single_v_ss": new_single_v_ss,
            "txt_single_s_nn_n": new_single_s_nn_n,
            "txt_multi_v_ss": new_multi_v_ss,
            "txt_multi_s_nn_n": new_multi_s_nn_n,
            "txt_sindo": new_sindo,
            "txt_ecosys": new_ecosys,
            "txt_305": new_305,
            "txt_5473": new_5473,
            "txt_apeos": new_apeos,
            "txt_5700": new_5700
        }
        if save_settings(updated_settings):
            st.session_state.settings = updated_settings
            st.success("✅ 설정이 파일(`message_settings.json`)에 안전하게 저장되었습니다! 즉시 반영됩니다.")
        else:
            st.error("❌ 저장 도중 오류가 발생했습니다. 권한을 확인해주세요.")
