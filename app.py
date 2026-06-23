import streamlit as st
import re
import urllib.parse
import json
import os
import copy  # 지역별 독립적 데이터 분리를 위해 copy 모듈 도입
from collections import OrderedDict

# 1. 페이지 기본 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="wide")

# 영구 저장할 파일 경로
SETTINGS_FILE = "message_settings.json"

# 핸드폰 화면 대응 CSS (기존 소스 유지)
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

# 2. 안내 문구 및 지역 설정 기본값 정의
default_machines = {
    "신도리코": "기기 메뉴버튼 → 화면 윗쪽 카운터 버튼 → 목록인쇄 → 시작 누르시면 출력물 하나 나옵니다. 인쇄물 캡쳐본 문자로 부탁드립니다.",
    "교세라(에코시스)": "기기 화면 좌측 하단 시스템메뉴/카운터 버튼 누르신 후 → 리포트 → 리포트 인쇄 → 스테이터스페이지 인쇄 하시면 출력물이 나옵니다. 캡쳐 후 문자로 부탁드립니다.",
    "제록스 305/3055": "1. 기계확인/사양설정 → 2. 리포트 → 프린터사용량 ok 누르신 후 리포트 캡쳐본 문자로 부탁드립니다.",
    "삼성 5473/5370": "사용량확인차 문자남겼습니다 확인방법 - 장치설정 > 보고서 > 시스템 > 인쇄집계결과 > 예 > 확인 누르면 출력물 하나 나옵니다 출력물 사진찍어서 문자발송 부탁드립니다.",
    "제록스 Apeos": "기계확인 버튼 → 사용매수 확인 눌러서 일련번호와 현재사용매수 나온 화면 캡쳐 후 문자로 부탁드립니다.",
    "삼성 5700": "(오른쪽 위) 연장 표시 → 모든 설정 → (밑으로 내리고) 보고서 인쇄 → (밑으로) 프린터 설정 (4장 중에 3번째장 복사기 카운터 나옴) 인쇄물 사진 찍어서 문자로 보내주세요.",
    "기본 기종": "안녕하세요 퍼스트 전산입니다.\n마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다.\n카운터 한장만 보내주시면 감사하겠습니다."
}

default_regions = {
    "V, SS급 (높은등급)": {
        "single": "안녕하세요 퍼스트 전산입니다. 세금계산서 발행을 위해 사용량 체크 카운터 사진이 필요하여 연락드렸습니다. 각 기기별 카운터 한장씩 보내주시면 감사하겠습니다.",
        "multi": "안녕하세요 퍼스트 전산입니다. 세금계산서 발행을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다. 각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
    },
    "S, NN, N급 (일반등급)": {
        "single": "안녕하세요 퍼스트 전산입니다. 마감을 위해 마감 카운터 사진이 필요하여 연락드렸습니다. 카운터 한장만 보내주시면 감사하겠습니다.",
        "multi": "안녕하세요 퍼스트 전산입니다. 마감을 위해 보유하신 총 {total}대 기기의 카운터 사진이 필요하여 연락드렸습니다. 각 기기별 카운터 한장씩 보내주시면 감사하겠습니다."
    }
}

# 3. 파일에서 데이터를 로드하거나 기본값으로 초기화하는 함수 (영구 저장 핵심)
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 세션에 로드된 데이터 바인딩
                st.session_state.custom_formats = data.get("machines", default_machines)
                st.session_state.region_formats = data.get("regions", default_regions)
                return
        except:
            pass
    
    # 파일이 없거나 에러 시 기본값 적용
    if "custom_formats" not in st.session_state:
        st.session_state.custom_formats = copy.deepcopy(default_machines)
    if "region_formats" not in st.session_state:
        st.session_state.region_formats = copy.deepcopy(default_regions)

