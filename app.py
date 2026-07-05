# 4열 배치(Modulus 4) 분기 처리 및 팝업창 트리거 연결
                    with btn_cols_s[g_idx % 4]:
                        if st.button(f"📱 {display_name} ({len(machines)}대)", key=f"btn_s_{gkey}", use_container_width=True):
                            show_send_popup(display_name, phones, generated_msg, original_names)
                            
        # 💎 V, SS급 탭 구현
        with tab_v:
            v_keys = [k for k in group_keys if grouped[k]["grade_group"] == "v_group"]
            if not v_keys: 
                st.caption("감지된 V, SS급 업체가 없습니다.")
            else:
                btn_cols_v = st.columns(4)
                for g_idx, gkey in enumerate(v_keys):
                    info = grouped[gkey]
                    phones, machines, display_name, original_names = info["phones"], info["machines"], info["display_name"], info["original_names"]
                    
                    generated_msg = build_message_by_grade(machines, active_machines, active_templates, "v_group")
                    
                    with btn_cols_v[g_idx % 4]:
                        if st.button(f"💎 {display_name} ({len(machines)}대)", key=f"btn_v_{gkey}", use_container_width=True):
                            show_send_popup(display_name, phones, generated_msg, original_names)
