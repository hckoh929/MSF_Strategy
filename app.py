import streamlit as st
import json
import os

# --- 🎨 頁面配置 (必須保持在最上方) ---
st.set_page_config(page_title="MSF 戰略專家終端", layout="wide")

# --- 🔐 密碼檢查功能 (搭配 Secrets) ---
def check_password():
    """驗證密碼，成功回傳 True"""
    def password_entered():
        # 從 Streamlit Cloud 的 Secrets 讀取密碼
        # 如果你還沒設定 Secrets，這裡會報錯，記得去後台設定喔！
        if st.session_state["password"] == st.secrets["MY_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 安全起見，刪除暫存密碼
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初次訪問，顯示登入介面
        st.markdown("<h2 style='text-align: center; color: white;'>🛡️ 漫威戰略終端訪問授權</h2>", unsafe_allow_html=True)
        st.text_input(
            "請輸入授權金鑰：", type="password", on_change=password_entered, key="password"
        )
        st.info("💡 這是特工限定工具，請向管理員索取密碼。")
        return False
    elif not st.session_state["password_correct"]:
        # 密碼錯誤
        st.text_input(
            "金鑰錯誤，請重新輸入：", type="password", on_change=password_entered, key="password"
        )
        st.error("🚫 存取拒絕：金鑰無效。")
        return False
    else:
        # 密碼正確
        return True

# --- 🎬 程式主邏輯 ---
if check_password():
    # --- 🪄 深度淨化 CSS：消除所有邊框與白條 ---
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        .hero-card-container { 
            background-color: #0d1117; 
            padding: 20px 0px;
            width: 100%;
        }
        .hero-name-zh { font-size: 2.8rem; font-weight: 700; color: white; margin: 0; }
        .hero-name-en { color: #8b949e; font-size: 1.1rem; }
        .official-tag {
            background-color: #1f2937;
            color: #38bdf8;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 📂 資料載入與處理 ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    def get_avatar_abs_path(hero_id):
        # 確保你的圖片放在 avatars 資料夾，且檔名是 id.png
        path = os.path.join(BASE_DIR, "avatars", f"{hero_id}.png")
        return path if os.path.exists(path) else None

    @st.cache_data
    def load_data():
        with open('hero_database_final.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    db = load_data()
    heroes = list(db.values())

    # --- 🔍 側邊欄：搜尋功能 ---
    st.sidebar.title("🦸‍♂️ 戰術檢索")
    search_query = st.sidebar.text_input("輸入角色名或關鍵字 (如: 隱身, 創傷)")
    
    keywords = search_query.lower().split()
    filtered = [d for d in heroes if not keywords or all(k in f"{d['name_zh']} {d.get('name_en','')} {d.get('strategy','')}\".lower() for k in keywords)]

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
        # 內容優化
        strategy_html = hero.get("strategy", "").replace("### 🏷️ 官方標籤", '<span class="official-tag">🏷️ 官方標籤</span>')
        
        avatar_path = get_avatar_abs_path(hero['id'])
        
        # --- 🖼️ 渲染區 ---
        st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if avatar_path:
                st.image(avatar_path, width=150)
            else:
                st.image("https://via.placeholder.com/150?text=MSF", width=150)
        
        with col2:
            st.markdown(f'<p class="hero-name-zh">{hero["name_zh"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
            st.markdown(strategy_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.warning("找不到符合的英雄...")
