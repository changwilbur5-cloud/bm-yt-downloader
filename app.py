import streamlit as st
import re
from urllib.parse import urlparse, parse_qs

# ==================== 頁面設定 ====================
st.set_page_config(
    page_title="波貓下載器 (直連下載版)", 
    page_icon="🐾", 
    layout="centered"
)

st.title("🐾 波貓下載器 (直連下載版)")
st.write("選擇對應平台與格式，貼上網址即可快速解析下載！")

# ==================== UI 輸入區 ====================
platform = st.selectbox(
    "1. 選擇平台與模式：",
    ["YouTube (單一影片/音訊)"]
)

format_choice = st.radio(
    "2. 選擇下載格式：",
    ["影片 (MP4)", "音訊 (MP3)"],
    horizontal=True
)

url = st.text_input(
    "3. 請貼上連結：",
    placeholder="https://youtu.be/..."
)

# ==================== 精確提取 Video ID ====================
def clean_video_id(url_str):
    """乾淨提取 11 位數的 YouTube Video ID"""
    url_str = url_str.strip()
    if "youtu.be/" in url_str:
        path = url_str.split("youtu.be/")[1]
        video_id = path.split("?")[0].split("&")[0]
        return video_id[:11]
    if "watch" in url_str:
        parsed_url = urlparse(url_str)
        captured = parse_qs(parsed_url.query).get('v')
        if captured:
            return captured[0][:11]
    match = re.search(r'([a-zA-Z0-9_-]{11})', url_str)
    if match:
        return match.group(1)
    return None

# ==================== 下載解析邏輯 ====================
if st.button("🚀 開始下載", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ 請先貼上有效的網址！")
    else:
        video_id = clean_video_id(url)
        is_audio = "MP3" in format_choice

        if video_id and len(video_id) == 11:
            st.success(f"✅ 解析成功！(影片 ID: {video_id})")
            
            # 直連解析服務門戶 (免嵌入、防封鎖)
            fmt = "mp3" if is_audio else "1080"
            download_url = f"https://loader.to/zh22/?link=https://www.youtube.com/watch?v={video_id}&f={fmt}"

            # 使用大型導向按鈕，避開 iframe 限制
            st.markdown(
                f'''
                <a href="{download_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                    <div style="
                        background-color: #0891b2;
                        color: white;
                        padding: 16px;
                        text-align: center;
                        border-radius: 10px;
                        font-size: 18px;
                        font-weight: bold;
                        margin-top: 15px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    ">
                        📥 點我開啟快捷下載頁面 ({'MP3 音樂' if is_audio else 'MP4 影片'})
                    </div>
                </a>
                ''',
                unsafe_allow_html=True
            )
            
            st.info("💡 **下載說明**：點擊上方藍色按鈕會新開頁面，系統已為您帶入此影片，直接按【Download】即可存檔至手機！")
        else:
            st.error("❌ 無法識別該 YouTube 網址，請確認連結格式是否正確！")
