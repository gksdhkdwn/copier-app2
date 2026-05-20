import streamlit as st
import re

# 스트림릿 페이지 설정
st.set_page_config(page_title="퍼스트전산 마감 도우미", layout="wide")

# 1. 기종별 카운터 방법 사전 초기화 (st.session_state 활용으로 새로고침 방지)
if "dict_mach" not in st.session_state:
    st.session_state.dict_mach = {
        "D451": "화면 우측의 [카운터] 버튼을 누르신 후 화면에 나오는 [사용량 확인] 전체 화면을 촬영해 주세요.",
        "X-9201": "조작부의 [인증/사양설정] 버튼 -> [카운터 확인]을 누르신 후 화면을 촬영해 주세요.",
        "X3220NR": "조작부의 [인증/사양설정] 버튼 -> [카운터 확인]을 누르신 후 화면을 촬영해 주세요.",
        "MP-C2003": "기기 본체의 [카운터] 물리 버튼을 누른 후 나오는 화면을 촬영해 주세요.",
        "ECOSYS": "기기 본체의 [카운터] 또는 [Counter] 버튼을 누른 후 화면을 촬영해 주세요."
    }

# 기본 기종 리스트
AVAILABLE_MACHINES = list(st.session_state.dict_mach.keys()) + ["기타 기종(직접 입력)"]

# 탭 구성
tab1, tab2 = st.tabs(["📝 마감 문자 대량 작성", "⚙️ 기종별 카운터 방법 사전"])

# ----------------------------------------------------
# 탭 2: 기종별 카운터 방법 사전 관리
# ----------------------------------------------------
with tab2:
    st.subheader("⚙️ 기종별 카운터 안내 문구 설정")
    st.write("여기서 문구를 수정하면 문자 작성 탭에 실시간으로 반영됩니다.")
    
    updated_dict = {}
    for mach, text in st.session_state.dict_mach.items():
        # 첫 번째 탭과 Key 충돌 방지를 위해 고유 Key 사용
        updated_text = st.text_area(f"📟 {mach} 안내 문구", value=text, key=f"dict_input_{mach}", height=70)
        updated_dict[mach] = updated_text
    
    # 수정된 내용 세션에 저장
    st.session_state.dict_mach = updated_dict

