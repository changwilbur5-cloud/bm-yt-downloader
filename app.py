import streamlit as st
import yt_dlp
import os
import tempfile
import sys
import subprocess
import requests

# 確保 yt-dlp 保持最新版
@st.cache_resource
def install_latest_ytdlp():
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "https://github.com/yt-dlp/yt-dlp/archive/master.zip"
        ])
    except Exception as e:
        pass

install_latest_ytdlp()

# 還原短網址
def resolve_url(url):
    if "xhslink" in url or "youtu.be" in url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15'
            }
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=8)
            resolved = response.url
            if "explore" in resolved or "404" in resolved:
                if response.history:
                    return response.history[0].headers.get('Location', url)
            return resolved
        except Exception:
            return url
    return url

st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (網頁跨平台版)")
st.write("輸入網址，選擇平台與格式即可快速下載！")

folders = {
    "1": "YouTube",
    "2": "Douyin (抖音)",
    "3": "Instagram",
    "4": "Podcasts",
    "5": "Xiaohongshu (小紅書)"
}

selected_platform = st.selectbox("1. 選擇平台：", list(folders.values()))
mode = st.radio("2. 選擇下載格式：", ["音訊 (MP3/Best Audio)", "影片 (MP4)"])

url = st.text_input("3. 請貼上影片/音訊網址：", placeholder="https://...")

if st.button("🚀 開始下載"):
    if url:
        st.info("⌛ 伺服器正在解析網址與抓取媒體，請稍候...")
        
        target_url = resolve_url(url.strip())
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            if "Xiaohongshu" in selected_platform or "xiaohongshu" in target_url:
                headers['Referer'] = 'https://www.xiaohongshu.com/'

            # 針對 YouTube 避開 403 的特別設定檔
            ydl_opts = {
                'outtmpl': save_path,
                'noplaylist': True,
                'quiet': True,
                'http_headers': headers,
                'no_check_certificate': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                # 使用 iOS / Android client 避開 Cloud 封鎖
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android', 'mweb'],
                        'skip': ['hls', 'dash']
                    }
                }
            }

            if "音訊" in mode:
                ydl_opts['format'] = 'ba/ba*'
            else:
                # 只抓取整合好的單一 mp4 檔案，防止 SABR 串流阻擋
                ydl_opts['format'] = 'b[ext=mp4]/b/best'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(target_url, download=True)
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
                st.warning("💡 **說明**：免費雲端伺服器 (Streamlit) 的 IP 近期被 YouTube 嚴格封鎖。如果依然顯示 403，建議更換為非 YouTube 平台的連結（如 Instagram、抖音），或是稍後再試！")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
