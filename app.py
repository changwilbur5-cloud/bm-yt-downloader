import streamlit as st
import requests

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
if st.button("🚀 開始下載", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ 請先貼上有效的網址！")
    else:
        status_box = st.info("⌛ 正在建立專屬下載通道，請稍候...")
        is_audio = "MP3" in format_choice

        # 使用最新的 Cobalt 代理服務 API 端點
        api_url = "https://co.wuk.sh/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url.strip(),
            "isAudioOnly": is_audio,
            "aFormat": "mp3" if is_audio else "best",
            "vCodec": "h264"
        }

        try:
            res = requests.post(api_url, json=payload, headers=headers, timeout=15)
            data = res.json()
            status_box.empty()

            if res.status_code == 200 and "url" in data:
                download_link = data["url"]
                st.success("✅ 解析成功！請點擊下方按鈕下載：")
                
                st.markdown(
                    f'''
                    <a href="{download_link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                        <div style="
                            background-color: #28a745;
                            color: white;
                            padding: 14px 20px;
                            text-align: center;
                            border-radius: 8px;
                            font-size: 18px;
                            font-weight: bold;
                            margin-top: 10px;
                        ">
                            💾 點我開始下載 ({'MP3 音訊' if is_audio else 'MP4 影片'})
                        </div>
                    </a>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                # 備用方案：如果主 API 繁忙，自動切換至備用通道
                st.warning("⚠️ 主要通道繁忙，切換至備用解析通道...")
                alt_api_url = f"https://api.vevioz.com/api/button/mp3/{url.strip().split('/')[-1]}" if is_audio else f"https://api.vevioz.com/api/button/videos/{url.strip().split('/')[-1]}"
                st.markdown(f"🔗 [點此使用備用下載通道]({alt_api_url})")

        except Exception as e:
            status_box.empty()
            st.error("❌ 連線逾時，請再試一次或更換影片連結！")
