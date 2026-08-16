import streamlit as st
import yt_dlp
import os
import tempfile
import requests

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (網頁跨平台版)")
st.write("輸入網址，選擇平台與格式即可快速下載！")

# 平台選單
folders = {
    "1": "YouTube (含播放清單)",
    "2": "Douyin (抖音)",
    "3": "Instagram",
    "4": "Podcasts",
    "5": "Xiaohongshu (小紅書)"
}

selected_platform = st.selectbox("1. 選擇平台：", list(folders.values()))
mode = st.radio("2. 選擇下載格式：", ["影片 (MP4)", "音訊 (MP3)"])

url = st.text_input("3. 請貼上影片/播放清單/音訊網址：", placeholder="https://...")

# 解析按鈕
if st.button("🔍 解析網址 / 播放清單"):
    if url:
        st.session_state['parsed_url'] = url.strip()
        st.session_state['parse_trigger'] = True
    else:
        st.warning("⚠️ 請先貼上有效的網址！")

# 執行解析與勾選邏輯
if st.session_state.get('parse_trigger') and st.session_state.get('parsed_url'):
    target_url = st.session_state['parsed_url']
    st.info("⌛ 正在解析媒體通道與播放清單資訊，請稍候...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'http_headers': headers,
        'extractor_args': {
            'youtube': {'player_client': ['android', 'ios', 'mweb']}
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            
            # 如果是播放清單模式
            if 'entries' in info:
                entries = [e for e in info['entries'] if e]
                st.success(f"📋 偵測到播放清單：「{info.get('title', 'YouTube 播放清單')}」，共 {len(entries)} 項。")
                
                # 全選/全不選 控制
                col_all, col_none = st.columns([1, 1])
                select_all = col_all.button("✅ 全部勾選")
                deselect_all = col_none.button("❌ 全部取消")
                
                # 建立表單讓使用者勾選
                with st.form("playlist_form"):
                    selected_items = []
                    st.write("---")
                    
                    for idx, entry in enumerate(entries, start=1):
                        item_title = entry.get('title', f'項目 {idx}')
                        item_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        
                        # 控制勾選狀態
                        default_val = True
                        if select_all:
                            default_val = True
                        elif deselect_all:
                            default_val = False
                            
                        is_checked = st.checkbox(f"{idx}. {item_title}", value=default_val, key=f"item_{idx}")
                        if is_checked:
                            selected_items.append({"title": item_title, "url": item_url})
                            
                    submit_btn = st.form_submit_button("📦 產生所選項目的下載連結")
                    
                if submit_btn:
                    if selected_items:
                        st.success(f"🎉 已選擇 {len(selected_items)} 個項目，請點擊下方按鈕進行下載：")
                        for idx, item in enumerate(selected_items, start=1):
                            st.link_button(f"📥 下載 #{idx}: {item['title']}", item['url'])
                    else:
                        st.warning("⚠️ 請至少勾選一個項目！")

            # 如果是單一影片模式
            else:
                st.success(f"✅ 解析成功！標題：{info.get('title', '媒體檔案')}")
                
                # 單曲直接下載/轉存
                with tempfile.TemporaryDirectory() as temp_dir:
                    save_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
                    dl_opts = {
                        'outtmpl': save_path,
                        'quiet': True,
                        'format': 'ba/bestaudio/best' if "音訊" in mode else 'b[ext=mp4]/best[ext=mp4]/best'
                    }
                    with yt_dlp.YoutubeDL(dl_opts) as dl_ydl:
                        dl_ydl.download([target_url])
                        filename = dl_ydl.prepare_filename(info)
                        
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="💾 點我儲存檔案到裝置",
                                data=file,
                                file_name=os.path.basename(filename),
                                mime="audio/mpeg" if "音訊" in mode else "video/mp4"
                            )

    except Exception as e:
        # 備援 API 模式
        try:
            res = requests.post(
                "https://api.cobalt.tools/",
                json={"url": target_url, "downloadMode": "audio" if "音訊" in mode else "auto"},
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=12
            )
            data = res.json()
            if data.get("status") in ["stream", "redirect"]:
                st.success("✅ 解析成功！")
                st.link_button("💾 點我開啟/下載媒體檔案", data.get("url"))
            else:
                st.error(f"❌ 解析失敗：{e}")
        except Exception:
            st.error("❌ 無法解析此連結，請確認網址是否正確。")
