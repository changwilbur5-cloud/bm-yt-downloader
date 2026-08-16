import streamlit as st
import yt_dlp
import os
import tempfile

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (網頁跨平台版)")
st.write("輸入網址，選擇平台與格式即可快速下載！")

# 分割平台選項（含小紅書）
folders = {
    "1": "YouTube",
    "2": "Douyin (抖音)",
    "3": "Instagram",
    "4": "Podcasts",
    "5": "Xiaohongshu (小紅書)"
}

# 介面元件 - 下拉選單與輸入框
selected_platform = st.selectbox("1. 選擇平台：", list(folders.values()))
mode = st.radio("2. 選擇下載格式：", ["音訊 (MP3/Best Audio)", "影片 (MP4)"])

url = st.text_input("3. 請貼上影片/音訊網址：", placeholder="https://...")

if st.button("🚀 開始下載"):
    if url:
        st.info("⌛ 伺服器正在抓取與解析媒體，請稍候...")
        
        # 建立臨時目錄供雲端伺服器暫存
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            # 通用的防封鎖與偽裝 Header
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Sec-Fetch-Mode': 'navigate',
            }

            # 針對小紅書加入專用 Referer 偽裝
            if "Xiaohongshu" in selected_platform or "xhslink" in url or "xiaohongshu" in url:
                headers['Referer'] = 'https://www.xiaohongshu.com/'

            # 依格式設定 yt-dlp 參數
            if "音訊" in mode:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': save_path,
                    'noplaylist': True,
                    'quiet': True,
                    'http_headers': headers,
                }
            else:
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': save_path,
                    'noplaylist': True,
                    'quiet': True,
                    'http_headers': headers,
                }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                st.success(f"✅ 解析成功！標題：{info.get('title', '媒體檔案')}")
                
                # 提供下載按鈕
                with open(filename, "rb") as file:
                    st.download_button(
                        label="💾 點我儲存檔案到裝置",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="audio/mpeg" if "音訊" in mode else "video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ 下載失敗，請檢查網址或平台限制。\n錯誤訊息：{e}")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
