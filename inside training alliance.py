import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 網頁配置
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 定義存檔路徑
DATA_FILE = "survey_results.csv"

# 特質清單 (核心組加上「核心-」，移除所有 Emoji 以保證穩定)
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
    st.title("📋 團隊特質調查系統 (CSV版)")
    name = st.text_input("您的姓名")
    if st.button("開始排序"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")

# 第二階段：排序操作
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.info("💡 操作說明：請在下方選單中『依序選取』特質。第一個選的代表最重要，請選滿 26 個。")
    
    # 使用內建 multiselect，支援繁體中文且不會報碼錯誤
    selected = st.multiselect("請依照重要程度選取特質", traits)
    
    if st.button("✅ 確認送出我的排序"):
        if len(selected) < len(traits):
            st.warning(f"請選滿 26 項特質。目前已選：{len(selected)} 項。")
        else:
            try:
                # 建立新數據
                new_data = pd.DataFrame([{
                    "姓名": st.session_state.user_name,
                    "排序結果": ",".join(selected),
                    "提交時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }])
                
                # 檢查檔案是否存在，決定是寫入還是附加
                if not os.path.isfile(DATA_FILE):
                    new_data.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                else:
                    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
                
                st.success("數據儲存成功！")
                st.balloons()
                
                # 顯示目前已蒐集的資料 (僅管理員或測試用)
                with st.expander("查看目前已收集的資料"):
                    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
                    st.dataframe(df)
                    
            except Exception as e:
                st.error(f"儲存失敗：{e}")

# 下載按鈕 (讓您可以把 CSV 載回電腦貼上 Excel)
if os.path.isfile(DATA_FILE):
    st.sidebar.markdown("---")
    with open(DATA_FILE, "rb") as file:
        st.sidebar.download_button(
            label="📥 下載完整資料 (CSV)",
            data=file,
            file_name="team_traits_results.csv",
            mime="text/csv"
        )