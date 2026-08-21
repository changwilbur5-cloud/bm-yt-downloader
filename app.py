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
    """乾淨提取 11 位數的 YouTube Video ID，自動去除 ?si= 等參數"""
    url_str = url_str.strip()
    
    # 處理 short link: https://youtu.be/Ntr0ZnRr7Qo?si=...
    if "youtu.be/" in url_str:
        path = url_str.split("youtu.be/")[1]
        video_id = path.split("?")[0].split("&")[0]
        return video_id[:11]
    
    # 處理 standard link: https://www.youtube.com/watch?v=Ntr0ZnRr7Qo
    if "watch" in url_str:
        parsed_url = urlparse(url_str)
        captured = parse_qs(parsed_url.query).get('v')
        if captured:
            return captured[0][:11]

    # 通用正則比對
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
            st.write("請選擇下方任一通道進行下載：")

            # 通道 1：Invidious 官方免封鎖直連通道
            audio_flag = "&listen=1" if is_audio else ""
            invidious_url = f"https://yewtu.be/watch?v={video_id}{audio_flag}"

            # 通道 2：Cobalt 網頁直連入口
            cobalt_url = f"https://cobalt.tools"

            st.markdown(
                f'''
                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
                    <a href="{invidious_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                        <div style="background-color: #28a745; color: white; padding: 12px; text-align: center; border-radius: 8px; font-weight: bold;">
                            ▶ 通道一：開啟線上無廣告播放 / 直接儲存
                        </div>
                    </a>
                    <a href="{cobalt_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                        <div style="background-color: #007bff; color: white; padding: 12px; text-align: center; border-radius: 8px; font-weight: bold;">
                            🌐 通道二：前往 Cobalt 工具頁面下載
                        </div>
                    </a>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            st.info("💡 **下載小撇步**：點擊「通道一」開啟頁面後，點擊影片右下角的三個點 `⋮` 即可選擇【下載】！")
        else:
            st.error("❌ 無法識別該 YouTube 網址，請確認連結格式是否正確！")
