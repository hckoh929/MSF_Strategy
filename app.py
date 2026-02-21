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
        st.markdown("<h2 style='text-align: center; color: white;'>🛡️ 漫威戰略終端訪問授權</h2>", unsafe_allow_html=True)
        st.text_input("請輸入授權金鑰：", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("金鑰錯誤，請重新輸入：", type="password", on_change=password_entered, key="password")
        st.error("🚫 存取拒絕")
        return False
    else:
        return True

# --- 🎬 3. 程式主邏輯 ---
if check_password():
    # --- 🪄 視覺效果：優化後的 CSS ---
    st.markdown("""
        <style>
        /* 移除強制隱藏 header，讓側邊欄按鈕可以顯示 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 全域背景設定 */
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        
        /* 側邊欄樣式微調，確保它是深色的 */
        [data-testid="stSidebar"] {
            background-color: #161b22;
        }
        
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
        path = os.path.join(BASE_DIR, "avatars", f"{hero_id}.png")
        return path if os.path.exists(path) else None

    @st.cache_data
    def load_data():
        with open('hero_database_final.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    try:
        db = load_data()
        heroes = list(db.values())
    except Exception as e:
        st.error(f"資料讀取失敗: {e}")
        st.stop()

    # --- 🔍 側邊欄內容 ---
    st.sidebar.title("🦸‍♂️ 戰術檢索")
    search_query = st.sidebar.text_input("輸入關鍵字 (如: 隱身, 創傷)")
    
    keywords = search_query.lower().split()
    
    filtered = []
    for d in heroes:
        target_text = f"{d['name_zh']} {d.get('name_en','')} {d.get('strategy','')}".lower()
        if not keywords or all(k in target_text for k in keywords):
            filtered.append(d)

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
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
        st.sidebar.warning("找不到符合的特工資料...")
