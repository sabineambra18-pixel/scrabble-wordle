import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random

# --- 1. CONFIGURATION & STYLES ---
st.set_page_config(page_title="Scrabble Wordle", page_icon="🟩")

# Custom CSS for MOBILE RESPONSIVENESS & COLORS
st.markdown("""
<style>
    /* Center everything */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 700px;
    }
    
    /* Row container to keep boxes side-by-side */
    .wordle-row {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-bottom: 5px;
    }

    /* The Box itself - Responsive sizing */
    .letter-box {
        display: flex;
        justify-content: center;
        align-items: center;
        
        /* Smart Sizing: 15% of screen width on mobile, capped at 60px on PC */
        width: 15vw;  
        height: 15vw;
        max-width: 60px;
        max-height: 60px;
        
        font-size: 2rem; /* Starts big */
        font-weight: bold;
        color: white;
        text-transform: uppercase;
        border-radius: 4px;
    }
    
    /* Media query for very small phones to adjust font size */
    @media (max-width: 500px) {
        .letter-box {
            font-size: 1.5rem;
        }
    }

    /* Colors */
    .correct { background-color: #6aaa64; border: 2px solid #6aaa64; } 
    .present { background-color: #c9b458; border: 2px solid #c9b458; } 
    .absent  { background-color: #787c7e; border: 2px solid #787c7e; } 
    
    /* THIS IS THE LINE WE CHANGED */
    .empty   { background-color: #c1e1ec; border: 2px solid #c1e1ec; color: black; }
    
    /* Input styling */
    .stTextInput input {
        text-transform: uppercase;
        font-size: 20px;
        letter-spacing: 2px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SCRAPING FUNCTION ---
@st.cache_data
def get_all_words():
    url = "https://scrabble.collinsdictionary.com/word-lists/five-letter-words-in-scrabble/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        found_words = re.findall(r'\b[A-Z]{5}\b', page_text)
        unique_words = sorted(list(set(found_words)))
        return unique_words
    except Exception as e:
        st.error(f"Error fetching words: {e}")
        return ["APPLE", "BRAIN", "CRANE", "DREAM", "EAGLE", "FEAST", "GRAPE"]

# --- 3. GAME LOGIC HELPER ---
def check_guess(guess, target):
    result = ["absent"] * 5
    target_chars_count = {}
    for char in target:
        target_chars_count[char] = target_chars_count.get(char, 0) + 1
    
    # First pass: Greens
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result[i] = "correct"
            target_chars_count[letter] -= 1
            
    # Second pass: Yellows
    for i, letter in enumerate(guess):
        if result[i] == "correct":
            continue 
        if letter in target_chars_count and target_chars_count[letter] > 0:
            result[i] = "present"
            target_chars_count[letter] -= 1
    return result

# --- 4. INITIALIZATION ---
with st.spinner("Loading words..."):
    WORD_LIST = get_all_words()

if 'target_word' not in st.session_state:
    st.session_state.target_word = random.choice(WORD_LIST)
    st.session_state.guesses = []
    st.session_state.game_over = False
    st.session_state.message = ""

def reset_game():
    st.session_state.target_word = random.choice(WORD_LIST)
    st.session_state.guesses = []
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.current_guess = "" 

# --- 5. UI & INTERACTION ---
st.title("Scrabble Wordle")
st.write(f"Valid words: **{len(WORD_LIST):,}**")

def submit_guess():
    guess = st.session_state.current_guess.upper().strip()
    if len(guess) != 5:
        st.session_state.message = "Word must be 5 letters long."
        return
    if not guess.isalpha():
        st.session_state.message = "Letters only please."
        return
    if guess not in WORD_LIST:
        st.session_state.message = "Not in word list."
        return
    
    st.session_state.guesses.append(guess)
    st.session_state.current_guess = "" 
    st.session_state.message = ""
    
    if guess == st.session_state.target_word:
        st.session_state.message = "🎉 YOU WON! 🎉"
        st.session_state.game_over = True
    elif len(st.session_state.guesses) >= 6:
        st.session_state.message = f"Game Over! The word was {st.session_state.target_word}"
        st.session_state.game_over = True

if not st.session_state.game_over:
    st.text_input("Type a 5-letter word", key="current_guess", on_change=submit_guess, max_chars=5)
else:
    st.button("🔄 New Game", on_click=reset_game, type="primary")

if st.session_state.message:
    st.warning(st.session_state.message)

# --- 6. RENDER GRID (MOBILE FRIENDLY HTML) ---
grid_html = ""
for i in range(6):
    grid_html += '<div class="wordle-row">'
    if i < len(st.session_state.guesses):
        this_guess = st.session_state.guesses[i]
        statuses = check_guess(this_guess, st.session_state.target_word)
        for idx, letter in enumerate(this_guess):
            status = statuses[idx]
            grid_html += f'<div class="letter-box {status}">{letter}</div>'
    else:
        for _ in range(5):
            grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'

st.markdown(grid_html, unsafe_allow_html=True)
