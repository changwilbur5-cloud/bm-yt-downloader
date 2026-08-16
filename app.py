import streamlit as st
import yt_dlp
import re

# 設定網頁標題與圖示
st.set_page_config(page_title="波貓下載器", page_icon="🐾")

st.title("🐾 波貓下載器 (終極穩定版)")
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

# 強效影片 ID 提取器
def extract_video_id(item_data):
    # 1. 優先從 entry 字典直接找 id
    if isinstance(item_data, dict):
        if item_data.get('id'):
            return item_data.get('id')
        if item_data.get('url'):
            item_data = item_data.get('url')
            
    # 2. 從網址字串提取 11 位數 ID
    if isinstance(item_data, str):
        match = re.search(r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})", item_data)
        if match:
            return match.group(1)
            
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
            'extract_flat': True,
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
                            vid = extract_video_id(entry)
                            
                            default_val = True
                            if select_all:
                                default_val = True
                            elif deselect_all:
                                default_val = False
                                
                            is_checked = st.checkbox(f"{idx}. {item_title}", value=default_val, key=f"item_{idx}")
                            if is_checked:
                                selected_items.append({"title": item_title, "id": vid, "raw": entry})
                                
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

    # 顯示穩定雙軌下載按鈕
    if 'items_to_download' in st.session_state:
        selected_items = st.session_state['items_to_download']
        st.write("---")
        st.subheader("📥 點擊下方按鈕即可開始儲存：")
        
        for idx, item in enumerate(selected_items, start=1):
            st.write(f"**#{idx} {item['title']}**")
            
            vid = item.get('id') or extract_video_id(item.get('raw'))
            
            if vid:
                clean_yt_url = f"https://www.youtube.com/watch?v={vid}"
                
                # 免 API 直接帶入網址的極速下載通道
                dl_channel_1 = f"https://cobalt.tools/#url={clean_yt_url}"
                dl_channel_2 = f"https://www.y2mate.com/youtube/{vid}"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button(f"⚡ 高速通道 #{idx}", dl_channel_1, type="primary")
                with col2:
                    st.link_button(f"🛡️ 備援通道 #{idx}", dl_channel_2)
            else:
                st.error(f"❌ #{idx} 項目無法解析 ID")
            st.write("---")

# --- 模式 B：單一媒體模式 ---
else:
    if st.button("🚀 開始下載"):
        if url:
            st.info("⌛ 正在建立專屬下載通道，請稍候...")
            target_url = url.strip()
            vid = extract_video_id(target_url)
            
            if vid:
                clean_yt_url = f"https://www.youtube.com/watch?v={vid}"
                dl_channel_1 = f"https://cobalt.tools/#url={clean_yt_url}"
                dl_channel_2 = f"https://www.y2mate.com/youtube/{vid}"
                
                st.success("✅ 解析成功！請選擇適合的通道進行下載：")
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("⚡ 高速下載通道", dl_channel_1, type="primary")
                with col2:
                    st.link_button("🛡️ 備援下載通道", dl_channel_2)
            else:
                st.link_button("⚡ 點我前往免追蹤線上下載", f"https://cobalt.tools/#url={target_url}", type="primary")
        else:
            st.warning("⚠️ 請先貼上有效的網址！")
