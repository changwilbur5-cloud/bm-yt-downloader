import streamlit as st
import requests
import json
import re

# 清理網址參數與標準化
def clean_url(raw_url):
    url = raw_url.strip()
    # 移除 YouTube / 小紅書 的 si、share_token 等追蹤參數
    if "?" in url:
        url = url.split("?")[0]
    return url

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
        
        target_url = clean_url(url)
        
        # Cobalt API 完整請求標頭
        cobalt_api_url = "https://api.cobalt.tools/"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://cobalt.tools",
            "Referer": "https://cobalt.tools/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        payload = {
            "url": target_url,
            "downloadMode": "audio" if "音訊" in mode else "auto",
            "videoQuality": "1080",
            "audioFormat": "mp3"
        }
        
        try:
            response = requests.post(cobalt_api_url, json=payload, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status in ["stream", "redirect"]:
                    download_link = data.get("url")
                    st.success("✅ 解析成功！請點擊下方按鈕開始下載：")
                    st.link_button("💾 點我開啟/下載媒體檔案", download_link)
                    
                elif status == "picker":
                    st.success("✅ 解析成功！找到多個媒體檔案：")
                    picker_items = data.get("picker", [])
                    for idx, item in enumerate(picker_items, start=1):
                        item_url = item.get("url")
                        st.link_button(f"💾 下載項目 {idx}", item_url)
                else:
                    error_msg = data.get("text", "無法解析此連結")
                    st.error(f"❌ 解析失敗：{error_msg}")
            else:
                st.error(f"❌ 伺服器回應異常 ({response.status_code})，請稍後重試。")

        except Exception as e:
            st.error(f"❌ 連線逾時或 API 服務忙碌中：{e}")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
