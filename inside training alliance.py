import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import re

# 網頁基本設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# --- 1. 連接 Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 定義特質清單 (使用 HTML 顏色標籤) ---
# 紅色組
group_red = [
    "責任感", "承載力", "事業跟人生分離", "持續力", 
    "身教回看自己覺察", "企圖心行動力", "缺乏動機", "自信"
]

# 藍色組
group_blue = [
    "輔導能力", "旁現深度連結", "挑資源", "完美主義", 
    "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", 
    "講目標願景", "善用資源", "專業能力", "締結心魔", 
    "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態",
    "缺乏增員能力", "缺乏零售能力"
]

# 在網頁顯示時，為文字加上顏色 HTML
display_traits = [f"<span style='color:#FF4B4B;'>{t}</span>" for t in group_red] + \
                 [f"<span style='color:#1C83E1;'>{t}</span>" for t in group_blue]

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
    st.write("請由上至下排列特質（最重要在最上面）：")
    
    # 執行拖曳組件
    sorted_items = sort_items(display_traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 【關鍵修復】：使用正規表達式移除 HTML 標籤，只保留純中文存入 Excel
            clean_traits = [re.sub('<[^<]+?>', '', t) for t in sorted_items]
            
            # 建立新資料
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(clean_traits),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])

            # [cite_start]讀取並寫回 工作表1 [cite: 1]
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(worksheet="工作表1", data=updated_df)
            
            st.success("儲存成功！Excel 資料已同步為純中文。")
            st.balloons()
        except Exception as e:
            st.error("儲存失敗，請檢查權限設定。")
            st.info(f"技術錯誤：{e}")