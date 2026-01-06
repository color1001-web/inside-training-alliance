import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
import os
from datetime import datetime

# 網頁配置
st.set_page_config(page_title="團隊特質調查系統", layout="wide")

# 定義 CSV 檔案路徑
DATA_FILE = "survey_results.csv"

# 定義特質清單 (核心組加上「核心-」前綴)
group_core = ["核心-責任感", "核心-承載力", "核心-事業跟人生分離", "核心-持續力", "核心-身教回看自己覺察", "核心-企圖心行動力", "核心-缺乏動機", "核心-自信"]
group_ability = ["輔導能力", "旁現深度連結", "挑資源", "完美主義", "一般面對結果", "逆商抗錯能力", "缺乏凝聚力", "文化建立尊重", "講目標願景", "善用資源", "專業能力", "締結心魔", "缺乏傳遞價值能力", "報喜不報憂", "獨立能力", "空杯心態", "缺乏增員能力", "缺乏零售能力"]
traits = group_core + group_ability

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# 第一階段：姓名輸入
if st.session_state.user_name is None:
    st.title("📋 團隊特質調查系統")
    name = st.text_input("您的姓名")
    if st.button("開始排序"):
        if name.strip():
            st.session_state.user_name = name
            st.rerun()
        else:
            st.error("請輸入姓名")

# 第二階段：上下拖曳排序
else:
    st.title(f"你好，{st.session_state.user_name}")
    st.info("💡 操作說明：請由上至下拖曳特質進行排序，最重要者放在最上方。")
    
    # 直觀的拖曳組件
    sorted_items = sort_items(traits, multi_containers=False, direction="vertical")
    
    if st.button("✅ 確認送出我的排序"):
        try:
            # 建立基礎資訊：姓名與時間
            entry_dict = {
                "姓名": st.session_state.user_name,
                "提交時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 【關鍵優化】：將 26 個特質分別放入「第 1 名」到「第 26 名」的欄位中
            for i, trait in enumerate(sorted_items):
                entry_dict[f"第{i+1}名"] = trait
            
            new_data = pd.DataFrame([entry_dict])
            
            # 寫入 CSV 檔案 (使用 utf-8-sig 確保 Excel 打開不亂碼)
            if not os.path.isfile(DATA_FILE):
                new_data.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            else:
                new_data.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
            
            st.success("數據儲存成功！感謝您的參與。")
            st.balloons()
            
        except Exception as e:
            st.error(f"儲存過程發生錯誤：{e}")

# 側邊欄：下載功能
if os.path.isfile(DATA_FILE):
    st.sidebar.title("管理員功能")
    with open(DATA_FILE, "rb") as file:
        st.sidebar.download_button(
            label="📥 下載完整調查結果 (CSV)",
            data=file,
            file_name="team_traits_final.csv",
            mime="text/csv"
        )