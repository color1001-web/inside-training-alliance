import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 頁面配置
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# --- 1. 連接 Google Sheets ---
# 會自動讀取 Secrets 中的 spreadsheet 連結
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. 定義特質 (核心組加上前綴，移除燈號) ---
group_core = ["核心-責任感", "核心-承載力", "核心-事業跟人生分離", "核心-持續力", "核心-身教回看自己覺察", "核心-企圖心行動力", "核心-缺乏動機", "核心-自信"]
group_ability = ["輔導能力", "旁現深度連結", "挑資源", "完美主義", "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", "缺乏增員能力", "缺乏零售能力"]

traits = group_core + group_ability

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 第一頁：姓名
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("開始排序"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")

# 第二頁：排序
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.write("請由上至下拖曳排列特質（最重要在最上面）：")
    
    # 執行拖曳 (僅傳入純中文字串，避開編碼衝突)
    sorted_items = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 建立新資料列，強制轉為字串格式
            new_entry = pd.DataFrame([{
                "姓名": str(st.session_state.user_name),
                "排序結果": ",".join(sorted_items),
                "提交時間": pd.Timestamp.now(tz='Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
            }])

            # 讀取現有資料 (工作表1)
            # ttl=0 確保讀取的是即時資料而非快取
            existing_data = conn.read(worksheet="工作表1", ttl=0)
            
            # 合併新舊資料
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # 將 DataFrame 全體強制轉為字串並寫回
            conn.update(worksheet="工作表1", data=updated_df.astype(str))
            
            st.success("儲存成功！資料已同步至雲端表格。")
            st.balloons()
        except Exception as e:
            st.error("儲存失敗。請檢查 Secrets 設定或試算表『編輯者』權限。")
            st.code(str(e))