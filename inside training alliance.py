import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 連接 Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 定義特質清單 (純中文，確保穩定性)
traits = [
    "核心-責任感", "核心-承載力", "核心-事業跟人生分離", "核心-持續力", 
    "核心-身教回看自己覺察", "核心-企圖心行動力", "核心-缺乏動機", "核心-自信",
    "輔導能力", "旁現深度連結", "挑資源", "完美主義", 
    "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", 
    "講目標願景", "善用資源", "專業能力", "締結心魔", 
    "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", 
    "缺乏增員能力", "缺乏零售能力"
]

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("開始進行"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.write("### 請依照『重要程度』選擇特質（第一個選的最重要）：")
    
    # 改用原生的多選盒，最穩定且支援中文
    selected = st.multiselect("請選擇特質（選取的順序即為您的排名）", traits)
    
    if st.button("✅ 確認送出我的排序"):
        if len(selected) < len(traits):
            st.warning(f"請選滿 {len(traits)} 項特質再送出。")
        else:
            try:
                new_entry = pd.DataFrame([{
                    "姓名": str(st.session_state.user_name),
                    "排序結果": ",".join(selected),
                    "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
                }])
                
                # 讀取現有資料 (分頁：工作表1)
                existing = conn.read(worksheet="工作表1", ttl=0)
                updated = pd.concat([existing, new_entry], ignore_index=True)
                
                # 存回雲端
                conn.update(worksheet="工作表1", data=updated.astype(str))
                st.success("數據儲存成功！")
                st.balloons()
            except Exception as e:
                st.error(f"儲存失敗：{e}")