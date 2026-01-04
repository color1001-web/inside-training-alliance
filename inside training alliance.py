import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁基本設定
st.set_page_config(page_title="團隊特質排序系統", layout="wide")

# --- 1. 連接 Google Sheets ---
# 務必確認您的 Secrets 裡 spreadsheet 網址正確
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1L2jIV-R1h6ZlmxsdXBPdGqqtPim7xMR5sNPnhD14qNo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 26 項特質清單 (統一加上 Emoji 避免編碼抓取失敗) ---
group_red = ["🔴 責任感", "🔴 承載力", "🔴 事業跟人生分離", "🔴 持續力", "🔴 身教回看自己覺察", "🔴 企圖心行動力", "🔴 缺乏動機", "🔴 自信"]
group_blue = ["🔵 輔導能力", "🔵 旁現深度連結", "🔵 挑資源", "🔵 完美主義", "🔵 面對結果", "🔵 逆商抗錯能力", "🔵 缺乏凝聚力", "🔵 文化建立尊重", "🔵 講目標願景", "🔵 善用資源", "🔵 專業能力", "🔵 締結心魔", "🔵 缺乏傳遞價值能力", "🔵 報喜不報憂", "🔵 獨立能力", "🔵 空杯心態", "🔵 缺乏增員能力", "🔵 缺乏零售能力"]
traits = group_red + group_blue

# --- 3. 頁面邏輯 ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 第一頁：姓名輸入
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("確認進入"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")

# 第二頁：排序頁面
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.write("請由上至下排列特質（最重要在最上面）")
    
    sorted_traits = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 建立新資料列並強制轉為字串避免編碼問題
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(sorted_traits),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }]).astype(str)
            
            # 讀取現有資料 (確認分頁名稱為 工作表1)
            existing_data = conn.read(spreadsheet=spreadsheet_url, worksheet="工作表1")
            
            # 合併並寫回
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(spreadsheet=spreadsheet_url, worksheet="工作表1", data=updated_df)
            
            st.success("儲存成功！資料已同步至雲端表格。")
            st.balloons()
            
            # 提交後提供重置按鈕
            if st.button("返回首頁"):
                st.session_state.user_name = None
                st.rerun()
        except Exception as e:
            st.error("儲存失敗。請檢查試算表權限是否已設為『編輯者』。")
            st.info(f"技術錯誤訊息：{e}")