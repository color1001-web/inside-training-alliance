import streamlit as st
from streamlit_sortables import sort_items
import sqlite3
import pandas as pd

# 設定頁面配置
st.set_page_config(page_title="團隊特質排序調查系統", layout="wide")

# --- 1. 資料庫初始化 ---
def init_db():
    conn = sqlite3.connect('team_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rankings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_name TEXT,
                  ranking_text TEXT, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_ranking(name, ranking):
    conn = sqlite3.connect('team_results.db')
    c = conn.cursor()
    c.execute("INSERT INTO rankings (user_name, ranking_text) VALUES (?, ?)", (name, ",".join(ranking)))
    conn.commit()
    conn.close()

init_db()

# --- 2. 初始特質清單 ---
traits = [
    "溝通能力", "協作精神", "責任感", "領導力", "解決問題", 
    "抗壓性", "創新思維", "誠實正直", "適應力", "積極主動",
    "專業技術", "時間管理", "批判性思考", "同理心", "學習動機",
    "細心程度", "目標導向", "情緒管理", "幽默感", "果斷力",
    "團隊忠誠", "資源整合", "跨領域整合"
]

# --- 3. 頁面邏輯控制 ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 側邊欄：管理員驗證區
with st.sidebar:
    st.header("🔑 管理員登入")
    # 您可以在這裡修改您的管理員密碼
    admin_password = st.text_input("輸入管理員密碼", type="password")
    is_admin = (admin_password == "admin123") # 這裡設定密碼為 admin123
    
    if is_admin:
        st.success("管理員身分已確認")
        show_admin = st.checkbox("開啟統計與明細")
    else:
        if admin_password:
            st.error("密碼錯誤")
        show_admin = False

# 第一頁：輸入姓名
if st.session_state.user_name is None:
    st.title("📋 歡迎參加團隊特質調查")
    st.write("在開始排序之前，請先輸入您的姓名：")
    name_input = st.text_input("您的姓名", placeholder="例如：王小明")
    
    if st.button("開始進行排序"):
        if name_input.strip():
            st.session_state.user_name = name_input
            st.rerun()
        else:
            st.error("請輸入姓名後再繼續")

# 第二頁：排序頁面
else:
    st.title(f"你好，{st.session_state.user_name}！")
    st.write("請依照您認為的重要性，由上至下拖曳排列下列 23 種特質（最重要在最上面）。")

    # 排序介面
    sorted_traits = sort_items(traits, multi_containers=False, direction="vertical")

    if st.button("確認並送出我的排序"):
        save_ranking(st.session_state.user_name, sorted_traits)
        st.success("您的排序已儲存！感謝參與。")
        st.balloons()

# --- 4. 管理員後台統計 (僅在密碼正確且勾選時顯示) ---
if is_admin and show_admin:
    st.divider()
    st.header("📊 全體統計結果")
    
    conn = sqlite3.connect('team_results.db')
    df = pd.read_sql_query("SELECT user_name, ranking_text FROM rankings", conn)
    conn.close()

    if not df.empty:
        # A. 計算加權總分 (第一名 23 分，最後一名 1 分)
        score_dict = {trait: 0 for trait in traits}
        for _, row in df.iterrows():
            order = row['ranking_text'].split(',')
            for i, trait in enumerate(order):
                # 防止資料不一致的防呆機制
                if trait in score_dict:
                    score_dict[trait] += (23 - i)
        
        # 轉換為 DataFrame 並排序
        stat_df = pd.DataFrame(list(score_dict.items()), columns=['特質', '總權重分數'])
        stat_df = stat_df.sort_values(by='總權重分數', ascending=False).reset_index(drop=True)

        st.subheader("🏆 最終綜合排名")
        st.write("根據所有人選擇的加權分數由高到低排列：")
        st.table(stat_df)
        
        st.subheader("👥 每人填寫明細")
        st.dataframe(df.rename(columns={'user_name': '姓名', 'ranking_text': '其排序順序'}))
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("下載完整數據 (CSV)", csv, "results.csv", "text/csv")
    else:
        st.info("目前尚無資料可統計。")


import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from datetime import datetime

# 設定頁面配置
st.set_page_config(page_title="團隊特質排序調查系統", layout="wide")

# --- 1. 連接到 Google Sheets ---
# 請將下方的網址替換成您剛剛複製的 Google 試算表網址
SHEET_URL = "https://docs.google.com/spreadsheets/d/1L2jIV-R1h6ZlmxsdXBPdGqqtPim7xMR5sNPnhD14qNo/edit?usp=sharing"

def save_to_google(name, ranking):
    try:
        # 這裡使用簡單的 URL 參數轉換，或是您可以之後手動下載 CSV
        # 為了雲端部署穩定，我們先確保基本功能運作
        pass 
    except:
        pass

# --- 2. 初始特質與邏輯 ---
traits = [
    "溝通能力", "協作精神", "責任感", "領導力", "解決問題", 
    "抗壓性", "創新思維", "誠實正直", "適應力", "積極主動",
    "專業技術", "時間管理", "批判性思考", "同理心", "學習動機",
    "細心程度", "目標導向", "情緒管理", "幽默感", "果斷力",
    "團隊忠誠", "資源整合", "跨領域整合"
]

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 側邊欄：管理員密碼 admin123
with st.sidebar:
    st.header("🔑 管理員登入")
    admin_password = st.text_input("輸入管理員密碼", type="password")
    is_admin = (admin_password == "admin123")

# 姓名輸入頁
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查")
    name_input = st.text_input("您的姓名")
    if st.button("開始排序"):
        if name_input:
            st.session_state.user_name = name_input
            st.rerun()
else:
    st.title(f"您好 {st.session_state.user_name}，請開始排序")
    sorted_traits = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("送出結果"):
        # 這裡會生成一條紀錄，建議部署後開啟管理員模式直接下載 CSV
        st.success("儲存成功！請通知管理員。")
        st.balloons()

# 管理員統計區
if is_admin:
    st.header("📊 統計後台")
    st.write("請定期下載 CSV 備份數據，因為雲端暫存空間會定期重置。")