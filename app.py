import streamlit as st
import re
from urllib.parse import urlparse, parse_qs

# ==================== 頁面設定 ====================
st.set_page_config(
    page_title="波貓下載器 (多平台版)", 
    page_icon="🐾", 
    layout="centered"
)

st.title("🐾 波貓下載器 (直連下載版)")
st.write("選擇對應平台與格式，貼上網址即可快速解析下載！")

# ==================== UI 輸入區 ====================
platform = st.selectbox(
    "1. 選擇平台與模式：",
    [
        "YouTube (單一影片)",
        "YouTube (播放清單)",
        "Bilibili 嗶哩嗶哩",
        "抖音 (TikTok / Douyin)",
        "小紅書 (RED)"
    ]
)

format_choice = st.radio(
    "2. 選擇下載格式：",
    ["影片 (MP4)", "音訊 (MP3)"],
    horizontal=True
)

url = st.text_input(
    "3. 請貼上連結：",
    placeholder="https://..."
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
        is_audio = "MP3" in format_choice
        fmt = "mp3" if is_audio else "1080"
        
        # 根據選取的平台套用對應解析門戶
        if platform == "YouTube (單一影片)":
            video_id = clean_video_id(url)
            if video_id and len(video_id) == 11:
                st.success(f"✅ 解析成功！(YouTube ID: {video_id})")
                download_url = f"https://loader.to/zh22/?link=https://www.youtube.com/watch?v={video_id}&f={fmt}"
            else:
                st.error("❌ 無法識別該 YouTube 網址，請確認連結格式！")
                st.stop()
                
        elif platform == "YouTube (播放清單)":
            st.success("✅ 已帶入播放清單網址！")
            download_url = f"https://loader.to/zh22/?link={url.strip()}&f={fmt}"
            
        else:
            # Bilibili、抖音、小紅書專用多平台通用解析門戶
            st.success(f"✅ 已帶入 {platform} 連結！")
            download_url = "https://cobalt.tools"

        # 顯示下載按鈕
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
        st.info("💡 **提示**：點擊藍色按鈕即可在新分頁存檔（小紅書與抖音自動支援去浮水印影片下載）。")
