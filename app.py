import streamlit as st
import yt_dlp
import os
import tempfile
import sys
import subprocess

# 強制升級 yt-dlp 至 nightly 版本 (含最新反 403 補丁)
@st.cache_resource
def install_latest_ytdlp():
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "https://github.com/yt-dlp/yt-dlp/archive/master.zip"
        ])
    except Exception as e:
        st.sidebar.warning(f"自動更新 yt-dlp 失敗: {e}")

install_latest_ytdlp()

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (網頁跨平台版)")
st.write("輸入網址，選擇平台與格式即可快速下載！")

# 分割平台選項
folders = {
    "1": "YouTube",
    "2": "Douyin (抖音)",
    "3": "Instagram",
    "4": "Podcasts",
    "5": "Xiaohongshu (小紅書)"
}

# 介面元件
selected_platform = st.selectbox("1. 選擇平台：", list(folders.values()))
mode = st.radio("2. 選擇下載格式：", ["音訊 (MP3/Best Audio)", "影片 (MP4)"])

url = st.text_input("3. 請貼上影片/音訊網址：", placeholder="https://...")

if st.button("🚀 開始下載"):
    if url:
        st.info("⌛ 伺服器正在抓取與解析媒體，請稍候...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            # 高度擬真 User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            if "Xiaohongshu" in selected_platform or "xhs" in url or "xiaohongshu" in url:
                headers['Referer'] = 'https://www.xiaohongshu.com/'

            # 通用強效 yt-dlp 參數
            ydl_opts = {
                'outtmpl': save_path,
                'noplaylist': True,
                'quiet': True,
                'http_headers': headers,
                'no_check_certificate': True,
                # 多重 Client 繞過 403 驗證
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv', 'mweb', 'web_embedded', 'android'],
                        'player_js_version': ['actual']
                    }
                }
            }

            if "音訊" in mode:
                ydl_opts['format'] = 'bestaudio/best'
            else:
                # 避開 4K/獨立串流的 SABR 防火牆，改抓 1080p 以下最穩定的單一/整合格式
                ydl_opts['format'] = 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                st.success(f"✅ 解析成功！標題：{info.get('title', '媒體檔案')}")
                
                with open(filename, "rb") as file:
                    st.download_button(
                        label="💾 點我儲存檔案到裝置",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="audio/mpeg" if "音訊" in mode else "video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ 下載失敗！\n錯誤細節：{e}")
                st.warning("💡 提示：若持續出現 403，代表 Streamlit 雲端伺服器 IP 被平台暫時封鎖。建議等待片刻後重試，或試試看其他連結。")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
