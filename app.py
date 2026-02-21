import streamlit as st
import json
import os

st.set_page_config(page_title="MSF 終極除錯版", layout="wide")

# --- 🔐 密碼檢查 (簡化版) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    
    pwd = st.text_input("輸入授權金鑰：", type="password")
    if pwd == st.secrets["MY_PASSWORD"]:
        st.session_state["password_correct"] = True
        st.rerun()
    return False

if check_password():
    # --- 📂 強制讀取新檔案 (不使用任何快取) ---
    # 💡 妮妮建議：請將妳的 JSON 檔名改為 hero_data_v2.json 來測試
    JSON_FILE = 'hero_data_v2.json' 
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    heroes = list(db.values())
    
    st.sidebar.title("🦸‍♂️ 特工選單")
    selected_name = st.sidebar.selectbox("選擇角色", [h['name_zh'] for h in heroes])
    hero = next(h for h in heroes if h['name_zh'] == selected_name)

    # --- 🔍 [妮妮專屬偵測器] ---
    st.warning(f"🕵️‍♀️ 妮妮偵測中... 目前 App 讀取到的檔案是：`{JSON_FILE}`")
    with st.expander("🛠️ 點開看目前 JSON 的原始內容 (Debug Only)"):
        st.code(hero.get("strategy", ""))

    # --- 🪄 畫面渲染 ---
    raw_str = hero.get("strategy", "")
    if "### ⚡ 核心技能摘要" in raw_str:
        parts = raw_str.split("### ⚡ 核心技能摘要")
        tag_line = parts[0].replace("### 🏷️ 官方標籤", "").strip()
        main_content = "### ⚡ 核心技能摘要" + parts[1]
        
        # 渲染藍色標籤與技能
        st.markdown(f"""
            <div style="background-color: #e0f2fe; color: #0369a1; padding: 10px; border-radius: 8px; border-left: 5px solid #0ea5e9; font-weight: bold; margin-bottom: 15px;">
                🏷️ 官方標籤：{tag_line}
            </div>
        """, unsafe_allow_html=True)
        st.markdown(main_content)
    else:
        st.write(raw_str)

