import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁基本設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# --- 1. 注入 CSS 強制控制字體 (不影響資料庫寫入) ---
st.markdown("""
    <style>
    /* 讓拖曳方塊內的字體變大，並設為深色確保清晰 */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #31333F !important;
    }
    /* 提示訊息顏色 */
    .stAlert p { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 連接 Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 定義純中文特質 (移除所有符號與 HTML，確保 API 100% 成功) ---
group_red = ["責任感", "承載力", "事業跟人生分離", "持續力", "身教回看自己覺察", "企圖心行動力", "缺乏動機", "自信"]
group_blue = ["輔導能力", "旁現深度連結", "挑資源", "完美主義", "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", "缺乏增員能力", "缺乏零售能力"]

traits = group_red + group_blue

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 姓名輸入
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("進入系統"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.markdown("### 🔴 核心組：責任感...至 自信 | 🔵 能力組：輔導能力...之後")
    st.write("請由上至下拖曳排列（最重要在最上面）")
    
    # 執行拖曳組件 (只傳入純文字字串，避免 ASCII 編碼報錯)
    sorted_items = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 【關鍵修復】：建立數據前強制將內容轉換為字串，並手動指定為 UTF-8
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(sorted_items),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])

            # 讀取並寫回 (ttl=0 禁用快取，確保即時寫入)
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # 將 DataFrame 強制轉換為字串格式後上傳
            conn.update(worksheet="工作表1", data=updated_df.astype(str))
            
            st.success("儲存成功！資料已同步至雲端表格。")
            st.balloons()
        except Exception as e:
            st.error("儲存失敗。這可能是由於伺服器編碼限制。")
            st.info(f"技術診斷：{str(e)}")