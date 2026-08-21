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
            
            # 使用高相容性的解析入口點
            format_type = "mp3" if is_audio else "1080"
            download_portal = f"https://loader.to/api/card/?url=https://www.youtube.com/watch?v={video_id}&f={format_type}"

            st.markdown(
                f'''
                <div style="margin-top: 15px;">
                    <iframe src="{download_portal}" width="100%" height="250px" scrolling="no" style="border:none; border-radius:10px; background:#ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05);"></iframe>
                </div>
                ''',
                unsafe_allow_html=True
            )
            st.info("💡 **操作說明**：請在上方框內點擊【Download】，進度條跑完後即可直接儲存檔案至手機！")
        else:
            st.error("❌ 無法識別該 YouTube 網址，請確認連結格式是否正確！")
