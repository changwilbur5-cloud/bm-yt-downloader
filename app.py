import streamlit as st
import yt_dlp
import requests
import json

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (防封鎖穩定版)")
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

# 透過 Piped/Invidious 備援鏡像通道解析直連下載檔 (防 403 封鎖)
def get_bypass_download_link(video_url, is_audio_mode):
    # 提取 Video ID
    video_id = None
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]
    
    if not video_id:
        return None

    # 使用 Piped 免費鏡像 API 取得直連網址
    piped_instances = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.privacydev.net",
        "https://pipedapi.tokhmi.xyz"
    ]
    
    for api_base in piped_instances:
        try:
            res = requests.get(f"{api_base}/streams/{video_id}", timeout=6)
            if res.status_code == 200:
                data = res.json()
                if is_audio_mode:
                    # 取得音訊串流
                    audio_streams = data.get("audioStreams", [])
                    if audio_streams:
                        return audio_streams[0].get("url")
                else:
                    # 取得含聲音影片串流
                    video_streams = data.get("videoStreams", [])
                    for stream in video_streams:
                        if stream.get("videoOnly") == False:
                            return stream.get("url")
                    if video_streams:
                        return video_streams[0].get("url")
        except Exception:
            continue
    return None

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
                            item_id = entry.get('id')
                            item_url = f"https://www.youtube.com/watch?v={item_id}" if item_id else entry.get('url')
                            
                            default_val = True
                            if select_all:
                                default_val = True
                            elif deselect_all:
                                default_val = False
                                
                            is_checked = st.checkbox(f"{idx}. {item_title}", value=default_val, key=f"item_{idx}")
                            if is_checked:
                                selected_items.append({"title": item_title, "url": item_url})
                                
                        submit_btn = st.form_submit_button("📦 確認勾選並取得下載網址")
                        
                    if submit_btn:
                        if selected_items:
                            st.session_state['items_to_download'] = selected_items
                        else:
                            st.warning("⚠️ 請至少勾選一個項目！")
                else:
                    st.warning("⚠️ 此連結似乎不是播放清單，請切換至「單一影片/音訊」模式。")
        except Exception as e:
            st.error(f"❌ 解析失敗：{e}")

    # 顯示直連下載按鈕 (避開 403)
    if 'items_to_download' in st.session_state:
        selected_items = st.session_state['items_to_download']
        st.write("---")
        st.subheader("📥 點擊下方按鈕即可快速儲存檔案：")
        
        is_audio = "音訊" in mode
        for idx, item in enumerate(selected_items, start=1):
            st.write(f"**#{idx} {item['title']}**")
            
            dl_link = get_bypass_download_link(item['url'], is_audio)
            
            if dl_link:
                st.link_button(f"💾 點我下載 #{idx} ({'MP3' if is_audio else 'MP4'})", dl_link)
            else:
                st.error(f"❌ #{idx} 媒體通道目前忙碌中，請稍後重試。")
            st.write("---")

# --- 模式 B：單一媒體模式 ---
else:
    if st.button("🚀 開始下載"):
        if url:
            st.info("⌛ 正在穿透防護通道，請稍候...")
            target_url = url.strip()
            is_audio = "音訊" in mode
            
            dl_link = get_bypass_download_link(target_url, is_audio)
            
            if dl_link:
                st.success("✅ 解析成功！請點擊下方按鈕開始下載：")
                st.link_button(f"💾 點我開啟/下載 ({'MP3' if is_audio else 'MP4'})", dl_link)
            else:
                st.error("❌ 無法取得媒體串流，可能是 YouTube 防爬蟲限制或網址不正確。")
        else:
            st.warning("⚠️ 請先貼上有效的網址！")
