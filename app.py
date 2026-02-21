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

# --- 🎬 3. 程式主邏輯 ---
if check_password():
    # --- 🪄 明亮模式 CSS 與 UI 優化 ---
    st.markdown("""
        <style>
        /* 隱藏預設選單與頁尾，但【絕對不隱藏 header】，這樣側邊欄小箭頭才會在！ */
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;} 
        header[data-testid="stHeader"] { background-color: transparent !important; }

        /* 全域明亮模式 */
        .stApp { background-color: #ffffff; color: #1f2937; }
        .hero-card-container { background-color: #ffffff; padding: 20px 0px; width: 100%; }
        .hero-name-zh { font-size: 2.8rem; font-weight: 700; color: #111827; margin: 0; }
        .hero-name-en { color: #6b7280; font-size: 1.1rem; font-family: monospace; }
        
        /* 官方標籤樣式 */
        .official-tag { 
            background-color: #e0f2fe; color: #0369a1; padding: 4px 12px;
            border-radius: 20px; font-weight: bold; font-size: 1rem; 
        }
        
        /* 官方 URL 連結按鈕樣式 */
        .official-link {
            display: inline-block; margin-top: 10px; padding: 5px 15px;
            background-color: #f0f9ff; color: #0ea5e9 !important;
            border: 1px solid #bae6fd; border-radius: 8px;
            text-decoration: none !important; font-weight: 600; font-size: 0.9rem;
        }
        .official-link:hover { background-color: #e0f2fe; transform: translateY(-1px); }
        
        /* 側邊欄樣式與提示框 */
        section[data-testid="stSidebar"] { background-color: #f3f4f6; border-right: 1px solid #e5e7eb; }
        .hint-box {
            font-size: 13px; color: #0369a1; background: rgba(3, 105, 161, 0.08); 
            border: 1px dashed #bae6fd; padding: 15px; border-radius: 10px; margin-bottom: 25px;
            line-height: 1.5;
        }
        img { border-radius: 12px; }
        </style>
        """, unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        file_path = "hero_database_final.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON 格式有誤！發生在第 {e.lineno} 行。")
                st.stop()
        return None

    def get_avatar_abs_path(h_id):
        folder = "avatars" 
        if not os.path.exists(folder): return None
        for name in [f"{h_id}.png", f"{h_id.lower()}.png", f"{h_id.capitalize()}.png"]:
            path = os.path.join(folder, name)
            if os.path.exists(path): return os.path.abspath(path)
        return None

    db = load_data()

    # --- 🔍 側邊欄設定 ---
    st.sidebar.title("🛡️ MSF 戰術索引")
    
    # 保留妳原本的提示 Instruction！
    st.sidebar.markdown("""
        <div class="hint-box">
            💡 <strong>提示：</strong><br>
            使用「空格」分隔關鍵字 (AND 邏輯)<br>
            例如：<code>變種人 暈眩</code>
        </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🔄 重新載入資料庫"):
        st.cache_data.clear()
        st.rerun()

    search_q = st.sidebar.text_input("🔍 全文檢索", placeholder="輸入名稱、效果或標籤...")

    if db:
        # 完全保留妳原本的搜尋邏輯
        keywords = search_q.lower().split() if search_q else []
        filtered = [d for d in db.values() if not keywords or all(k in f"{d['name_zh']} {d.get('name_en','')} {d.get('strategy','')}".lower() for k in keywords)]

        if filtered:
            filtered.sort(key=lambda x: x['name_zh'])
            selected_name = st.sidebar.selectbox(f"符合戰術條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
            hero = next(h for h in filtered if h['name_zh'] == selected_name)
            
            # 解析標籤與 URL
            strategy_html = hero.get("strategy", "").replace("### 🏷️ 官方標籤", '<span class="official-tag">🏷️ 官方標籤</span>')
            official_url = hero.get("url", "")
            avatar_path = get_avatar_abs_path(hero['id'])
            
            # --- 🖼️ 渲染區 ---
            st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 4])
            with col1:
                if avatar_path: st.image(avatar_path, width=150)
                else: st.image("https://via.placeholder.com/150?text=Avatar", width=150)
            with col2:
                st.markdown(f'<p class="hero-name-zh">🦸 {hero["name_zh"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
                
                # 如果有 URL 就顯示按鈕
                if official_url:
                    st.markdown(f'<a href="{official_url}" target="_blank" class="official-link">🌐 官方資料連結</a>', unsafe_allow_html=True)
            
            st.divider() 
            st.markdown(strategy_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.sidebar.warning("查無符合結果")
    else:
        st.error("📡 找不到資料庫檔案 hero_database_final.json")
