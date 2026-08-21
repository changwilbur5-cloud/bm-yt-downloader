import os
import glob
import streamlit as st
import yt_dlp

# ==================== 頁面設定 ====================
st.set_page_config(
    page_title="波貓下載器 (直連下載版)", 
    page_icon="🐾", 
    layout="centered"
)

# ==================== 下載暫存資料夾 ====================
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def cleanup_old_files():
    """清理暫存區的舊檔案，避免佔用伺服器空間"""
    for f in glob.glob(f"{DOWNLOAD_DIR}/*"):
        try:
            os.remove(f)
        except Exception:
            pass

# ==================== 主頁面標題 ====================
st.title("🐾 波貓下載器 (直連下載版)")
st.write("選擇對應平台與格式，貼上網址即可快速解析下載！")

# ==================== 輸入介面 ====================
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

# ==================== 下載處理邏輯 ====================
if st.button("🚀 開始下載", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ 請先貼上有效的影片或音樂網址！")
    else:
        cleanup_old_files()
        status_box = st.info("⌛ 正在為您處理影片串流，請稍候...")
        
        is_audio = "MP3" in format_choice
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        # 設定 yt-dlp 選項，選取兼具高畫質與最佳相容性的格式
        if is_audio:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "no_warnings": True,
            }
        else:
            ydl_opts = {
                "format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url.strip(), download=True)
                video_title = info.get("title", "downloaded_media")

                # 尋找下載產生的檔案
                downloaded_files = glob.glob(f"{DOWNLOAD_DIR}/*")

                if downloaded_files:
                    target_file = downloaded_files[0]
                    file_name = os.path.basename(target_file)

                    status_box.empty()
                    st.success(f"✅ 解析成功！【{video_title}】")

                    # 讀取檔案二進位資料並透過 Streamlit 原生按鈕發送給手機
                    with open(target_file, "rb") as f:
                        file_bytes = f.read()

                    st.download_button(
                        label=f"💾 點我儲存到手機 ({'MP3 音訊' if is_audio else 'MP4 影片'})",
                        data=file_bytes,
                        file_name=file_name,
                        mime="audio/mp3" if is_audio else "video/mp4",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    status_box.empty()
                    st.error("❌ 找不到處理後的檔案，請重試！")

        except Exception as e:
            status_box.empty()
            st.error(f"❌ 解析失敗：{e}")
