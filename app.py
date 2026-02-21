import streamlit as st
import json
import os

# --- 🎨 1. 頁面配置 ---
st.set_page_config(page_title="MSF 戰略專家終端", layout="wide")

# --- 🔐 2. 密碼檢查功能 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["MY_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #1f2937;'>🛡️ 漫威戰略終端訪問授權</h2>", unsafe_allow_html=True)
        st.text_input("請輸入授權金鑰：", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    # --- 🪄 視覺效果：CSS ---
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        .stApp { background-color: #ffffff; color: #1f2937; }
        .hero-card-container { background-color: #ffffff; padding: 10px 0px; width: 100%; }
        .hero-name-zh { font-size: 2.2rem; font-weight: 700; color: #111827; margin: 0; }
        .hero-name-en { color: #6b7280; font-size: 1rem; margin-bottom: 5px; }
        .official-tag-row {
            background-color: #e0f2fe; color: #0369a1; padding: 10px;
            border-radius: 8px; font-size: 0.9rem; font-weight: 600;
            display: block; margin: 10px 0; border-left: 5px solid #0ea5e9;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 📂 直接讀取檔案 (不使用快取) ---
    @st.cache_resource # 改用 resource 快取，或是乾脆拿掉
    def load_data():
        if os.path.exists('hero_database_final.json'):
            with open('hero_database_final.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    db = load_data()
    heroes = list(db.values())

    # --- 🔍 側邊欄 ---
    st.sidebar.title("🦸‍♂️ 戰術檢索")
    # 💡 這裡加一個重新整理按鈕，讓妳在手機上也能點
    if st.sidebar.button("🔄 重新載入資料庫"):
        st.cache_resource.clear()
        st.rerun()

    search_query = st.sidebar.text_input("輸入關鍵字")
    keywords = search_query.lower().split()
    
    filtered = [d for d in heroes if not keywords or all(k in f"{d['name_zh']} {d.get('strategy','')}".lower() for k in keywords)]

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
        # --- 🪄 解析內容 ---
        raw_str = hero.get("strategy", "")
        
        # 檢查標題是否真的存在
        if "### ⚡ 核心技能摘要" in raw_str:
            parts = raw_str.split("### ⚡ 核心技能摘要")
            tag_line = parts[0].replace("### 🏷️ 官方標籤", "").strip()
            rest = "### ⚡ 核心技能摘要" + parts[1]
            display_html = f'<div class="official-tag-row">🏷️ 官方標籤：{tag_line}</div>\n\n{rest}'
        else:
            # 如果讀不到標題，就直接顯示原始內容 (方便我們除錯)
            display_html = raw_str

        # --- 🖼️ 渲染 ---
        st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            img_path = f"avatars/{hero['id']}.png"
            if os.path.exists(img_path): st.image(img_path, width=120)
            else: st.image("https://via.placeholder.com/120", width=120)
        with col2:
            st.markdown(f'<p class="hero-name-zh">{hero["name_zh"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
            st.markdown(display_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
