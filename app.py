import streamlit as st
import json
import os

# --- 🎨 1. 頁面配置 ---
st.set_page_config(page_title="MSF 終極修復版", layout="wide")

# --- 🔐 2. 密碼檢查 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    
    st.markdown("### 🛡️ 漫威戰略終端訪問授權")
    pwd = st.text_input("請輸入授權金鑰：", type="password")
    if pwd:
        if pwd == st.secrets["MY_PASSWORD"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("🚫 金鑰錯誤")
    return False

if check_password():
    # --- 📂 3. 檔案路徑與檢查 ---
    # 💡 妮妮提醒：請確認妳 GitHub 上的檔名是這一個喔！
    JSON_FILE = 'hero_database_final.json' 
    
    # 檢查檔案是否存在
    if not os.path.exists(JSON_FILE):
        st.error(f"❌ 找不到檔案：`{JSON_FILE}`")
        st.info("🕵️‍♀️ 妮妮偵測到目前資料夾裡的檔案有：")
        st.code(os.listdir('.')) # 這行會列出所有檔案，幫我們抓出錯字
        st.stop() # 停止執行，避免看到紅字報錯

    # --- 讀取資料 ---
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)
        heroes = list(db.values())
    except Exception as e:
        st.error(f"讀取 JSON 時發生錯誤: {e}")
        st.stop()

    # --- 🔍 4. 側邊欄與搜尋 ---
    st.sidebar.title("🦸‍♂️ 特工選單")
    search_query = st.sidebar.text_input("搜尋關鍵字")
    
    filtered = [h for h in heroes if not search_query or search_query.lower() in f"{h['name_zh']} {h.get('strategy','')}".lower()]

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)

        # --- 🪄 5. 畫面渲染 ---
        raw_str = hero.get("strategy", "")
        
        # 顯示 Debug 用的原始碼 (等成功後可以刪掉這段)
        with st.expander("🛠️ 原始內容檢查"):
            st.code(raw_str)

        if "### ⚡ 核心技能摘要" in raw_str:
            parts = raw_str.split("### ⚡ 核心技能摘要")
            tag_line = parts[0].replace("### 🏷️ 官方標籤", "").strip()
            main_content = "### ⚡ 核心技能摘要" + parts[1]
            
            st.markdown(f"""
                <div style="background-color: #e0f2fe; color: #0369a1; padding: 10px; border-radius: 8px; border-left: 5px solid #0ea5e9; font-weight: bold; margin-bottom: 15px;">
                    🏷️ 官方標籤：{tag_line}
                </div>
            """, unsafe_allow_html=True)
            st.markdown(main_content)
        else:
            st.write(raw_str)
    else:
        st.sidebar.warning("找不到相符的特工...")
