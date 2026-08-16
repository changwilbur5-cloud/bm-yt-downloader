import streamlit as st
import yt_dlp
import os
import tempfile
import sys
import subprocess
import requests

# 自動更新 yt-dlp
@st.cache_resource
def install_latest_ytdlp():
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "https://github.com/yt-dlp/yt-dlp/archive/master.zip"
        ])
    except Exception:
        pass

install_latest_ytdlp()

# 還原短網址 (小紅書 / YouTube 短網址)
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
            }

            if "Xiaohongshu" in selected_platform or "xiaohongshu" in target_url:
                headers['Referer'] = 'https://www.xiaohongshu.com/'

            # 防 403 終極參數：引入 Invidious 公用代理節點 + 停用 Dash
            ydl_opts = {
                'outtmpl': save_path,
                'noplaylist': True,
                'quiet': True,
                'http_headers': headers,
                'no_check_certificate': True,
                'nocheckcertificate': True,
                'extractor_args': {
                    'youtube': {
                        'invidious_instance': ['https://invidious.nerdvpn.de', 'https://inv.us.projectsegfau.lt', 'https://invidious.flokinet.to'],
                        'player_client': ['android', 'ios', 'mweb'],
                        'skip': ['dash', 'hls']
                    }
                }
            }

            if "音訊" in mode:
                ydl_opts['format'] = 'ba/bestaudio/best'
            else:
                ydl_opts['format'] = 'b[ext=mp4]/best[ext=mp4]/best'

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
                st.warning("💡 **小提醒**：如果 YouTube 依然被阻擋，代表各公用機房正遭受嚴格限制，建議優先測試 抖音、Instagram 或 Podcast 等其他平台！")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
