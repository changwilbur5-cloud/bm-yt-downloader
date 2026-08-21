import streamlit as st
import re

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

# ==================== 下載解析邏輯 ====================
def extract_video_id(url_str):
    """提取 YouTube Video ID"""
    pattern = r'(?:v=|\/([0-9A-Za-z_-]{11})|youtu\.be\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url_str)
    if match:
        return match.group(1) or match.group(2)
    return None

if st.button("🚀 開始下載", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ 請先貼上有效的網址！")
    else:
        video_id = extract_video_id(url.strip())
        is_audio = "MP3" in format_choice

        if video_id:
            st.success("✅ 解析成功！請使用下方快速下載通道：")
            
            # 使用免 API Key 的開放前端下載服務通道
            if is_audio:
                dl_link = f"https://api.vevioz.com/api/button/mp3/{video_id}"
            else:
                dl_link = f"https://api.vevioz.com/api/button/videos/{video_id}"

            # 嵌入安全且快速的下載按鈕頁面
            st.markdown(
                f'''
                <div style="text-align: center; margin-top: 15px;">
                    <iframe src="{dl_link}" width="100%" height="180px" scrolling="no" style="border:none; border-radius:10px; background:#f8f9fa;"></iframe>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            st.info("💡 提示：點擊上方框內的【Download】即可直接存檔至手機！")
        else:
            st.error("❌ 無法識別該 YouTube 網址，請確認輸入是否正確！")
