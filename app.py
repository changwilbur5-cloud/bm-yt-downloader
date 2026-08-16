import streamlit as st
import yt_dlp
import os
import tempfile
import requests
import time

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (網頁跨平台版)")
st.write("選擇對應平台與格式，貼上網址即可快速解析下載！")

# 分類平台選項 (區分有無播放清單)
platform_options = [
    "YouTube (單一影片/音訊)",
    "YouTube (播放清單批次下載)",
    "Douyin (抖音 - 單一影片)",
    "Instagram (貼文/Reels/多圖)",
    "Podcasts (單集音訊)",
    "Xiaohongshu (小紅書 - 影片/圖文)"
]

selected_platform = st.selectbox("1. 選擇平台與模式：", platform_options)
mode = st.radio("2. 選擇下載格式：", ["影片 (MP4)", "音訊 (MP3)"])

url = st.text_input("3. 請貼上連結：", placeholder="https://...")

is_playlist_mode = "播放清單" in selected_platform

# 取得 Cobalt API 下載連結
def get_cobalt_download_url(target_url, mode_type):
    cobalt_urls = [
        "https://api.cobalt.tools/",
        "https://co.wuk.sh/api/json"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "url": target_url,
        "downloadMode": "audio" if "音訊" in mode_type else "auto",
        "audioFormat": "mp3"
    }

    for api in cobalt_urls:
        try:
            res = requests.post(api, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                if data.get("url"):
                    return data.get("url")
                elif data.get("status") in ["stream", "redirect"]:
                    return data.get("url")
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
        st.info("⌛ 正在解析播放清單內容，請稍候...")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'extractor_args': {
                'youtube': {'player_client': ['android', 'ios', 'mweb']}
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)
                
                if 'entries' in info:
                    entries = [e for e in info['entries'] if e]
                    st.success(f"📋 偵測到播放清單：「{info.get('title', 'YouTube 播放清單')}」，共 {len(entries)} 項。")
                    
                    col_all, col_none = st.columns([1, 1])
                    select_all = col_all.button("✅ 全部勾選")
                    deselect_all = col_none.button("❌ 全部取消")
                    
                    with st.form("playlist_form"):
                        selected_items = []
                        st.write("---")
                        
                        for idx, entry in enumerate(entries, start=1):
                            item_title = entry.get('title', f'項目 {idx}')
                            item_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            
                            default_val = True
                            if select_all:
                                default_val = True
                            elif deselect_all:
                                default_val = False
                                
                            is_checked = st.checkbox(f"{idx}. {item_title}", value=default_val, key=f"item_{idx}")
                            if is_checked:
                                selected_items.append({"title": item_title, "url": item_url})
                                
                        submit_btn = st.form_submit_button("📦 開始取得所選項目的下載連結")
                        
                    if submit_btn:
                        if selected_items:
                            st.session_state['items_to_download'] = selected_items
                        else:
                            st.warning("⚠️ 請至少勾選一個項目！")
                else:
                    st.warning("⚠️ 此連結似乎不是播放清單，請切換至「單一影片/音訊」模式再試一次。")
        except Exception as e:
            st.error(f"❌ 播放清單解析失敗：{e}")

    # 處理勾選項目的下載連結生成
    if 'items_to_download' in st.session_state:
        selected_items = st.session_state['items_to_download']
        st.success(f"🎉 正在為選取的 {len(selected_items)} 個項目獲取直連檔案：")
        
        progress_bar = st.progress(0)
        
        for idx, item in enumerate(selected_items, start=1):
            st.write(f"**#{idx} {item['title']}**")
            
            # 呼叫多重備援 API 取得直接下載檔
            dl_file_url = get_cobalt_download_url(item['url'], mode)
            
            if dl_file_url:
                st.link_button(f"💾 點我下載 #{idx} ({'MP3' if '音訊' in mode else 'MP4'})", dl_file_url)
            else:
                # 備援第三方快捷下載管道
                cobalt_web = f"https://cobalt.tools/#url={item['url']}"
                st.link_button(f"🔗 前往通道下載 #{idx}", cobalt_web)
                st.caption("（若無直連按鈕，請點上方按鈕一鍵前往下載）")

            st.write("---")
            # 加上防擋緩衝時間 (0.5 秒)
            time.sleep(0.5)
            progress_bar.progress(idx / len(selected_items))

# --- 模式 B：單一媒體模式 (無播放清單) ---
else:
    if st.button("🚀 開始下載"):
        if url:
            st.info("⌛ 正在解析並抓取媒體檔案，請稍候...")
            target_url = url.strip()
            
            dl_file_url = get_cobalt_download_url(target_url, mode)
            if dl_file_url:
                st.success("✅ 解析成功！請點擊下方按鈕下載：")
                st.link_button("💾 點我開啟/下載媒體檔案", dl_file_url)
            else:
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
                        dl_opts = {
                            'outtmpl': save_path,
                            'quiet': True,
                            'format': 'ba/bestaudio/best' if "音訊" in mode else 'b[ext=mp4]/best[ext=mp4]/best'
                        }
                        with yt_dlp.YoutubeDL(dl_opts) as ydl:
                            info = ydl.extract_info(target_url, download=True)
                            filename = ydl.prepare_filename(info)
                            
                            st.success(f"✅ 解析成功！標題：{info.get('title', '媒體檔案')}")
                            with open(filename, "rb") as file:
                                st.download_button(
                                    label="💾 點我儲存檔案到裝置",
                                    data=file,
                                    file_name=os.path.basename(filename),
                                    mime="audio/mpeg" if "音訊" in mode else "video/mp4"
                                )
                except Exception as e:
                    st.error(f"❌ 下載失敗：{e}")
        else:
            st.warning("⚠️ 請先貼上有效的網址！")
