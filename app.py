import streamlit as st
import google.generativeai as genai
import json
import re
import base64
import os
from PIL import Image

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="AiLove Generator - Beta",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. INJEKSI BACKGROUND, LOGO & CSS KUSTOM
# ==========================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

bg_file = "AI_Timelapse_app_background_design_202608031806.jpeg"
bg_base64 = get_base64_of_bin_file(bg_file)

if bg_base64:
    bg_css = f"background-image: url('data:image/jpeg;base64,{bg_base64}');"
else:
    bg_css = "background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);"

logo_file = "Logo App.png"
logo_base64 = get_base64_of_bin_file(logo_file)

custom_css = f"""
<style>
    [data-testid="collapsedControl"] {{ display: none; }}
    header {{ display: none !important; }}
    
    .stApp {{
        {bg_css}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #E0E0FF;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    div[data-testid="column"] {{
        background: rgba(20, 20, 35, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 150, 255, 0.3);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }}
    
    h1, h2, h3 {{ color: #00FFFF !important; text-shadow: 0 0 10px rgba(0, 255, 255, 0.5); }}
    p, label {{ color: #B0C4DE !important; font-weight: bold; }}
    
    .stTextArea>div>div>textarea {{ 
        background-color: #F0F8FF !important; 
        color: #000000 !important; 
        border: 2px solid #00FFFF !important; 
        font-weight: bold !important;
        font-size: 16px !important;
    }}
    
    .stTextInput>div>div>input {{ 
        background-color: rgba(0,0,0,0.5) !important; 
        color: #00FFFF !important; 
        border: 1px solid #4B0082 !important; 
    }}
    
    div[data-testid="stForm"] {{
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }}

    .stButton>button {{ 
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%) !important; 
        color: white !important; 
        border: 1px solid #00FFFF; 
        border-radius: 10px; 
        font-weight: bold; 
        width: 100%; 
        padding: 15px;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.6);
        transition: 0.3s;
        margin-top: 15px;
    }}
    .stButton>button:hover {{ 
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.8); 
        border: 1px solid #FF00FF;
    }}
    
    div[data-testid="stCodeBlock"] {{ 
        background-color: rgba(10, 10, 25, 0.9) !important; 
        border: 1px solid #00FFFF; 
        border-radius: 8px; 
    }}
    
    .bulb-dim {{
        font-size: 80px;
        text-align: center;
        filter: grayscale(100%) brightness(50%);
        opacity: 0.5;
        transition: 0.5s;
    }}
    .bulb-glow {{
        font-size: 100px;
        text-align: center;
        text-shadow: 0 0 30px #00FFFF, 0 0 60px #8A2BE2;
        animation: pulse 1s infinite alternate;
    }}
    @keyframes pulse {{
        0% {{ opacity: 0.8; transform: scale(0.95); text-shadow: 0 0 20px #00FFFF; }}
        100% {{ opacity: 1; transform: scale(1.05); text-shadow: 0 0 50px #00FFFF, 0 0 80px #FF00FF; }}
    }}
    .status-text {{ text-align: center; color: #00FFFF; font-family: monospace; font-size: 18px; margin-top: 10px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI EKSTRAK JSON
# ==========================================
def extract_json(text):
    match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
    if match:
        text = match.group(1)
    text = text[text.find('{'):text.rfind('}')+1]
    return json.loads(text)

# ==========================================
# 4. TATA LETAK UTAMA (HEADER & GRID)
# ==========================================
if logo_base64:
    logo_html = f"<img src='data:image/png;base64,{logo_base64}' width='120' style='margin-bottom: 10px; filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.3));'>"
else:
    logo_html = "<h1 style='font-size: 60px;'>⚙️</h1>"

st.markdown(f"""
    <div style='text-align: center; margin-bottom: 30px;'>
        {logo_html}
        <h1 style='margin-bottom: 0px;'>AiLove Generator</h1>
        <p style='color: #00FFFF; font-family: monospace; font-size: 14px; letter-spacing: 3px; margin-top: 5px;'>VERSION 1.3 BETA - STRICT TIMELAPSE VEO 3.1</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1.2, 2.5, 1.2], gap="large")

with col_left:
    st.markdown("### 🎛️ DATA INPUT")
    api_key = st.text_input("🔑 API Key Token", type="password")
    ide_teks = st.text_area("📝 Parameter Proyek", height=150, placeholder="Masukkan ide atau konsep bangunan... (Teks hitam)")

with col_right:
    st.markdown("### ⚙️ SYSTEM CONTROL")
    with st.form("kontrol_form"):
        rasio = st.selectbox("📺 Aspek Rasio", ["16:9", "9:16", "4:3", "1:1"])
        num_frames = st.slider("Target Frames (0-100%)", min_value=2, max_value=10, value=5)
        foto_akhir = st.file_uploader("🖼️ Visual Override (Opsional)", type=['jpg', 'jpeg', 'png'])
        generate_btn = st.form_submit_button("INITIATE GENERATOR 🚀")

