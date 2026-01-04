import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 頁面基本設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# --- 1. 連接 Google Sheets ---
# 請確保您的 Streamlit Cloud Secrets 中已設定好連線資訊
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1L2jIV-R1h6ZlmxsdXBPdGqqtPim7xMR5sNPnhD14qNo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 定義 26 項特質清單 (使用顏色 Emoji 區分組別) ---
# 第一組：核心特質 (紅色)
group_red = [
    "🔴 責任感", "🔴 承載力", "🔴 事業跟人生分離", "🔴 持續力", 
    "🔴 身教回看自己覺察", "🔴 企圖心行動力", "🔴 缺乏動機", "🔴 自信"
]

# 第二組：能力發展 (藍色)
group_blue = [
    "🔵 輔導能力", "🔵 旁現深度連結", "🔵 挑資源", "🔵 完美主義", 
    "🔵 面對結果", "🔵 逆商抗錯能力", "🔵 缺乏凝聚力", "🔵 文化建立尊重", 
    "🔵 講目標願景", "🔵 善用資源", "🔵 專業能力", "🔵 締結心魔", 
    "🔵 缺乏傳遞價值能力", "🔵 報喜不報憂", "🔵 獨立能力", "🔵 空杯心態",
    "🔵 缺乏增員能力", "🔵 缺乏零售能力"
]

traits = group_red + group_blue

# --- 3. 頁面邏輯控制 ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 登入頁面
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    st.markdown("#### 請輸入您的姓名以開始進行排序")
    name_input = st.text_input("姓名", placeholder="例如：王小明")
    
    if st.button("進入系統"):
        if name_input.strip():
            st.session_state.user_name = name_input
            st.rerun()
        else:
            st.error("請填寫姓名")

# 排序頁面
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.markdown("""
    **排序指引：**
    1. 請將您認為「最重要」的特質拖拽至**最上方**。
    2. 🔴 為核心特質組，🔵 為能力發展組。
    3. 方塊顏色為淺灰色，點擊文字即可拖動。
    """)
    
    # 呼叫拖拽組件 (維持原生淺色方框風格)
    sorted_traits = sort_items(traits, multi_containers=False, direction="vertical")
    
    st.divider()
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 讀取 Google Sheets 中的現有資料 (預設工作表1)
            # 注意：若您的分頁名稱不同，請修改 worksheet 參數
            existing_data = conn.read(spreadsheet=spreadsheet_url, worksheet="工作表1")
            
            # 建立新的資料列
            new_entry = pd.DataFrame([{
                "姓名": st.session_state.user_name,
                "排序結果": ",".join(sorted_traits),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])
            
            # 合併並上傳
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(spreadsheet=spreadsheet_url, worksheet="工作表1", data=updated_df)
            
            st.success("提交成功！感謝您的參與，數據已同步至雲端報表。")
            st.balloons()
            
            # 提交後清除 session 避免重複提交
            if st.button("返回首頁"):
                st.session_state.user_name = None
                st.rerun()
                
        except Exception as e:
            st.error(f"儲存失敗，請檢查權限或網路連線。錯誤訊息: {e}")

# 管理員隱藏後台 (選用)
with st.sidebar:
    st.header("系統管理")
    show_raw = st.checkbox("顯示原始填寫數據")
    if show_raw:
        try:
            data = conn.read(spreadsheet=spreadsheet_url, worksheet="工作表1")
            st.dataframe(data)
        except:
            st.write("暫無數據")