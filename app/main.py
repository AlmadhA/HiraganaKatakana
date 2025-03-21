import streamlit as st
import json
import random

# CSS untuk menampilkan watermark di pojok kanan bawah
watermark = """
<style>
    .watermark {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 14px;
        color: rgba(0, 0, 0, 0.5);
        font-family: 'serif';
        z-index: 100;
    }
</style>
<div class="watermark">Webapp by @almadharpp</div>
"""
st.markdown(watermark, unsafe_allow_html=True)

# Load database
with open("data/database.json", "r", encoding="utf-8") as file:
    data = json.load(file)

def get_random_question(category):
    question = random.choice(data[category])
    choices = [question["romaji"]]
    while len(choices) < 10:
        choice = random.choice(data[category])["romaji"]
        if choice not in choices:
            choices.append(choice)
    random.shuffle(choices)
    return question, choices

# Streamlit App
st.title("Hiragana & Katakana Quiz")

# Main menu
category = st.radio("Pilih kategori:", ["Hiragana", "Katakana"], horizontal=True)

if "question" not in st.session_state:
    st.session_state.question, st.session_state.choices = get_random_question(category)
    st.session_state.score = 0

st.subheader("Tebak huruf berikut:")
st.markdown(f"## {st.session_state.question['character']}")

# Display answer choices
selected = st.radio("Pilih jawaban:", st.session_state.choices)
if st.button("Submit"):
    if selected == st.session_state.question["romaji"]:
        st.session_state.score += 1
        st.success("Benar! 🎉")
    else:
        st.error(f"Salah! Jawaban yang benar adalah {st.session_state.question['romaji']}")
    
    # Load new question
    st.session_state.question, st.session_state.choices = get_random_question(category)
    st.experimental_rerun()

st.sidebar.write(f"Score: {st.session_state.score}")
if st.sidebar.button("Reset Game"):
    st.session_state.score = 0
    st.experimental_rerun()

# Menampilkan tombol kembali ke menu utama
if st.sidebar.button("Kembali ke Menu"):
    del st.session_state.question
    del st.session_state.choices
    st.experimental_rerun()
