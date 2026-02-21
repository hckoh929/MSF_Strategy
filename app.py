import streamlit as st
import json
import os

# --- 🎨 1. 頁面配置 (必須放在最上方) ---
st.set_page_config(page_title="MSF 戰略專家終端", layout="wide")

# --- 🔐 2. 密碼檢查功能 ---
def check_password():
    """驗證密碼，成功回傳 True"""
    def password_entered():
        if st.session_state["password"] == st.secrets["MY_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #1f2937;'>🛡️ 漫威戰略終端訪問授權</h2>", unsafe_allow_html=True)
        st.text_input("請輸入授權金鑰：", type="password", on_change=password_entered, key="password")
        st.info("💡 這是特工限定工具，請向管理員索取密碼。")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("金鑰錯誤，請重新輸入：", type="password", on_change=password_entered, key="password")
        st.error("🚫 存取拒絕：金鑰無效。")
        return False
    else:
        return True

# --- 🎬 3. 程式主邏輯 ---
if check_password():
    # --- 🪄 視覺效果：明亮模式 CSS 優化 ---
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp { background-color: #ffffff; color: #1f2937; }
        [data-testid="stSidebar"] { background-color: #f3f4f6; }
        
        /* 角色卡片容器 */
        .hero-card-container { 
            background-color: #ffffff; 
            padding: 20px 0px;
            width: 100%;
        }
        
        .hero-name-zh { font-size: 2.8rem; font-weight: 700; color: #111827; margin: 0; }
        .hero-name-en { color: #6b7280; font-size: 1.1rem; margin-bottom: 15px; }
        
        /* ✨ 官方標籤專屬樣式：確保整排藍色、不被切斷 */
        .official-tag-row {
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            display: block; /* 強制換行顯示整排 */
            margin: 15px 0;
            line-height: 1.6;
            border-left: 5px solid #0ea5e9;
        }
        
        .stMarkdown { color: #374151; }
        
        /* 讓圖片圓角一點比較好看 */
        img { border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 📂 資料載入 (清除快取以確保讀取最新 JSON) ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    def get_avatar_abs_path(hero_id):
        path = os.path.join(BASE_DIR, "avatars", f"{hero_id}.png")
        return path if os.path.exists(path) else None

    @st.cache_data(ttl=600) # 設定 10 分鐘自動過期，或手動 Clear Cache
    def load_data():
        with open('hero_database_final.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    try:
        db = load_data()
        heroes = list(db.values())
    except Exception as e:
        st.error(f"資料讀取失敗，請檢查 JSON 檔案: {e}")
        st.stop()

    # --- 🔍 側邊欄：搜尋與選擇 ---
    st.sidebar.title("🦸‍♂️ 戰術檢索")
    search_query = st.sidebar.text_input("搜尋角色、技能或標籤")
    
    keywords = search_query.lower().split()
    
    filtered = []
    for d in heroes:
        # 組合搜尋文字，包含中文名、英文名與 strategy 內容
        target_text = f"{d['name_zh']} {d.get('name_en','')} {d.get('strategy','')}".lower()
        if not keywords or all(k in target_text for k in keywords):
            filtered.append(d)

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
        # --- 🪄 強力解析邏輯：確保 JSON 內容與網頁一致 ---
        raw_strategy = hero.get("strategy", "")
        
        # 尋找標籤與摘要的分界點
        if "### ⚡ 核心技能摘要" in raw_strategy:
            parts = raw_strategy.split("### ⚡ 核心技能摘要")
            # 抓取第一部分並移除標題文字，留下純標籤
            tag_content = parts[0].replace("### 🏷️ 官方標籤", "").strip()
            # 剩餘的部分是技能摘要
            main_content = "### ⚡ 核心技能摘要" + parts[1]
            # 組合為 HTML 格式
            display_html = f'<div class="official-tag-row">🏷️ 官方標籤：{tag_content}</div>\n\n{main_content}'
        else:
            display_html = raw_strategy

        avatar_path = get_avatar_abs_path(hero['id'])
        
        # --- 🖼️ 畫面渲染 ---
        st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if avatar_path:
                st.image(avatar_path, width=160)
            else:
                st.image("https://via.placeholder.com/160?text=No+Image", width=160)
        
        with col2:
            st.markdown(f'<p class="hero-name-zh">{hero["name_zh"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
            # 使用 Markdown 渲染組合後的 HTML 與技能文字
            st.markdown(display_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.warning("找不到相符的特工...")
