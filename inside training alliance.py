import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁基本設定
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 連接 Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 特質清單 (請確保名稱與您 Google Sheets 統計報表 A 欄完全一致)
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
    st.title(f"你好，{st.session_state.user_name}")
    st.info("💡 操作說明：請點擊下方選單選擇特質，『第一個選的』代表最重要，依此類推排滿 26 項。")
    
    # 使用內建 multiselect，支援繁體中文且傳輸穩定
    selected = st.multiselect("請選取並排序特質", traits)
    
    if st.button("✅ 確認送出我的排序"):
        if len(selected) < len(traits):
            st.warning(f"請選滿 {len(traits)} 項特質。目前已選：{len(selected)} 項。")
        else:
            try:
                # 建立數據
                new_entry = pd.DataFrame([{
                    "姓名": str(st.session_state.user_name),
                    "排序結果": ",".join(selected),
                    "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
                }])
                
                # 讀取現有資料並寫回 (工作表1)
                existing = conn.read(worksheet="工作表1", ttl=0)
                updated = pd.concat([existing, new_entry], ignore_index=True)
                
                # 強制轉換為字串上傳，避開所有編碼問題
                conn.update(worksheet="工作表1", data=updated.astype(str))
                st.success("數據儲存成功！資料已同步至雲端表格。")
                st.balloons()
            except Exception as e:
                st.error(f"儲存失敗，請確認 Secrets 設定。技術提示：{e}")