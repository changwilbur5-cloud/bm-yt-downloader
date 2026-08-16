import streamlit as st
import requests
import json
import re

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (網頁跨平台版)")
st.write("輸入網址，選擇平台與格式即可快速下載！")

# 平台選單
folders = {
    "1": "YouTube",
    "2": "Douyin (抖音)",
    "3": "Instagram",
    "4": "Podcasts",
    "5": "Xiaohongshu (小紅書)"
}

selected_platform = st.selectbox("1. 選擇平台：", list(folders.values()))
mode = st.radio("2. 選擇下載格式：", ["影片 (MP4)", "音訊 (MP3)"])

url = st.text_input("3. 請貼上影片/音訊網址：", placeholder="https://...")

if st.button("🚀 開始下載"):
    if url:
        st.info("⌛ 正在透過雲端高安全性通道解析媒體，請稍候...")
        
        # 準備請求 Cobalt 代理 API
        cobalt_api_url = "https://api.cobalt.tools/"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        payload = {
            "url": url.strip(),
            "downloadMode": "audio" if "音訊" in mode else "auto",
            "videoQuality": "1080",
            "audioFormat": "mp3"
        }
        
        try:
            # 發送請求給 API 伺服器
            response = requests.post(cobalt_api_url, json=payload, headers=headers, timeout=15)
            data = response.json()
            
            # 判斷 API 回傳狀態
            status = data.get("status")
            
            if status in ["stream", "redirect"]:
                download_link = data.get("url")
                
                st.success("✅ 解析成功！請點擊下方按鈕開始下載：")
                st.link_button("💾 點我開啟/下載媒體檔案", download_link)
                
            elif status == "picker":
                # 如果是小紅書或多圖/多影片貼文
                st.success("✅ 解析成功！找到多個媒體檔案：")
                picker_items = data.get("picker", [])
                for idx, item in enumerate(picker_items, start=1):
                    item_url = item.get("url")
                    st.link_button(f"💾 下載項目 {idx}", item_url)
                    
            else:
                error_msg = data.get("text", "無法解析此連結")
                st.error(f"❌ 解析失敗：{error_msg}")
                st.info("💡 提示：請確認輸入的網址是否正確，或嘗試重新點擊一次下載。")

        except Exception as e:
            st.error(f"❌ 連線異常或 API 服務忙碌中：{e}")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
