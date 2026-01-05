import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁配置
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# --- 1. 連接 Google Sheets ---
# 從 Secrets 讀取連結，請確保您的 Secrets 網址正確
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 定義特質 (核心組標註「核心-」，能力組維持原樣) ---
group_core = [f"核心-{t}" for t in ["責任感", "承載力", "事業跟人生分離", "持續力", "身教回看自己覺察", "企圖心行動力", "缺乏動機", "自信"]]
group_ability = ["輔導能力", "旁現深度連結", "挑資源", "完美主義", "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", "缺乏增員能力", "缺乏零售能力"]

traits = group_core + group_ability

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 姓名輸入
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("進入排序"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.write("請由上至下拖曳排列特質（最重要在最上面）：")
    
    # 執行拖曳元件
    sorted_items = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 【關鍵修復點】：建立 DataFrame 並將所有繁體中文字串強制轉為標準格式
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(map(str, sorted_items)),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])

            # 讀取現有資料並合併 (分頁：工作表1)
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # 強制將整個表格轉換為字串格式後上傳，避免 ASCII 編碼報錯
            conn.update(worksheet="工作表1", data=updated_df.astype(str))
            
            st.success("數據儲存成功！資料已同步至雲端表格。")
            st.balloons()
        except Exception as e:
            st.error("儲存失敗。請檢查試算表權限。")
            # 顯示技術診斷資訊
            st.code(str(e))