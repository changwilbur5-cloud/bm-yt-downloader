import streamlit as st
import yt_dlp
import requests

# 設定網頁標題與圖示
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
mode = st.radio("2. 選擇下載格式：", ["影片 (MP4)", "音訊 (MP3)"])

url = st.text_input("3. 請貼上影片/音訊網址：", placeholder="https://...")

if st.button("🚀 開始下載"):
    if url:
        st.info("⌛ 正在解析媒體通道，請稍候...")
        
        target_url = url.strip()
        
        # 使用多重極速 API 通道解析
        api_url = f"https://api.cobalt.tools/"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        payload = {
            "url": target_url,
            "videoQuality": "720" if "影片" in mode else "360",
            "downloadMode": "audio" if "音訊" in mode else "auto"
        }
        
        parsed = False
        
        # 優先嘗試 API 通道
        try:
            res = requests.post(api_url, json=payload, headers=headers, timeout=12)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") in ["stream", "redirect"]:
                    download_link = data.get("url")
                    st.success("✅ 解析成功！請點擊下方按鈕開啟/下載媒體：")
                    st.link_button("💾 點我下載檔案", download_link)
                    parsed = True
                elif data.get("status") == "picker":
                    st.success("✅ 解析成功！找到多個媒體檔案：")
                    for idx, item in enumerate(data.get("picker", []), start=1):
                        st.link_button(f"💾 下載項目 {idx}", item.get("url"))
                    parsed = True
        except Exception:
            pass

        # 備援通道：若 API 失敗，使用本地 yt-dlp 抽離直連網址
        if not parsed:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best' if "影片" in mode else 'bestaudio/best',
                    'extractor_args': {
                        'youtube': {'player_client': ['android', 'ios', 'mweb']}
                    }
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(target_url, download=False)
                    direct_url = info.get('url')
                    title = info.get('title', '媒體檔案')
                    
                    if direct_url:
                        st.success(f"✅ 解析成功！標題：{title}")
                        st.link_button("💾 點我看影片 / 長按儲存", direct_url)
                        parsed = True
            except Exception as e:
                st.error(f"❌ 解析失敗：{e}")
                st.warning("💡 小提醒：YouTube 目前對免費雲端主機封鎖極為嚴格，若多次失敗，建議換成抖音、IG、小紅書等平台連結測試！")
    else:
        st.warning("⚠️ 請先貼上有效的網址！")
