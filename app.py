import streamlit as st
import requests

# ==================== 頁面設定 ====================
st.set_page_config(
    page_title="波貓下載器 (直連下載版)", 
    page_icon="🐾", 
    layout="centered"
)

# ==================== 主頁面標題與說明 ====================
st.title("🐾 波貓下載器 (直連下載版)")
st.write("選擇對應平台與格式，貼上網址即可快速解析下載！")

# ==================== 表單輸入區 ====================
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
    placeholder="https://youtu.be/Ntr0ZnRr7Qo?si=0z4EiiEVWk7X8Eik"
)

# ==================== 下載解析核心邏輯 ====================
if st.button("🚀 開始下載", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("⚠️ 請先貼上有效的影片或音樂網址！")
    else:
        # 顯示狀態提示框
        status_box = st.info("⌛ 正在建立專屬下載通道，請稍候...")
        
        is_audio = "MP3" in format_choice
        
        # 使用直連 API 進行網址解析
        api_endpoint = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url.strip(),
            "downloadMode": "audio" if is_audio else "auto",
            "audioFormat": "mp3" if is_audio else "best",
            "youtubeVideoCodec": "h264"
        }

        try:
            # 發送請求至解析伺服器
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=20)
            data = response.json()
            
            # 清除載入中提示
            status_box.empty()
            
            # 判斷 API 回傳狀態
            if response.status_code == 200 and data.get("status") in ["tunnel", "redirect", "picker"]:
                download_link = data.get("url")
                
                st.success("✅ 解析成功！請選擇適合的通道下載：")
                
                # 建立醒目的直連下載按鈕
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
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        ">
                            💾 點我開始下載 ({'MP3 音訊檔' if is_audio else 'MP4 影片檔'})
                        </div>
                    </a>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                error_detail = data.get("text", "伺服器無回應，請確認網址或稍後再試！")
                st.error(f"❌ 解析失敗：{error_detail}")
                
        except requests.exceptions.Timeout:
            status_box.empty()
            st.error("❌ 連線逾時，伺服器處理時間過長，請再試一次。")
        except Exception as e:
            status_box.empty()
            st.error(f"❌ 發生未知錯誤：{e}")
            st.info("💡 提示：如果連續失敗，可能是該影片受到版權保護限制。")
