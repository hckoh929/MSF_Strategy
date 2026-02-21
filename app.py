import streamlit as st
import json
import os

# --- 🎨 1. 頁面配置 (必須放在最頂端) ---
st.set_page_config(page_title="MSF 戰略專家終端", layout="wide")

# --- 🔐 2. 密碼檢查功能 (從 Secrets 讀取) ---
def check_password():
    """驗證密碼，成功回傳 True"""
    def password_entered():
        # 注意：MY_PASSWORD 必須在 Streamlit Cloud 後台的 Secrets 設定
        if st.session_state["password"] == st.secrets["MY_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
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
        st.text_input(
            "金鑰錯誤，請重新輸入：", type="password", on_change=password_entered, key="password"
        )
        st.error("🚫 存取拒絕：金鑰無效。")
        return False
    else:
        return True

# --- 🎬 3. 程式主邏輯 ---
if check_password():
    # --- 🪄 視覺效果：深度淨化 CSS ---
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

    # --- 📂 資料與路徑處理 ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    def get_avatar_abs_path(hero_id):
        # 確保你的 GitHub 裡有一個 avatars/ 資料夾
        path = os.path.join(BASE_DIR, "avatars", f"{hero_id}.png")
        return path if os.path.exists(path) else None

    @st.cache_data
    def load_data():
        # 讀取你提供的 hero_database_final.json
        with open('hero_database_final.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    try:
        db = load_data()
        heroes = list(db.values())
    except FileNotFoundError:
        st.error("找不到 hero_database_final.json，請確認檔案已上傳至 GitHub。")
        st.stop()

    # --- 🔍 側邊欄：搜尋邏輯 (修正 Syntax Error 版) ---
    st.sidebar.title("🦸‍♂️ 戰術檢索")
    search_query = st.sidebar.text_input("輸入關鍵字 (如: 隱身, 創傷)")
    
    keywords = search_query.lower().split()
    
    # 使用迴圈進行搜尋，避免複雜的 f-string 報錯
    filtered = []
    for d in heroes:
        target_text = f"{d['name_zh']} {d.get('name_en','')} {d.get('strategy','')}".lower()
        if not keywords or all(k in target_text for k in keywords):
            filtered.append(d)

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
        # 標籤顯示優化
        strategy_html = hero.get("strategy", "").replace("### 🏷️ 官方標籤", '<span class="official-tag">🏷️ 官方標籤</span>')
        
        avatar_path = get_avatar_abs_path(hero['id'])
        
        # --- 🖼️ 渲染區 ---
        st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if avatar_path:
                st.image(avatar_path, width=150)
            else:
                # 找不到圖時的預設圖
                st.image("https://via.placeholder.com/150?text=MSF", width=150)
        
        with col2:
            st.markdown(f'<p class="hero-name-zh">{hero["name_zh"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
            st.markdown(strategy_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.warning("找不到符合的特工資料...")