# ----------------------------------------------------
# 탭 1: 마감 문자 대량 작성 및 발송
# ----------------------------------------------------
with tab1:
    st.title("📟 퍼스트전산 마감 도우미 (모바일 겸용)")
    st.write("카톡방 마감 명단을 아래에 통째로 붙여넣으세요. 동일 번호는 문자 1개로 자동 통합됩니다.")

    # 카톡 텍스트 입력창
    raw_text = st.text_area("📋 카카오톡 마감 명단 붙여넣기", height=250, placeholder="여기에 카톡 마감 양식을 통째로 붙여넣으세요.")

    if raw_text:
        # 순번(숫자 뒤 콤마)을 기준으로 거래처 블록 분리
        blocks = re.split(r'(?=\b\d+,\s*)', raw_text)
        
        # 유효한 블록 필터링
        valid_blocks = []
        for b in blocks:
            b_clean = b.strip()
            # 대괄호로 시작하는 지역명 제외 및 실제 데이터가 있는 경우만 포함
            if b_clean and not b_clean.startswith("[") and not b_clean.startswith("【"):
                valid_blocks.append(b_clean)

        if valid_blocks:
            st.success(f"🔍 총 {len(valid_blocks)}개의 기기 마감 데이터를 감지했습니다.")
            
            # --- [핵심 수정 로직] 전화번호 기준 데이터 그룹화 ---
            # phone_groups 구조: { "010-1234-5678": [ {block_info_1}, {block_info_2} ] }
            phone_groups = {}
            
            for idx, block in enumerate(valid_blocks):
                # 전화번호 추출
                phone_match = re.search(r'010[-.\s]?\d{3,4}[-.\s]?\d{4}', block)
                phone_num = phone_match.group().replace(" ", "-") if phone_match else f"번호없음-{idx}"
                
                # 기종(모델명) 자동 매칭 시도
                matched_machine = "기타 기종(직접 입력)"
                for m_key in st.session_state.dict_mach.keys():
                    if m_key.lower() in block.lower() or (m_key == "X3220NR" and "3220" in block):
                        matched_machine = m_key
                        break
                
                # 그룹 사전에 추가
                if phone_num not in phone_groups:
                    phone_groups[phone_num] = []
                
                phone_groups[phone_num].append({
                    "block_idx": idx,
                    "raw_block": block,
                    "default_machine": matched_machine
                })

            st.subheader("💬 담당자별 통합 문자 생성 목록")
            st.write("---")

            # 그룹화된 담당자별로 화면 표시 및 문자 생성
            for p_num, items in phone_groups.items():
                # '번호없음' 임시 처리 방지
                is_valid_phone = not p_num.startswith("번호없음")
                display_phone = p_num if is_valid_phone else "⚠️ 번호 미확인"
                
                st.markdown(f"### 👤 담당자 연락처: `{display_phone}` (총 {len(items)}대 관리 중)")
                
                # 이 담당자가 사용하는 기기별 기종 선택창 배치
                selected_machines_info = []
                
                # 가로 레이아웃으로 기종 선택 UI 배치
                cols = st.columns(min(len(items), 4))
                for i, item in enumerate(items):
                    col_idx = i % 4
                    with cols[col_idx]:
                        sb_key = f"sel_{item['block_idx']}_{p_num}"
                        u_machine = st.selectbox(
                            f"기기 {i+1} 기종 선택", 
                            AVAILABLE_MACHINES, 
                            index=AVAILABLE_MACHINES.index(item["default_machine"]),
                            key=sb_key
                        )
                        
                        # 기타 기종일 경우 직접 입력창 제공
                        if u_machine == "기타 기종(직접 입력)":
                            ti_key = f"txt_{item['block_idx']}_{p_num}"
                            custom_mach = st.text_input(f"기기 {i+1} 기종명 입력", value="기본기종", key=ti_key)
                            ta_key = f"area_{item['block_idx']}_{p_num}"
                            custom_how = st.text_area(f"기기 {i+1} 안내문 입력", value="정확한 카운터 화면 사진을 촬영하여 전송해 주세요.", key=ta_key, height=60)
                            selected_machines_info.append({"machine": custom_mach, "how": custom_how})
                        else:
                            selected_machines_info.append({
                                "machine": u_machine, 
                                "how": st.session_state.dict_mach.get(u_machine, "")
                            })
                
                # --- 문자 메시지 본문 통합 조립 ---
                msg_header = "안녕하세요, 퍼스트전산입니다!\n한 달 동안 사용하신 복사기 마감 진행을 위해 카운터 사진 요청드립니다.\n\n📌 [마감 대상 기기 안내]"
                
                msg_body = ""
                for idx, m_info in enumerate(selected_machines_info):
                    msg_body += f"\n▶ ({idx+1}) 기종: {m_info['machine']}\n💡 방법: {m_info['how']}\n"
                
                msg_footer = "\n확인하신 카운터 화면을 본 번호로 사진 문자(SMS) 전송 부탁드립니다.\n매번 번거롭게 해드려 죄송하며, 협조해 주셔서 늘 감사합니다! 🙏"
                
                final_integrated_msg = f"{msg_header}{msg_body}{msg_footer}"
                
                # 통합된 최종 문자 보여주기
                ta_msg_key = f"integrated_msg_{p_num}"
                editable_msg = st.text_area("📄 최종 발송 문자 미리보기 (수정 가능)", value=final_integrated_msg, key=ta_msg_key, height=180)
                
                # 갤럭시 문자 앱 즉시 전송 버튼 생성
                if is_valid_phone:
                    clean_phone = p_num.replace("-", "").strip()
                    # 공백 및 특수문자 url 인코딩 대응
                    encoded_msg = editable_msg.replace('\n', '%0A').replace(' ', '%20')
                    sms_link = f"sms:{clean_phone}?body={encoded_msg}"
                    
                    st.markdown(
                        f'<a href="{sms_link}" target="_self" style="text-decoration:none;">'
                        f'<button style="width:100%; padding:10px; background-color:#2db742; color:white; '
                        f'border:none; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:20px;">'
                        f'💬 이 담당자에게 문자 1개로 즉시 전송 (기기 {len(items)}대 통합)</button></a>',
                        unsafe_allow_code=True
                    )
                else:
                    st.warning("⚠️ 전화번호가 정확하지 않아 갤럭시 문자 발송 링크를 생성할 수 없습니다. 번호를 확인해 주세요.")
                
                st.markdown("<div style='border-bottom:2px dashed #ccc; margin:20px 0;'></div>", unsafe_allow_code=True)
        else:
            st.info("올바른 순번 형태(예: '20,')를 가진 거래처 데이터를 찾지 못했습니다. 양식을 확인해 주세요.")
