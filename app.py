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
    elif not st.session_state["password_correct"]:
        st.text_input("金鑰錯誤，請重新輸入：", type="password", on_change=password_entered, key="password")
        st.error("🚫 存取拒絕")
        return False
    else:
        return True

if check_password():
    # --- 🪄 視覺效果：明亮模式 CSS ---
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp { background-color: #ffffff; color: #1f2937; }
        [data-testid="stSidebar"] { background-color: #f3f4f6; }
        .hero-card-container { background-color: #ffffff; padding: 20px 0px; width: 100%; }
        .hero-name-zh { font-size: 2.2rem; font-weight: 700; color: #111827; margin: 0; }
        .hero-name-en { color: #6b7280; font-size: 1rem; margin-bottom: 10px; }
        
        /* 藍色標籤區塊：強制不換行並顯示完整 */
        .official-tag-row {
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            display: block; 
            margin: 15px 0;
            line-height: 1.5;
            border-left: 5px solid #0ea5e9;
        }
        .stMarkdown { color: #374151; }
        </style>
    """, unsafe_allow_html=True)

    # --- 📂 資料載入 (💡 徹底刪除 Cache，保證每次都讀最新檔案) ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 這裡不再使用 @st.cache_data，手機才不會讀到舊資料
    def load_json_fresh():
        try:
            with open('hero_database_final.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return None

    db = load_json_fresh()
    if db:
        heroes = list(db.values())
    else:
        st.error("找不到 JSON 檔案，請確認檔案已 Push 到 GitHub！")
        st.stop()

    # --- 🔍 側邊欄 ---
    st.sidebar.title("🦸‍♂️ 戰術檢索")
    search_query = st.sidebar.text_input("搜尋角色或技能")
    keywords = search_query.lower().split()
    
    filtered = [d for d in heroes if not keywords or all(k in f"{d['name_zh']} {d.get('strategy','')}".lower() for k in keywords)]

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
        # --- 🪄 解析 JSON 內容 ---
        raw_str = hero.get("strategy", "")
        if "### ⚡ 核心技能摘要" in raw_str:
            parts = raw_str.split("### ⚡ 核心技能摘要")
            tag_content = parts[0].replace("### 🏷️ 官方標籤", "").strip()
            # 💡 這裡會渲染妳在 JSON 裡辛苦寫的「靈魂法師突擊」等標籤化文字
            main_content = "### ⚡ 核心技能摘要" + parts[1]
            display_html = f'<div class="official-tag-row">🏷️ 官方標籤：{tag_content}</div>\n\n{main_content}'
        else:
            display_html = raw_str

        # --- 🖼️ 渲染區 ---
        st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            img_path = os.path.join(BASE_DIR, "avatars", f"{hero['id']}.png")
            if os.path.exists(img_path):
                st.image(img_path, width=120)
            else:
                st.image("https://via.placeholder.com/120", width=120)
        with col2:
            st.markdown(f'<p class="hero-name-zh">{hero["name_zh"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
            st.markdown(display_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
