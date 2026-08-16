import streamlit as st
import yt_dlp
import requests

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (直連下載版)")
st.write("選擇對應平台與格式，貼上網址即可快速解析下載！")

# 分類平台選項
platform_options = [
    "YouTube (單一影片/音訊)",
    "YouTube (播放清單批次下載)",
    "Douyin (抖音)",
    "Instagram",
    "Podcasts",
    "Xiaohongshu (小紅書)"
]

selected_platform = st.selectbox("1. 選擇平台與模式：", platform_options)
mode = st.radio("2. 選擇下載格式：", ["影片 (MP4)", "音訊 (MP3)"])

url = st.text_input("3. 請貼上連結：", placeholder="https://...")

is_playlist_mode = "播放清單" in selected_platform

# 嘗試取得直接音訊/影片串流
def get_direct_stream_url(video_url, is_audio):
    # 提取 Video ID
    video_id = None
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]
        
    if not video_id:
        return None, None
        
    # 通道 A: Piped 免費 API
    try:
        res = requests.get(f"https://pipedapi.kavin.rocks/streams/{video_id}", timeout=5)
        if res.status_code == 200:
            data = res.json()
            if is_audio:
                audio_streams = data.get("audioStreams", [])
                if audio_streams:
                    return audio_streams[0].get("url"), "audio"
            else:
                video_streams = data.get("videoStreams", [])
                for s in video_streams:
                    if not s.get("videoOnly"):
                        return s.get("url"), "video"
    except Exception:
        pass

    # 通道 B: Invidious
    invidious_link = f"https://yewtu.be/watch?v={video_id}"
    return invidious_link, "page"

# --- 模式 A：播放清單模式 ---
if is_playlist_mode:
    if st.button("🔍 解析播放清單"):
        if url:
            st.session_state['parsed_url'] = url.strip()
            st.session_state['parse_trigger'] = True
        else:
            st.warning("⚠️ 請先貼上有效的播放清單網址！")

    if st.session_state.get('parse_trigger') and st.session_state.get('parsed_url'):
        target_url = st.session_state['parsed_url']
        st.info("⌛ 正在讀取播放清單內容，請稍候...")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)
                
                if 'entries' in info:
                    entries = [e for e in info['entries'] if e]
                    st.success(f"📋 偵測到播放清單：「{info.get('title', '播放清單')}」，共 {len(entries)} 項。")
                    
                    col_all, col_none = st.columns([1, 1])
                    select_all = col_all.button("✅ 全部勾選")
                    deselect_all = col_none.button("❌ 全部取消")
                    
                    with st.form("playlist_form"):
                        selected_items = []
                        st.write("---")
                        
                        for idx, entry in enumerate(entries, start=1):
                            item_title = entry.get('title', f'項目 {idx}')
                            item_id = entry.get('id') or entry.get('url')
                            if item_id and not item_id.startswith("http"):
                                item_url = f"https://www.youtube.com/watch?v={item_id}"
                            elif item_id and item_id.startswith("http"):
                                item_url = item_id
                            else:
                                item_url = target_url

                            default_val = True
                            if select_all:
                                default_val = True
                            elif deselect_all:
                                default_val = False
                                
                            is_checked = st.checkbox(f"{idx}. {item_title}", value=default_val, key=f"item_{idx}")
                            if is_checked:
                                selected_items.append({"title": item_title, "url": item_url})
                                
                        submit_btn = st.form_submit_button("📦 確認勾選並準備下載通道")
                        
                    if submit_btn:
                        if selected_items:
                            st.session_state['items_to_download'] = selected_items
                        else:
                            st.warning("⚠️ 請至少勾選一個項目！")
                else:
                    st.warning("⚠️ 此連結似乎不是播放清單，請切換至「單一影片/音訊」模式。")
        except Exception as e:
            st.error(f"❌ 解析失敗：{e}")

    # 顯示穩定線上記錄下載按鈕
    if 'items_to_download' in st.session_state:
        selected_items = st.session_state['items_to_download']
        st.write("---")
        st.subheader("📥 點擊下方按鈕即可開始儲存：")
        
        is_audio = "音訊" in mode
        for idx, item in enumerate(selected_items, start=1):
            st.write(f"**#{idx} {item['title']}**")
            
            clean_url = item['url']
            
            # 使用 SSYoutube (可自動填帶網址且無 DNS 封鎖)
            ss_url = clean_url.replace("https://www.youtube.com/", "https://www.ssyoutube.com/")
            
            # 取得多通道按鈕
            col1, col2 = st.columns(2)
            with col1:
                st.link_button(f"💾 極速下載 #{idx}", ss_url, type="primary")
            with col2:
                # Dirpy 備援 (可直接輸出 MP3)
                dirpy_url = f"https://dirpy.com/from/{clean_url}"
                st.link_button(f"🎵 轉音訊(MP3) #{idx}", dirpy_url)
            st.write("---")

# --- 模式 B：單一媒體模式 ---
else:
    if st.button("🚀 開始下載"):
        if url:
            st.info("⌛ 正在建立專屬下載通道，請稍候...")
            target_url = url.strip()
            
            ss_url = target_url.replace("https://www.youtube.com/", "https://www.ssyoutube.com/").replace("https://youtu.be/", "https://www.ssyoutube.com/watch?v=")
            dirpy_url = f"https://dirpy.com/from/{target_url}"
            
            st.success("✅ 解析成功！請選擇適合的通道進行下載：")
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("💾 點我極速下載影片/音訊", ss_url, type="primary")
            with col2:
                st.link_button("🎵 點我進階轉檔 MP3", dirpy_url)
        else:
            st.warning("⚠️ 請先貼上有效的網址！")
