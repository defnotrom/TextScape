import json
import urllib.request
import streamlit as st

st.set_page_config(page_title="TextScape AI RPG", page_icon="🌌", layout="centered")

st.title("🌌 TextScape: All-New RPG")
st.caption("Petualangan Teks Interaktif — Direct REST API Mode")

# Sidebar Pengaturan
with st.sidebar:
    st.header("⚙️ Pengaturan Game")
    api_key = st.text_input("Gemini API Key:", type="password")
    
    st.divider()
    st.header("🎭 Buat Karakter")
    player_name = st.text_input("Nama Karakter:", "Petualang")
    genre = st.selectbox(
        "Pilih Semesta Dunia:",
        [
            "🌌 Cyberpunk 2099 (Neon, Hacker, & Cyborg)",
            "🗡️ Dark Fantasy (Sihir, Monster, & Kerajaan)",
            "🧟 Post-Apocalyptic (Zombie & Survival)",
            "🚀 Galactic Explorer (Luar Angkasa & Alien)"
        ]
    )
    
    st.divider()
    if st.button("🔄 Restart Petualangan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.info("💡 Masukkan Gemini API Key kamu di sidebar untuk mulai bermain!")
    st.stop()

# Fungsi Panggil Gemini REST API Langsung
def call_gemini_api(messages_history, system_prompt, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": messages_history
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as response:
        res_body = json.loads(response.read().decode('utf-8'))
        return res_body['candidates'][0]['content']['parts'][0]['text']

SYSTEM_PROMPT = f"""
Kamu adalah seorang Game Master (GM) RPG yang sangat seru dan interaktif.
Pemain bernama: {player_name}
Genre petualangan: {genre}

Panduan Merespons:
1. Buat narasi pembuka atau lanjutan yang imersif dan penuh suspense (maksimal 2-3 paragraf).
2. Tanggapi setiap aksi pemain dengan efek/konsekuensi yang realistis.
3. Gunakan formatting Markdown (teks tebal untuk aksi penting, cetak miring untuk dialog).
4. SELALU akhiri respons kamu dengan memberikan 3 Opsi Aksi Bernomor (1, 2, 3), lalu ingatkan bahwa pemain bebas mengetikkan tindakan unik mereka sendiri.
"""

# Inisialisasi Riwayat Percakapan
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    with st.spinner("🎲 Game Master sedang merancang duniamu..."):
        try:
            init_history = [{
                "role": "user", 
                "parts": [{"text": f"Mulai petualangan baru di dunia {genre} untuk {player_name}. Buat situasi pembuka yang darurat dan berikan 3 pilihan aksi awal!"}]
            }]
            response_text = call_gemini_api(init_history, SYSTEM_PROMPT, api_key)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Gagal menghubungkan ke Gemini. Cek API Key kamu. Detail: {e}")
            st.stop()

# Tampilkan Riwayat Chat
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "🤠"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input dari Pemain
if user_input := st.chat_input("Ketik Opsi (1/2/3) atau tindakan bebasmu di sini..."):
    st.chat_message("user", avatar="🤠").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Susun riwayat percakapan untuk API
    api_history = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        api_history.append({"role": role, "parts": [{"text": m["content"]}]})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🎲 Game Master sedang merespons..."):
            try:
                response_text = call_gemini_api(api_history, SYSTEM_PROMPT, api_key)
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
