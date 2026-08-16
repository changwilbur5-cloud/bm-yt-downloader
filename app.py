import streamlit as st
import yt_dlp
import os
import tempfile

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (原生下載版)")
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
        st.info("⌛ 正在讀取播放清單清單，請稍候...")
        
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
                            item_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            
                            default_val = True
                            if select_all:
                                default_val = True
                            elif deselect_all:
                                default_val = False
                                
                            is_checked = st.checkbox(f"{idx}. {item_title}", value=default_val, key=f"item_{idx}")
                            if is_checked:
                                selected_items.append({"title": item_title, "url": item_url})
                                
                        submit_btn = st.form_submit_button("📦 確認勾選並準備下載")
                        
                    if submit_btn:
                        if selected_items:
                            st.session_state['items_to_download'] = selected_items
                        else:
                            st.warning("⚠️ 請至少勾選一個項目！")
                else:
                    st.warning("⚠️ 此連結似乎不是播放清單，請切換至「單一影片/音訊」模式。")
        except Exception as e:
            st.error(f"❌ 解析失敗：{e}")

    # 逐一下載所選項目並提供原生儲存按鈕
    if 'items_to_download' in st.session_state:
        selected_items = st.session_state['items_to_download']
        st.write("---")
        st.subheader("📥 點擊下方按鈕直接下載檔案：")
        
        for idx, item in enumerate(selected_items, start=1):
            st.write(f"**#{idx} {item['title']}**")
            
            # 使用 Streamlit 獨立按鈕即時下載實體檔案
            if st.button(f"⚡ 轉存成 {'MP3' if '音訊' in mode else 'MP4'} (#{idx})", key=f"dl_btn_{idx}"):
                with st.spinner(f"正在轉存 #{idx} 中，請稍候..."):
                    try:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
                            dl_opts = {
                                'outtmpl': save_path,
                                'quiet': True,
                                'format': 'ba/best' if "音訊" in mode else 'b[ext=mp4]/best',
                                'http_headers': {'User-Agent': 'Mozilla/5.0'}
                            }
                            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                                info = ydl.extract_info(item['url'], download=True)
                                filename = ydl.prepare_filename(info)
                                
                                with open(filename, "rb") as file:
                                    st.download_button(
                                        label=f"💾 儲存檔案 #{idx} 到裝置",
                                        data=file.read(),
                                        file_name=os.path.basename(filename),
                                        mime="audio/mpeg" if "音訊" in mode else "video/mp4",
                                        key=f"save_btn_{idx}"
                                    )
                    except Exception as err:
                        st.error(f"❌ 轉存失敗：{err}")

# --- 模式 B：單一媒體模式 ---
else:
    if st.button("🚀 開始下載"):
        if url:
            st.info("⌛ 正在伺服器端抓取並處理檔案，請稍候...")
            target_url = url.strip()
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
                    dl_opts = {
                        'outtmpl': save_path,
                        'quiet': True,
                        'format': 'ba/best' if "音訊" in mode else 'b[ext=mp4]/best',
                        'http_headers': {'User-Agent': 'Mozilla/5.0'}
                    }
                    with yt_dlp.YoutubeDL(dl_opts) as ydl:
                        info = ydl.extract_info(target_url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        st.success(f"✅ 解析成功！標題：{info.get('title', '媒體檔案')}")
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="💾 點我儲存檔案到裝置",
                                data=file.read(),
                                file_name=os.path.basename(filename),
                                mime="audio/mpeg" if "音訊" in mode else "video/mp4"
                            )
            except Exception as e:
                st.error(f"❌ 下載失敗：{e}")
        else:
            st.warning("⚠️ 請先貼上有效的網址！")
