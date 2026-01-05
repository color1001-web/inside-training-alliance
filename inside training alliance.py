import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 基本網頁設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 連接 Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 定義特質清單 (必須與統計報表 A 欄文字完全一致)
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

# 第一階段：姓名輸入
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("確認進入"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")

# 第二階段：排序操作
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.info("💡 操作說明：請從選單中選取特質，『第一個選的』代表最重要，請依序排滿 26 項。")
    
    # 使用原生組件，支援繁體中文且傳輸極度穩定
    selected = st.multiselect("請選取特質 (選取的順序即為您的排名)", traits)
    
    if st.button("✅ 確認送出我的排序"):
        if len(selected) < len(traits):
            st.warning(f"請選滿 26 項。目前已選：{len(selected)} 項。")
        else:
            try:
                # 建立數據並強制轉為字串格式
                new_entry = pd.DataFrame([{
                    "姓名": str(st.session_state.user_name),
                    "排序結果": ",".join(selected),
                    "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
                }])
                
                # 讀取並合併 (分頁：工作表1)
                existing = conn.read(worksheet="工作表1", ttl=0)
                updated = pd.concat([existing, new_entry], ignore_index=True)
                
                # 強制轉換為字串上傳，繞過所有編碼報錯
                conn.update(worksheet="工作表1", data=updated.astype(str))
                st.success("成功！數據已同步至雲端表格。")
                st.balloons()
            except Exception as e:
                st.error("儲存失敗，請檢查試算表權限。")
                st.exception(e)