def save_settings():
    data = {
        "machines": st.session_state.custom_formats,
        "regions": st.session_state.region_formats
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 설정 로드 실행
load_settings()

# 탭 구성
tab_main, tab_setting = st.tabs(["📋 마감 문자 작성", "⚙️ 기종 및 지역별 양식 설정"])

# ==========================================
# 탭 2: 기종 및 지역별 양식 설정 (백엔드 저장 기능 강화)
# ==========================================
with tab_setting:
    st.subheader("🛠️ 영구 저장 및 관리 설정")
    st.caption("여기서 수정한 내용들은 이제 새로고침해도 절대 사라지지 않고 영구 보존됩니다.")
    
    # --- 구역 1: 지역 등급별 문자 양식 설정 ---
    st.markdown("#### 📍 1. 지역/등급별 문자 양식 설정")
    
    r_formats = st.session_state.region_formats
    
    for r_name, templates in list(r_formats.items()):
        with st.expander(f"🏢 {r_name} 설정", expanded=True):
            cols = st.columns(2)
            with cols[0]:
                new_single = st.text_area(f"[{r_name}] 단일 기기 문구", value=templates["single"], key=f"r_single_{r_name}")
            with cols[1]:
                new_multi = st.text_area(f"[{r_name}] 여러 기기 문구 ({{total}} 포함 필수)", value=templates["multi"], key=f"r_multi_{r_name}")
            
            # 실시간 반영
            st.session_state.region_formats[r_name]["single"] = new_single
            st.session_state.region_formats[r_name]["multi"] = new_multi
    
    # 신규 지역 추가 기능
    st.markdown("---")
    st.markdown("➕ **새로운 지역 등급 그룹 추가**")
    new_reg_name = st.text_input("새 지역/등급 이름 (예: 대구지사, A급지사 등)", key="new_reg_name_input")
    if st.button("➕ 새 지역 추가하기"):
        if new_reg_name and new_reg_name not in st.session_state.region_formats:
            st.session_state.region_formats[new_reg_name] = {
                "single": "안녕하세요 퍼스트 전산입니다. 카운터 사진 요청드립니다.",
                "multi": "안녕하세요 퍼스트 전산입니다. 보유하신 총 {total}대 기기의 카운터 사진 요청드립니다."
            }
            save_settings()
            st.success(f"✅ '{new_reg_name}' 그룹이 추가되었습니다!")
            st.rerun()
            
    # --- 구역 2: 기종별 카운터 안내 문구 설정 ---
    st.markdown("---")
    st.markdown("#### 🖨️ 2. 복사기 기종별 카운터 안내 문구 설정")
    
    m_formats = st.session_state.custom_formats
    for m_name, m_text in list(m_formats.items()):
        new_text = st.text_area(f"▶ {m_name} 안내 문구", value=m_text, key=f"m_input_{m_name}")
        st.session_state.custom_formats[m_name] = new_text

    # 최종 저장 버튼
    st.markdown("---")
    if st.button("💾 모든 설정 영구 저장하기", use_container_width=True, type="primary"):
        save_settings()
        st.success("🎉 모든 설정이 안전하게 파일로 영구 저장되었습니다! 이제 새로고침해도 지워지지 않습니다.")

# ==========================================
# 탭 1: 마감 문자 작성 (메인 로직)
# ==========================================
with tab_main:
    st.title("퍼스트전산 마감 도우미 📱")
    st.caption("카톡 마감 명단을 붙여넣으면 중복 번호는 하나로 묶고 구역별/등급별 맞춤 문자를 자동으로 만듭니다.")
    
    raw_input = st.text_area("카카오톡 마감 명단을 복사해서 여기에 붙여넣으세요:", height=250, placeholder="예:\n홍길동 010-1234-5678 신도리코 V서울\n이순신 010-9876-5432 교세라 SS경기")
    
    if raw_input:
        lines = raw_input.split('\n')
        grouped = OrderedDict()
        
        # 전화번호 및 정보 추출 정규식
        pattern = re.compile(r'([가-힣a-zA-Z0-9_\s]+)\s+(010[-.\s]?\d{3,4}[-.\s]?\d{4})')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = pattern.search(line)
            if match:
                full_name_part = match.group(1).strip()
                phone = match.group(2).replace(" ", "").replace("-", "").strip()
                
                # 직급 추출 분리 로직 (이름 뒤에 직급이 없어도 이름이 들어가도록 방어 코드 반영)
                name_tokens = full_name_part.split()
                if len(name_tokens) >= 2:
                    name = name_tokens[0]
                    position = name_tokens[1]
                elif len(name_tokens) == 1:
                    name = name_tokens[0]
                    position = ""
                else:
                    name = full_name_part
                    position = ""
                    
                # 남은 문자열에서 기종 및 등급/지역 파악
                remain_str = line[match.end():].strip()
                
                # 기종 매칭
                detected_machine = "기본 기종"
                for m_key in st.session_state.custom_formats.keys():
                    if m_key in remain_str:
                        detected_machine = m_key
                        break
                
                # 등급/지역 판별 (V, SS 가 들어있으면 상위 등급 자동 매칭)
                grade_group = "S, NN, N급 (일반등급)"
                for r_key in st.session_state.region_formats.keys():
                    if "V" in r_key or "SS" in r_key:
                        if "V" in remain_str or "SS" in remain_str:
                            grade_group = r_key
                            break
                    elif r_key in remain_str:
                        grade_group = r_key
                        break
                        
                if phone not in grouped:
                    grouped[phone] = {
                        "name": name,
                        "position": position,
                        "machines": [],
                        "grade_group": grade_group
                    }
                grouped[phone]["machines"].append(detected_machine)
        
        if grouped:
            st.markdown(f"### 🎯 총 {len(grouped)}건의 마감 대상이 분석되었습니다.")
            
            # 화면 보기 좋게 탭 분리 (V/SS급 탭과 일반 탭)
            tab_v, tab_s = st.tabs(["🔴 높은 등급 (V, SS급 등)", "🔵 일반 등급 및 기타 구역"])
            
            group_keys = list(grouped.keys())
            
            # 높은 등급 탭 렌더링
            with tab_v:
                v_keys = [k for k in group_keys if "V" in grouped[k]["grade_group"] or "SS" in grouped[k]["grade_group"]]
                if not v_keys:
                    st.caption("감지된 높은 등급(V, SS급) 업체가 없습니다.")
                else:
                    for idx, phone in enumerate(v_keys):
                        info = grouped[phone]
                        total_mcs = len(info["machines"])
                        g_group = info["grade_group"]
                        
                        # 다중/단일 양식 선택
                        template_type = "multi" if total_mcs > 1 else "single"
                        base_msg = st.session_state.region_formats[g_group][template_type]
                        
                        # 직급 포함 이름 처리
                        display_name = f"{info['name']} {info['position']}".strip()
                        
                        # 문자 조립
                        final_msg = base_msg.format(total=total_mcs) + "\n\n"
                        final_msg += f"📌 요청 기기 목록 (총 {total_mcs}대):\n"
                        for m_idx, mc in enumerate(info["machines"], 1):
                            m_guide = st.session_state.custom_formats.get(mc, "")
                            final_msg += f"{m_idx}. {mc}\n💡 방법: {m_guide}\n\n"
                        final_msg += "매번 번거롭게 해드려 죄송합니다."
                        
                        # UI 렌더링
                        with st.expander(f"📱 {display_name} ({phone}) - 기기 {total_mcs}대 [{g_group}]", expanded=True):
                            st.text_area("문자 내용 미리보기", value=final_msg, height=200, key=f"txt_v_{idx}")
                            sms_url = f"sms:{phone}?body={urllib.parse.quote(final_msg)}"
                            st.markdown(f'<a href="{sms_url}" target="_blank"><button style="width:100%; padding:10px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📲 {display_name}에게 문자 바로 전송하기</button></a>', unsafe_allow_html=True)

            # 일반 등급 탭 렌더링
            with tab_s:
                s_keys = [k for k in group_keys if not ("V" in grouped[k]["grade_group"] or "SS" in grouped[k]["grade_group"])]
                if not s_keys:
                    st.caption("감지된 일반 등급(S, NN, N급) 업체가 없습니다.")
                else:
                    for idx, phone in enumerate(s_keys):
                        info = grouped[phone]
                        total_mcs = len(info["machines"])
                        g_group = info["grade_group"]
                        
                        template_type = "multi" if total_mcs > 1 else "single"
                        base_msg = st.session_state.region_formats[g_group][template_type]
                        
                        display_name = f"{info['name']} {info['position']}".strip()
                        
                        final_msg = base_msg.format(total=total_mcs) + "\n\n"
                        final_msg += f"📌 요청 기기 목록 (총 {total_mcs}대):\n"
                        for m_idx, mc in enumerate(info["machines"], 1):
                            m_guide = st.session_state.custom_formats.get(mc, "")
                            final_msg += f"{m_idx}. {mc}\n💡 방법: {m_guide}\n\n"
                        final_msg += "매번 번거롭게 해드려 죄송합니다."
                        
                        with st.expander(f"📱 {display_name} ({phone}) - 기기 {total_mcs}대 [{g_group}]", expanded=True):
                            st.text_area("문자 내용 미리보기", value=final_msg, height=200, key=f"txt_s_{idx}")
                            sms_url = f"sms:{phone}?body={urllib.parse.quote(final_msg)}"
                            st.markdown(f'<a href="{sms_url}" target="_blank"><button style="width:100%; padding:10px; background-color:#1E90FF; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📲 {display_name}에게 문자 바로 전송하기</button></a>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ 올바른 이름과 전화번호 형식의 데이터가 감지되지 않았습니다. 복사한 내용을 다시 확인해 주세요.")

    # 입력 내용 초기화 기능
    if st.button("🗑️ 입력 내용 전체 초기화", use_container_width=True):
        st.rerun()