with col_center:
    monitor_space = st.empty()
    monitor_space.markdown("""
        <div style='margin-top: 50px;'>
            <div class='bulb-dim'>💡</div>
            <div class='status-text' style='color: gray;'>SYSTEM STANDBY...</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. LOGIKA AI & GENERASI (KUNCI KONSISTENSI)
# ==========================================
if generate_btn:
    if not api_key:
        with col_center:
            st.error("SYSTEM ERROR: API Key Missing!")
    elif not ide_teks and not foto_akhir:
        with col_center:
            st.error("SYSTEM ERROR: Input Data Empty!")
    else:
        monitor_space.markdown("""
            <div style='margin-top: 50px;'>
                <div class='bulb-glow'>💡</div>
                <div class='status-text'>PROCESSING STRICT TIMELAPSE NEURAL NETWORK...</div>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            genai.configure(api_key=api_key)
            
            # PERBAIKAN: Instruksi sangat ketat agar video stop motion tidak melenceng strukturnya
            system_instruction = f"""
            Kamu adalah sutradara AI yang sangat logis. Pecah proses pembangunan menjadi {num_frames} frame (0% hingga 100%).

            ATURAN KONSISTENSI MUTLAK:
            1. 'prompt_gambar': Gunakan gaya bahasa untuk Midjourney (--ar {rasio}). SATU sudut kamera statis, latar belakang lingkungan identik di setiap frame.
            2. 'prompt_video' (SANGAT PENTING): AI Video (Veo 3.1) sering merusak struktur. Untuk mencegahnya, kamu WAJIB memulai setiap prompt video dengan kalimat bahasa Inggris ini secara persis: "Fixed locked camera, time-lapse stop-motion style, perfectly interpolating from the starting frame to the ending frame while maintaining exact structural integrity, lighting, and background."
            3. Setelah kalimat wajib tersebut, deskripsikan BAGAIMANA material bertambah/muncul secara ajaib ke posisinya. (contoh: "...Wooden planks rapidly snapping into place building the walls.")
            4. Akhiri prompt video dengan instruksi ASMR. (contoh: "Audio: ASMR clear sounds of drilling, hammering wood, and ambient nature.")
            
            BALAS HANYA DENGAN JSON:
            {{
              "frames": [
                {{"frame": 1, "persen": "0%", "prompt_gambar": "prompt gambar statis untuk Midjourney..."}}
              ],
              "transitions": [
                {{"dari_frame": 1, "ke_frame": 2, "prompt_video": "Fixed locked camera, time-lapse stop-motion style, perfectly interpolating from the starting frame to the ending frame while maintaining exact structural integrity, lighting, and background. [deskripsikan material yang muncul/tersusun]. Audio: ASMR [deskripsi suara keras konstruksi & alam]."}}
              ]
            }}
            """
            
            input_data = [system_instruction]
            if ide_teks: input_data.append(f"Konsep: {ide_teks}")
            if foto_akhir:
                input_data.append("Gunakan referensi gambar ini untuk wujud final Frame 100%.")
                input_data.append(Image.open(foto_akhir))
            
            response_text = None
            
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    try:
                        model = genai.GenerativeModel(m.name)
                        response = model.generate_content(
                            input_data,
                            generation_config=genai.types.GenerationConfig(temperature=0.2)
                        )
                        response_text = response.text
                        break 
                    except Exception:
                        continue
            
            if response_text:
                data = extract_json(response_text)
                
                monitor_space.empty()
                
                with col_center.container():
                    st.markdown("### 📸 IMAGE KEYFRAMES (MIDJOURNEY)")
                    for f in data.get('frames', []):
                        st.markdown(f"<span style='color:#00FFFF; font-size: 18px; font-weight: bold;'>► Frame {f['frame']} [{f['persen']}]</span>", unsafe_allow_html=True)
                        st.markdown("<small style='color:lightgray;'>Salin Prompt Gambar:</small>", unsafe_allow_html=True)
                        st.code(f['prompt_gambar'], language="text")
                        st.markdown("<hr style='border-color: #4B0082; margin: 10px 0;'>", unsafe_allow_html=True)
                    
                    st.markdown("<br>### 🎞️ STRICT TIMELAPSE VIDEO (VEO 3.1)", unsafe_allow_html=True)
                    for t in data.get('transitions', []):
                        st.markdown(f"<span style='color:#FF00FF; font-size: 16px; font-weight: bold;'>► Transisi {t['dari_frame']} ➔ {t['ke_frame']}</span>", unsafe_allow_html=True)
                        st.markdown("<small style='color:lightgreen;'>Salin Prompt Kunci Kamera & Audio (Veo 3.1):</small>", unsafe_allow_html=True)
                        st.code(t['prompt_video'], language="text")
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                monitor_space.error("SERVER DISCONNECTED: Tidak ada model AI yang cocok dengan input ini.")
                
        except Exception as e:
            monitor_space.error(f"FATAL ERROR: Pastikan API Key valid atau coba beberapa saat lagi. Detail: {e}")
