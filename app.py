import streamlit as st
import google.generativeai as genai
import json
import re
import base64
from PIL import Image

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="AiLove Generator - Pro",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. INJEKSI BACKGROUND & CSS KUSTOM
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
    }}
    
    /* Box Styling */
    div[data-testid="column"] {{
        background: rgba(20, 20, 35, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
    }}
    
    h1, h2, h3, h4 {{ color: #00FFFF !important; text-align: center; }}
    
    /* Input Styling */
    .stTextArea>div>div>textarea, .stTextInput>div>div>input {{ 
        background-color: #F0F8FF !important; 
        color: #000000 !important; 
        border: 2px solid #00FFFF !important; 
        font-weight: bold !important;
    }}
    
    div[data-testid="stForm"] {{ border: none !important; background: transparent !important; padding: 0 !important; }}

    /* Button Styling */
    .stButton>button {{ 
        background: linear-gradient(90deg, #4B0082 0%, #00FFFF 100%) !important; 
        color: white !important; 
        font-weight: bold; 
        width: 100%; 
        padding: 15px;
        border-radius: 10px;
        border: none;
    }}
    
    div[data-testid="stCodeBlock"] {{ background-color: rgba(10, 10, 25, 0.9) !important; border: 1px solid #00FFFF; }}
    
    /* ANIMASI RODA GIGI BERPUTAR */
    @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
    
    .gear-standby {{
        font-size: 80px;
        text-align: center;
        filter: grayscale(100%) brightness(50%);
        opacity: 0.5;
        display: inline-block;
    }}
    
    .gear-spinning {{
        font-size: 100px;
        text-align: center;
        display: inline-block;
        animation: spin 2s linear infinite;
        text-shadow: 0 0 30px #00FFFF, 0 0 60px #8A2BE2;
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
# 4. TATA LETAK INPUT
# ==========================================
st.markdown("<h1>⚙️ AiLove Generator Pro</h1>", unsafe_allow_html=True)

if "saved_api_key" not in st.session_state:
    st.session_state.saved_api_key = ""

api_input = st.text_input("🔑 API Key Token (Gunakan fitur 'Save Password' di browser)", type="password", value=st.session_state.saved_api_key)
if api_input:
    st.session_state.saved_api_key = api_input

with st.form("main_input_form"):
    col_in_left, col_in_right = st.columns(2, gap="large")
    
    with col_in_left:
        st.markdown("#### JUMLAH FRAME")
        num_frames = st.slider("Target Frames", min_value=2, max_value=10, value=5, label_visibility="collapsed")
        
        st.markdown("#### MASUKAN IDE")
        ide_teks = st.text_area("Contoh: Dimulai dari lahan kosong menjadi rumah mewah", height=120, label_visibility="collapsed")
        
        st.markdown("#### KARAKTER LOCK (Opsional)")
        karakter = st.text_input("Contoh: Pria berjaket kuning dan topi helm proyek", label_visibility="collapsed")

    with col_in_right:
        st.markdown("#### ASPEK RASIO")
        rasio = st.selectbox("Pilih Rasio", ["16:9", "9:16", "4:3", "1:1"], label_visibility="collapsed")
        
        st.markdown("#### VISUAL OVERRIDE (Preview)")
        foto_akhir = st.file_uploader("Unggah referensi hasil akhir", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
        if foto_akhir:
            st.image(foto_akhir, caption="Preview Gambar Referensi", use_column_width=True)

    submit_btn = st.form_submit_button("GENERATE PROMPTS 🚀")

# ==========================================
# 5. AREA MONITOR & LOGIKA GENERASI
# ==========================================
# Membuat penampung untuk animasi roda gigi di tengah layar (di bawah tombol)
monitor_space = st.empty()
monitor_space.markdown("""
    <div style='text-align: center; margin-top: 30px; margin-bottom: 30px;'>
        <div class='gear-standby'>⚙️</div>
        <div class='status-text' style='color: gray;'>SYSTEM STANDBY...</div>
    </div>
""", unsafe_allow_html=True)

if submit_btn:
    if not st.session_state.saved_api_key:
        monitor_space.error("SYSTEM ERROR: API Key belum dimasukkan!")
    elif not ide_teks and not foto_akhir:
        monitor_space.error("SYSTEM ERROR: Masukan Ide atau Gambar tidak boleh kosong!")
    else:
        # MENGAKTIFKAN ANIMASI RODA GIGI BERPUTAR SAAT LOADING
        monitor_space.markdown("""
            <div style='text-align: center; margin-top: 30px; margin-bottom: 30px;'>
                <div class='gear-spinning'>⚙️</div>
                <div class='status-text'>PROCESSING NEURAL NETWORK...</div>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            genai.configure(api_key=st.session_state.saved_api_key)
            
            char_instruction = ""
            if karakter:
                char_instruction = f"CHARACTER LOCK AKTIF: WAJIB sertakan deskripsi visual karakter ini di setiap frame dan transisi video: '{karakter}'. Karakter ini harus terlihat sedang melakukan aksi pembangunan."
            
            system_instruction = f"""
            Kamu adalah sutradara AI logis. Pecah proses pembangunan menjadi {num_frames} frame (0% hingga 100%).
            {char_instruction}

            ATURAN:
            1. 'prompt_gambar': Gaya Midjourney (--ar {rasio}). Kamera statis dan lingkungan identik.
            2. 'prompt_video': Gunakan template ini persis:
            Create an ultra-realistic cinematic construction timelapse showing the specific construction stage of a [JENIS BANGUNAN].
            Construction stage currently in progress: [JELASKAN TAHAPAN].
            Workers: {f'[CHARACTER LOCK: {karakter}]' if karakter else '[JUMLAH pekerja]'} performing the task.
            Materials: [MATERIAL]. Equipment: [PERALATAN].
            Camera: fixed locked camera interpolating from start to end frame to maintain strict structural integrity.
            Environment: realistic weather changes.
            Audio: high-quality ASMR construction sounds only: [SUARA ASMR SPESIFIK TAHAP INI].
            No music. No narration. No text. Photorealistic, 8K HDR.

            BALAS HANYA DENGAN JSON:
            {{
              "frames": [
                {{"frame": 1, "prompt_gambar": "prompt..."}}
              ],
              "transitions": [
                {{"dari_frame": 1, "ke_frame": 2, "prompt_video": "prompt template lengkap..."}}
              ]
            }}
            """
            
            input_data = [system_instruction]
            if ide_teks: input_data.append(f"Konsep: {ide_teks}")
            if foto_akhir:
                input_data.append("Gunakan gambar referensi ini untuk target wujud Frame 100%.")
                input_data.append(Image.open(foto_akhir))
            
            response_text = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    try:
                        model = genai.GenerativeModel(m.name)
                        response = model.generate_content(input_data, generation_config=genai.types.GenerationConfig(temperature=0.2))
                        response_text = response.text
                        break 
                    except Exception:
                        continue
            
            if response_text:
                data = extract_json(response_text)
                
                # MENGHAPUS RODA GIGI BERPUTAR SETELAH SELESAI
                monitor_space.empty()
                
                # TAMPILAN OUTPUT
                col_out_left, col_out_right = st.columns(2, gap="large")
                
                with col_out_left:
                    st.markdown("### PROMPT IMAGE")
                    for f in data.get('frames', []):
                        st.markdown(f"**Frame {f['frame']}**")
                        st.code(f['prompt_gambar'], language="text")
                
                with col_out_right:
                    st.markdown("### PROMPT VIDEO")
                    for t in data.get('transitions', []):
                        st.markdown(f"**Transisi {t['dari_frame']} ➔ {t['ke_frame']}**")
                        st.code(t['prompt_video'], language="text")
                        
            else:
                monitor_space.error("Gagal terhubung ke model AI. Coba lagi.")
                
        except Exception as e:
            monitor_space.error(f"Error: Pastikan API Key valid. Detail: {e}")
