import streamlit as st
import json
import os

# --- 🎨 頁面配置 ---
st.set_page_config(page_title="MSF 戰略專家終端", layout="wide")

# --- 🪄 深度淨化 CSS：消除所有邊框與白條 ---
st.markdown("""
    <style>
    /* 1. 消除頂部白條、選單與頁尾 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. 全域背景設定 (純深色) */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* 3. 卡片容器淨化：移除所有灰框感，改用與背景融合的設計 */
    .hero-card-container { 
        background-color: #0d1117; /* 與背景完全一致，消除框感 */
        padding: 20px 0px;        /* 移除左右內距，讓它像浮在背景上 */
        width: 100%;
    }

    /* 4. 內容區塊微調 */
    .hero-name-zh { font-size: 2.8rem; font-weight: 700; color: white; margin: 0; }
    .hero-name-en { color: #8b949e; font-size: 1.1rem; font-family: monospace; }
    .official-tag { color: #ffa657; font-weight: bold; font-size: 1.1rem; }
    
    /* 側邊欄邊界線淡化 */
    section[data-testid="stSidebar"] { 
        background-color: #0d1117; 
        border-right: 1px solid #21262d; 
    }

    /* 提示區塊 */
    .hint-box {
        font-size: 13px; 
        color: #ffa657; 
        background: rgba(255,166,87,0.05); 
        border: 1px dashed #30363d; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 20px;
    }
    
    /* 隱藏 Streamlit 的預設圖片邊框 */
    img { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 📂 數據與頭像核心 ---
@st.cache_data
def load_data():
    file_path = "hero_database_final.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_avatar_abs_path(h_id):
    folder = "portraits"
    if not os.path.exists(folder): return None
    for name in [f"{h_id}.png", f"{h_id.lower()}.png", f"{h_id.capitalize()}.png"]:
        path = os.path.join(folder, name)
        if os.path.exists(path): return os.path.abspath(path)
    return None

# --- 🚀 啟動邏輯 ---
db = load_data()

st.sidebar.title("🛡️ MSF 戰術索引")
st.sidebar.markdown('<div class="hint-box">💡 提示：使用「空格」分隔關鍵字 (AND 邏輯)<br>例如：<strong>變種人 暈眩</strong></div>', unsafe_allow_html=True)

search_q = st.sidebar.text_input("🔍 全文檢索", placeholder="輸入名稱、效果或標籤...")

if db:
    keywords = search_q.lower().split() if search_q else []
    filtered = [d for d in db.values() if not keywords or all(k in f"{d['name_zh']} {d.get('name_en','')} {d.get('strategy','')}".lower() for k in keywords)]

    if filtered:
        filtered.sort(key=lambda x: x['name_zh'])
        selected_name = st.sidebar.selectbox(f"符合戰術條件 ({len(filtered)})", [h['name_zh'] for h in filtered])
        hero = next(h for h in filtered if h['name_zh'] == selected_name)
        
        # 標籤顯示優化
        strategy = hero.get("strategy", "").replace("### 🏷️ 官方標籤", '<span class="official-tag">🏷️ 官方標籤</span>')
        strategy = strategy.replace("### 🏷️ **官方標籤**", '<span class="official-tag">🏷️ 官方標籤</span>')
        
        avatar_path = get_avatar_abs_path(hero['id'])
        
        # --- 🖼️ 渲染區：完全融合背景的無框設計 ---
        st.markdown('<div class="hero-card-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if avatar_path:
                st.image(avatar_path, width=150)
            else:
                st.image("https://via.placeholder.com/150?text=MSF", width=150)
        with col2:
            st.markdown(f'<p class="hero-name-zh">🦸 {hero["name_zh"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="hero-name-en">{hero.get("name_en", "")}</p>', unsafe_allow_html=True)
        
        st.divider() 
        st.markdown(strategy, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.warning("查無符合結果")
else:
    st.error("📡 找不到資料庫檔案。")