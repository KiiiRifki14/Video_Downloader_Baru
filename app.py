import streamlit as st
import backend
import os
import shutil

# --- KONFIGURASI ---
st.set_page_config(page_title="Ki.Downloader", page_icon="⚡", layout="wide")

# --- CSS (TAMPILAN GALERI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #050505; font-family: 'Inter', sans-serif; }
    header, footer, #MainMenu {visibility: hidden;}

    .block-container { max-width: 600px; padding-top: 2rem; padding-bottom: 5rem; }

    /* HEADER */
    .logo-text { font-size: 20px; font-weight: 800; color: white; }
    .logo-text span { color: #4c4cff; }
    .private-badge { background: #111; color: #666; padding: 4px 10px; border-radius: 20px; font-size: 10px; border: 1px solid #222; }

    /* JUDUL */
    .hero-title { text-align: center; font-size: 32px; font-weight: 800; color: white; margin-top: 40px; }
    .hero-title span { color: #4c4cff; }
    .hero-desc { text-align: center; color: #666; font-size: 13px; margin-bottom: 40px; }

    /* INPUT */
    .stTextInput > div > div > input {
        background-color: #121212; color: white; border: 2px solid #222;
        border-radius: 25px; padding: 30px 20px; font-size: 18px; text-align: center;
    }
    .stTextInput > div > div > input:focus { border-color: #4c4cff; box-shadow: 0 0 20px rgba(76, 76, 255, 0.4); }

    /* TOMBOL CEK */
    div[data-testid="stButton"] button {
        border-radius: 50px; font-weight: 800; border: none; transition: 0.3s;
    }
    
    /* ITEM GALERI (CARD) */
    .gallery-card {
        background-color: #111; border: 1px solid #222; border-radius: 15px;
        padding: 15px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([1, 1])
with c1: st.markdown('<div class="logo-text">Ki<span>.downloader</span></div>', unsafe_allow_html=True)
with c2: st.markdown('<div style="text-align:right"><span class="private-badge">🔒 Personal Only</span></div>', unsafe_allow_html=True)

# --- HERO ---
st.markdown("""
    <div class="hero-title">Video <span>Downloader</span></div>
    <div class="hero-desc">TikTok • Instagram • YouTube (Mode Galeri)</div>
""", unsafe_allow_html=True)

# --- LOGIKA UTAMA ---
if 'video_info' not in st.session_state: st.session_state.video_info = None
if 'file_list' not in st.session_state: st.session_state.file_list = [] # List untuk nampung banyak file

# INPUT
url_input = st.text_input("URL", placeholder="Paste Link Video Disini...", label_visibility="collapsed")
st.write("") 

# TOMBOL CEK
col_left, col_center, col_right = st.columns([0.2, 2, 0.2])
with col_center:
    cek_clicked = st.button("🔍 CEK POSTINGAN", use_container_width=True, type="primary")

if cek_clicked:
    if url_input:
        st.session_state.file_list = [] # Reset list lama
        with st.spinner("Menganalisa tautan..."):
            info = backend.get_video_info(url_input)
            if info:
                st.session_state.video_info = info
                st.session_state.current_url = url_input
            else:
                st.error("❌ Link tidak valid!")

# --- AREA HASIL ---
if st.session_state.video_info:
    info = st.session_state.video_info
    
    st.markdown("---")
    st.markdown(f"**Judul:** {info.get('title', 'Instagram Post')}")
    
    # TOMBOL PROSES (Untuk Mengambil Semua File ke Server Dulu)
    if not st.session_state.file_list:
        if st.button("⚡ AMBIL SEMUA MEDIA", use_container_width=True):
            with st.spinner("Sedang mengambil semua slide..."):
                files = backend.download_video(st.session_state.current_url)
                if files:
                    st.session_state.file_list = files # Simpan daftar file
                    st.rerun() # Refresh halaman biar galeri muncul
                else:
                    st.error("Gagal mengambil media.")

    # --- MODE GALERI (LOOPING FILE) ---
    if st.session_state.file_list:
        st.success(f"Ditemukan {len(st.session_state.file_list)} media!")
        
        # Looping setiap file yang ditemukan
        for i, file_path in enumerate(st.session_state.file_list):
            
            # Buat Container Kartu
            with st.container():
                st.markdown(f'<div class="gallery-card">', unsafe_allow_html=True)
                
                # Nama file bersih
                file_name = os.path.basename(file_path)
                
                # Tampilkan Preview
                if file_name.endswith(('.jpg', '.png', '.jpeg')):
                    st.image(file_path, use_container_width=True)
                    label_dl = f"⬇️ Download Foto #{i+1}"
                    mime_dl = "image/jpeg"
                elif file_name.endswith(('.mp4', '.webm')):
                    st.video(file_path)
                    label_dl = f"⬇️ Download Video #{i+1}"
                    mime_dl = "video/mp4"
                
                # Baca file untuk tombol download
                with open(file_path, "rb") as f:
                    btn = st.download_button(
                        label=label_dl,
                        data=f,
                        file_name=file_name,
                        mime=mime_dl,
                        use_container_width=True,
                        key=f"dl_btn_{i}" # Key unik biar gak error
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tombol Reset
        if st.button("🔄 Reset / Download Lain"):
            # Bersihkan file sampah
            try: 
                folder_path = os.path.dirname(st.session_state.file_list[0])
                shutil.rmtree(folder_path)
            except: pass
            
            # Reset session
            st.session_state.file_list = []
            st.session_state.video_info = None
            st.rerun()

# Footer
st.markdown("<div style='text-align:center; margin-top:50px; color:#333; font-size:12px;'>Ki.Downloader © 2026</div>", unsafe_allow_html=True)