import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 設定頁面配置
st.set_page_config(page_title="團隊特質排序系統", layout="wide")

# --- 1. 連接 Google Sheets ---
# 使用您提供的試算表網址
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1L2jIV-R1h6ZlmxsdXBPdGqqtPim7xMR5sNPnhD14qNo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 更新後的 23 項特質清單 ---
traits = [
    "責任感", "承載力", "事業跟人生分離", "持續力", "身教回看自己覺察", 
    "企圖心行動力", "缺乏動機", "自信", "輔導能力", "旁現深度連結", 
    "挑資源", "完美主義", "面對結果", "逆商抗錯能力", "缺乏凝聚力", 
    "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", 
    "缺乏傳遞價值能力", "報喜不報憂", "獨立能力"
]

# --- 3. 邏輯控制 ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 管理員登入 (側邊欄)
with st.sidebar:
    st.header("🔑 管理員登入")
    admin_password = st.text_input("輸入管理員密碼", type="password")
    is_admin = (admin_password == "admin123") # 預設密碼 admin123

# 第一頁：姓名輸入
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    st.write("請先輸入姓名以開始排序")
    name_input = st.text_input("您的姓名")
    if st.button("進入排序"):
        if name_input.strip():
            st.session_state.user_name = name_input
            st.rerun()
        else:
            st.error("請輸入姓名")

# 第二頁：排序操作
else:
    st.title(f"您好，{st.session_state.user_name}")
    st.write("請由上至下拖曳排列（最重要在最上面）：")
    
    # 拖曳組件
    sorted_traits = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("確認送出我的排序"):
        try:
            # 讀取現有資料
            existing_data = conn.read(spreadsheet=spreadsheet_url)
            
            # 準備新資料
            new_entry = pd.DataFrame([{
                "姓名": st.session_state.user_name,
                "排序結果": ",".join(sorted_traits),
                "提交時間": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }])
            
            # 合併並更新
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(spreadsheet=spreadsheet_url, data=updated_df)
            
            st.success("儲存成功！資料已同步至 Google 試算表。")
            st.balloons()
        except Exception as e:
            st.error(f"儲存失敗，請確保試算表已開啟編輯權限給「知道連結的人」。錯誤訊息: {e}")

# 管理員統計後台
if is_admin:
    st.divider()
    st.header("📊 管理員統計結果")
    try:
        data = conn.read(spreadsheet=spreadsheet_url)
        if not data.empty:
            st.subheader("👥 原始填寫資料")
            st.dataframe(data)
            
            # 加權計算邏輯
            score_dict = {trait: 0 for trait in traits}
            for _, row in data.iterrows():
                order = str(row['排序結果']).split(',')
                for i, t in enumerate(order):
                    if t in score_dict:
                        score_dict[t] += (23 - i)
            
            # 顯示綜合排名
            stat_df = pd.DataFrame(list(score_dict.items()), columns=['特質', '總權重分數'])
            stat_df = stat_df.sort_values(by='總權重分數', ascending=False).reset_index(drop=True)
            
            st.subheader("🏆 團隊綜合排名 (加權計分)")
            st.table(stat_df)
        else:
            st.info("目前尚無資料。")
    except:
        st.warning("無法讀取統計數據，請檢查試算表權限。")