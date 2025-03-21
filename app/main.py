import streamlit as st
import random
import json
import time
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Google Sheets
SHEET_ID = "11coLcirjxLmyLEZFbMfj9R6A2Fz4mMD3182x_XHMr7E"
SERVICE_ACCOUNT_FILE = "data/service_account.json"

# Autentikasi Google Sheets
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Load database
with open("data/database.json", "r", encoding="utf-8") as file:
    data = json.load(file)

def get_random_question(mode):
    """ Mengambil pertanyaan acak sesuai mode permainan """
    if mode == "Hiragana only":
        category = "Hiragana"
    elif mode == "Katakana only":
        category = "Katakana"
    else:
        category = random.choice(["Hiragana", "Katakana"])
    
    question = random.choice(data[category])  
    correct_answer = question["romaji"]

    choices = random.sample([q["romaji"] for cat in data.values() for q in cat], 4)
    
    if correct_answer not in choices:
        choices.append(correct_answer)
    
    random.shuffle(choices)
    
    return question["character"], correct_answer, choices

def save_score(name, score):
    """ Menyimpan skor ke Google Sheets """
    sheet.append_row([name, score, time.strftime("%Y-%m-%d %H:%M:%S")])

def get_leaderboard():
    """ Mengambil leaderboard dari Google Sheets """
    records = sheet.get_all_values()[1:]
    return sorted(records, key=lambda x: int(x[1]), reverse=True)[:10]

# Streamlit UI
st.set_page_config(page_title="Kana Quiz", layout="centered")

st.title("Hiragana & Katakana Quiz")

# Inisialisasi sesi
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "name" not in st.session_state:
    st.session_state.name = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "current_answer" not in st.session_state:
    st.session_state.current_answer = None
if "choices" not in st.session_state:
    st.session_state.choices = []

# Input nama pemain
if not st.session_state.game_started:
    st.session_state.name = st.text_input("Masukkan Nama/Inisial:", "")
    mode = st.radio("Pilih Mode Permainan:", ["Hiragana only", "Katakana only", "Random"])
    
    if st.button("Mulai Game") and st.session_state.name:
        st.session_state.game_started = True
        st.session_state.score = 0
        st.session_state.mode = mode
        st.session_state.current_question, st.session_state.current_answer, st.session_state.choices = get_random_question(mode)

# Gameplay
else:
    # Ambil pertanyaan jika belum ada
    if st.session_state.current_question is None:
        st.session_state.current_question, st.session_state.current_answer, st.session_state.choices = get_random_question(st.session_state.mode)

    # Soal besar di tengah
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{st.session_state.current_question}</h1>", unsafe_allow_html=True)

    # Tampilkan pilihan jawaban tanpa reload halaman
    cols = st.columns(len(st.session_state.choices))
    for i, choice in enumerate(st.session_state.choices):
        if cols[i].button(f"**{choice}**", key=f"choice_{i}", use_container_width=True):
            if choice == st.session_state.current_answer:
                st.session_state.score += 1
            # Langsung lanjut ke pertanyaan berikutnya tanpa reload
            st.session_state.current_question, st.session_state.current_answer, st.session_state.choices = get_random_question(st.session_state.mode)

    # Tampilkan skor
    st.subheader(f"Skor: {st.session_state.score}")
    
    if st.button("Selesai & Simpan Skor"):
        save_score(st.session_state.name, st.session_state.score)
        st.session_state.game_started = False
        st.success(f"Game Selesai! Skor Akhir: {st.session_state.score}")

        # Tampilkan leaderboard
        st.subheader("Leaderboard 🏆")
        leaderboard = get_leaderboard()
        for i, (name, score, date) in enumerate(leaderboard, start=1):
            st.write(f"{i}. {name}: {score} poin ({date})")

        st.button("Main Lagi", on_click=lambda: st.rerun())