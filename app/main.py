import streamlit as st
import random
import json
import gspread
import time
from google.oauth2.service_account import Credentials

# Load secrets dari Streamlit
service_account_info = json.loads(st.secrets["google"]["service_account"])
credentials = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])

# Gunakan credentials untuk akses Google Sheets
gc = gspread.authorize(credentials)
SHEET_ID = "11coLcirjxLmyLEZFbMfj9R6A2Fz4mMD3182x_XHMr7E"
sheet = gc.open_by_key(SHEET_ID).sheet1

def get_random_question(mode, data):
    """ Mengambil pertanyaan acak sesuai mode permainan """
    category = "Hiragana" if mode == "Hiragana only" else "Katakana" if mode == "Katakana only" else random.choice(["Hiragana", "Katakana"])
    question = random.choice(data[category])
    correct_answer = question["romaji"]
    
    choices = random.sample([q["romaji"] for cat in data.values() for q in cat], 3)
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

# Load database
with open("data/database.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Inisialisasi sesi
if "game_started" not in st.session_state:
    st.session_state.update({"game_started": False, "score": 0, "name": "", "current_question": None, "current_answer": None, "choices": []})

# Input nama pemain
if not st.session_state.game_started:
    st.session_state.name = st.text_input("Masukkan Nama/Inisial:", "")
    mode = st.radio("Pilih Mode Permainan:", ["Hiragana only", "Katakana only", "Random"])
    
    if st.button("Mulai Game") and st.session_state.name:
        st.session_state.update({"game_started": True, "score": 0, "mode": mode})
        st.session_state.current_question, st.session_state.current_answer, st.session_state.choices = get_random_question(mode, data)

# Gameplay
else:
    if st.session_state.current_question is None:
        st.session_state.current_question, st.session_state.current_answer, st.session_state.choices = get_random_question(st.session_state.mode, data)
    
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{st.session_state.current_question}</h1>", unsafe_allow_html=True)
    
    cols = st.columns(len(st.session_state.choices))
    for i, choice in enumerate(st.session_state.choices):
        if cols[i].button(f"**{choice}**", key=f"choice_{i}", use_container_width=True):
            if choice == st.session_state.current_answer:
                st.session_state.score += 1
            st.session_state.current_question, st.session_state.current_answer, st.session_state.choices = get_random_question(st.session_state.mode, data)

    st.subheader(f"Skor: {st.session_state.score}")
    
    if st.button("Selesai & Simpan Skor"):
        save_score(st.session_state.name, st.session_state.score)
        st.session_state.game_started = False
        st.success(f"Game Selesai! Skor Akhir: {st.session_state.score}")
        
        st.subheader("Leaderboard 🏆")
        leaderboard = get_leaderboard()
        for i, (name, score, date) in enumerate(leaderboard, start=1):
            st.write(f"{i}. {name}: {score} poin ({date})")
        
        st.button("Main Lagi", on_click=lambda: st.rerun())