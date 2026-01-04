import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# 網頁基本設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# --- 1. 連接 Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 重新定義特質名稱 (捨棄燈號，紅色組加上「核心」前綴) ---
group_core = [f"核心-{t}" for t in ["責任感", "承載力", "事業跟人生分離", "持續力", "身教回看自己覺察", "企圖心行動力", "缺乏動機", "自信"]]
group_ability = ["輔導能力", "旁現深度連結", "挑資源", "完美主義", "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", "缺乏增員能力", "缺乏零售能力"]

traits = group_core + group_ability

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 登入頁面
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("確認進入"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.write("請由上至下拖曳排列特質：")
    
    # 執行拖曳組件
    sorted_items = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 【終極修復】：將中文轉換為 URL 編碼，避開所有 ASCII 限制
            # 存入 Excel 前再還原成正常中文
            safe_name = urllib.parse.quote(st.session_state.user_name)
            safe_result = urllib.parse.quote(",".join(sorted_items))
            
            new_entry = pd.DataFrame([{
                "姓名": urllib.parse.unquote(safe_name),
                "排序結果": urllib.parse.unquote(safe_result),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])

            # 讀取現有資料 (工作表1) [cite: 1]
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # 強制轉換為字串並上傳
            conn.update(worksheet="工作表1", data=updated_df.astype(str))
            
            st.success("儲存成功！資料已同步至雲端。")
            st.balloons()
        except Exception as e:
            st.error("儲存失敗，請檢查權限或網路。")
            st.info(f"技術診斷：{e}")