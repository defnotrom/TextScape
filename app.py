import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Game Master", page_icon="⚔️", layout="centered")

st.title("⚔️ AI Game Master RPG")
st.caption("Petualangan interaktif berbasis teks powered by Gemini")

# Sidebar untuk konfigurasi
with st.sidebar:
    st.header("Pengaturan Game")
    api_key = st.text_input("Gemini API Key", type="password", help="Dapatkan API Key gratis di Google AI Studio")
    genre = st.selectbox(
        "Pilih Tema Petualangan:",
        ["Cyberpunk Detective", "Dark Fantasy", "Sci-Fi Space Survival", "Post-Apocalyptic"]
    )
    
    if st.button("Reset Game / Mulai Baru"):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.warning("Masukkan Gemini API Key kamu di sidebar untuk memulai petualangan!", icon="🔑")
    st.stop()

# Konfigurasi Gemini API
genai.configure(api_key=api_key)

SYSTEM_PROMPT = f"""
Kamu adalah seorang Game Master (GM) RPG ahli untuk genre {genre}.
Tugas utama kamu:
1. Buat narasi singkat yang imersif, hidup, dan penuh suasana (maksimal 2-3 paragraf).
2. Setiap kali merespons aksi pemain, perhitungkan konsekuensinya secara realistis.
3. Selalu akhiri respons kamu dengan 3 pilihan aksi bernomor (1, 2, 3), lalu ingatkan pemain bahwa mereka juga boleh mengetik aksi bebas sendiri.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Inisialisasi riwayat pesan
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    
    # Generate cerita pembuka secara otomatis
    with st.spinner("Game Master sedang menyusun dunia..."):
        chat = model.start_chat(history=[])
        opening_response = chat.send_message("Mulai petualangan baru! Buat adegan pembuka yang menarik dan berikan pilihan aksi pertama.")
        st.session_state.messages.append({"role": "assistant", "content": opening_response.text})

# Tampilkan seluruh riwayat chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input dari pemain
if user_input := st.chat_input("Ketik tindakanmu atau pilih nomor aksi..."):
    # Tampilkan input pemain
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Format riwayat percakapan untuk API Gemini
    history_gemini = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history_gemini.append({"role": role, "parts": [m["content"]]})

    # Kirim ke model dan dapatkan balasan GM
    chat = model.start_chat(history=history_gemini)
    with st.chat_message("assistant"):
        with st.spinner("Game Master sedang merespons..."):
            response = chat.send_message(user_input)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
