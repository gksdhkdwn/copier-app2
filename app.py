import streamlit as st
import re
import urllib.parse

st.set_page_config(page_title="퍼스트전산 마감 도우미", page_icon="📱", layout="centered")
st.title("퍼스트전산 마감 도우미 📱")
st.caption("카톡 내용을 복사해 넣으면 맞춤형 안내 문자를 자동으로 만들어 드립니다.")

if "instructions" not in st.session_state:
    st.session_state.instructions = {
        "D410": "화면 우측의 [카운터] 버튼을 누르신 후 [사용량 확인] 화면을 촬영해 주세요.",
        "D420": "화면 우측의 [카운터] 버튼을 누르신 후 [사용량 확인] 화면을 촬영해 주세요.",
        "D450": "조작부 홈 화면에서 [카운터] 아이콘을 누르고 전체 화면을 촬영해 주세요.",
        "D451": "조작부 홈 화면에서 [카운터] 아이콘을 누르고 전체 화면을 촬영해 주세요.",
        "BH": "[메뉴] -> [카운터] 버튼을 순서대로 누르신 후 화면을 촬영해 주세요.",
        "X3220": "화면에서 [설정] -> [기기 정보] -> [카운터] 화면을 촬영해 주세요.",
        "C3060": "조작부의 [인증/사양설정] 버튼 누른 후 [카운터 확인]을 촬영해 주세요.",
        "TASKalfa": "기기 본체의 [카운터] 물리 버튼을 누른 후 나오는 화면을 촬영해 주세요."
    }
if "base_msg" not in st.session_state:
    st.session_state.base_msg = "안녕하세요 {company} 고객님! 퍼스트전산입니다. 마감 진행을 위해 카운터 사진이 필요하여 요청드립니다.\n\n📌 [{model}] 카운터 확인 방법:\n{instruction}\n\n확인하신 화면을 이 번호로 사진 문자 보내주시거나 카카오톡 채널로 전송해 주시면 감사하겠습니다. 매번 번거롭게 해드려 죄송합니다!"

tab1, tab2 = st.tabs(["📝 마감 문자 작성", "⚙️ 기종 및 문구 설정"])

with tab1:
    katalk_input = st.text_area("📋 카톡방에서 복사한 내용을 여기에 붙여넣으세요:", height=150)
    extracted_phone = ""
    extracted_company = ""
    detected_model = "기타 기종"

    if katalk_input:
        phone_match = re.search(r'010[-.\s]?\d{3,4}[-.\s]?\d{4}', katalk_input)
        if phone_match:
            extracted_phone = phone_match.group().replace("-", "").strip()
        lines = [line.strip() for line in katalk_input.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if extracted_phone and (extracted_phone in line or (phone_match and phone_match.group() in line)):
                if i > 0:
                    extracted_company = lines[i-1].split("매월")[0].split("15")[0].strip()
        for model_key in st.session_state.instructions.keys():
            if model_key.lower() in katalk_input.lower():
                detected_model = model_key
                break

    st.subheader("🔍 자동 인식된 정보 (수정 가능)")
    company = st.text_input("🏢 업체명", value=extracted_company)
    phone = st.text_input("📞 고객 연락처", value=extracted_phone)
    model_list = list(st.session_state.instructions.keys()) + ["기타 기종"]
    default_index = model_list.index(detected_model) if detected_model in model_list else len(model_list)-1
    selected_model = st.selectbox("🖨️ 복사기 기종 선택", model_list, index=default_index)
    current_instruction = st.session_state.instructions.get(selected_model, "복사기 정면 혹은 상단의 카운터 버튼을 눌러 확인해 주세요.")

    final_msg = st.session_state.base_msg.format(
        company=company,
        model=selected_model,
        instruction=current_instruction
    )
    st.subheader("✉️ 최종 발송 문구 미리보기")
    final_msg_edited = st.text_area("", value=final_msg, height=180)

    if phone:
        encoded_msg = urllib.parse.quote(final_msg_edited)
        sms_url = f"sms:{phone}?body={encoded_msg}"
        st.markdown(f'<a href="{sms_url}" target="_blank"><button style="width:100%; height:55px; background-color:#25D366; color:white; border:none; border-radius:10px; font-size:18px; font-weight:bold; cursor:pointer;">✉️ 갤럭시 문자로 내보내기</button></a>', unsafe_allow_html=True)
    else:
        st.info("카톡 내용을 입력하시면 문자 보내기 버튼이 활성화됩니다.")

with tab2:
    st.subheader("⚙️ 복사기 기종별 안내 문구 수정")
    for k, v in list(st.session_state.instructions.items()):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.text(k)
        with col2:
            st.session_state.instructions[k] = st.text_input(f"{k} 설명", value=v, label_visibility="collapsed")
    st.write("---")
    st.write("➕ 새로운 복사기 기종 추가")
    new_model = st.text_input("새 기종 이름 (예: C3300)")
    new_inst = st.text_input("새 기종 카운터 확인 방법 설명")
    if st.button("기종 추가하기"):
        if new_model and new_inst:
            st.session_state.instructions[new_model] = new_inst
            st.success(f"[{new_model}] 기종이 성공적으로 추가되었습니다!")
            st.rerun()
    st.write("---")
    st.subheader("📝 기본 문자 양식 수정")
    st.session_state.base_msg = st.text_area("기본 문자 양식", value=st.session_state.base_msg, height=150)
