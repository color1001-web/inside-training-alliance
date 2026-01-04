import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 連接 Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 定義特質清單 (網頁上顯示時帶有顏色方便辨識)
group_red = ["🔴 責任感", "🔴 承載力", "🔴 事業跟人生分離", "🔴 持續力", "🔴 身教回看自己覺察", "🔴 企圖心行動力", "🔴 缺乏動機", "🔴 自信"]
group_blue = ["🔵 輔導能力", "🔵 旁現深度連結", "🔵 挑資源", "🔵 完美主義", "🔵 一般面對結果", "🔵 逆商抗錯能力", "🔵 缺乏凝聚力", "🔵 文化建立尊重", "🔵 講目標願景", "🔵 善用資源", "🔵 專業能力", "🔵 締結心魔", "🔵 缺乏傳遞價值能力", "🔵 報喜不報憂", "🔵 獨立能力", "🔵 空杯心態", "🔵 缺乏增員能力", "🔵 缺乏零售能力"]
traits = group_red + group_blue

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("確認進入"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請填寫姓名")
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.write("請由上至下排列特質（最重要在最上面）")
    
    sorted_traits = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 【關鍵優化】：過濾掉 🔴 和 🔵 符號，只保留純中文存入 Excel
            clean_traits = [t.replace("🔴 ", "").replace("🔵 ", "") for t in sorted_traits]
            
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(clean_traits),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])
            
            # [cite_start]讀取現有資料並寫回 [cite: 1]
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(worksheet="工作表1", data=updated_df)
            
            st.success("儲存成功！Excel 中的資料現在已是純中文，方便您統計。")
            st.balloons()
        except Exception as e:
            st.error(f"儲存失敗，請確認試算表權限。技術錯誤：{e}")