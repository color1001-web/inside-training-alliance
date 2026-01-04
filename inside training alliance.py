import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁基本設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 強制注入 CSS：讓網頁文字變大，並美化介面
st.markdown("""
    <style>
    .stMarkdown p { font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 連接 Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 定義特質清單 (純中文，避免編碼出錯) ---
# 紅色組 (核心)
group_red = ["責任感", "承載力", "事業跟人生分離", "持續力", "身教回看自己覺察", "企圖心行動力", "缺乏動機", "自信"]
# 藍色組 (能力)
group_blue = ["輔導能力", "旁現深度連結", "挑資源", "完美主義", "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", "缺乏增員能力", "缺乏零售能力"]

traits = group_red + group_blue

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
    st.info("💡 排序指引：請將特質由上至下拖曳排列（最重要在最上面）")
    
    # 執行拖曳組件 (使用純中文，確保穩定性)
    sorted_items = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 【關鍵修復】：強制使用 UTF-8 編碼處理字串，徹底避開 ASCII 錯誤
            # 同時確保所有傳入 Google Sheets 的資料都是純淨的字串
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(sorted_items),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }]).astype(str)

            # 讀取並寫回 工作表1
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # 使用更穩定的更新方式
            conn.update(worksheet="工作表1", data=updated_df)
            
            st.success("儲存成功！下週打開 Excel 即可看到統計報表。")
            st.balloons()
        except Exception as e:
            st.error("儲存失敗。請檢查 Secrets 設定或試算表權限。")
            st.info(f"系統錯誤碼：{e}")