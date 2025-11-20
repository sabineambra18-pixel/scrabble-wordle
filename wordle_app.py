import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random
import streamlit.components.v1 as components

# --- 1. CONFIGURATION & STYLES ---
st.set_page_config(page_title="Scrabble Wordle", page_icon="🟩")

# --- 2. CORE LOGIC & STATE ---
if 'word_list' not in st.session_state:
    try:
        url = "https://scrabble.collinsdictionary.com/word-lists/five-letter-words-in-scrabble/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        found_words = re.findall(r'\b[A-Z]{5}\b', page_text)
        st.session_state.word_list = sorted(list(set(found_words)))
    except:
        st.session_state.word_list = ["APPLE", "BRAIN", "CRANE", "DREAM", "EAGLE", "FEAST", "GRAPE"]

if 'target_word' not in st.session_state:
    st.session_state.target_word = random.choice(st.session_state.word_list)
    st.session_state.guesses = []
    st.session_state.current_guess = ""
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.letter_status = {chr(i): None for i in range(65, 91)}

# --- 3. GAME FUNCTIONS ---
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
            st.session_state.letter_status[letter] = "correct"
            
    # Second pass: Yellows
    for i, letter in enumerate(guess):
        if result[i] == "correct":
            continue 
        if letter in target_chars_count and target_chars_count[letter] > 0:
            result[i] = "present"
            target_chars_count[letter] -= 1
            if st.session_state.letter_status[letter] != "correct":
                st.session_state.letter_status[letter] = "present"
        else:
            if st.session_state.letter_status[letter] not in ["correct", "present"]:
                 st.session_state.letter_status[letter] = "absent"
    return result

def handle_key_click(key):
    if st.session_state.game_over:
        return

    if key == "ENTER":
        submit_guess()
    elif key == "⌫":
        st.session_state.current_guess = st.session_state.current_guess[:-1]
    else:
        if len(st.session_state.current_guess) < 5:
            st.session_state.current_guess += key

def submit_guess():
    guess = st.session_state.current_guess
    if len(guess) != 5:
        st.session_state.message = "Not enough letters"
        return
    if guess not in st.session_state.word_list:
        st.session_state.message = "Not in word list"
        return
    
    st.session_state.guesses.append(guess)
    check_guess(guess, st.session_state.target_word)
    st.session_state.current_guess = ""
    st.session_state.message = ""

    if guess == st.session_state.target_word:
        st.session_state.message = "🎉 YOU WON! 🎉"
        st.session_state.game_over = True
    elif len(st.session_state.guesses) >= 6:
        st.session_state.message = f"Word was: {st.session_state.target_word}"
        st.session_state.game_over = True

def new_game():
    st.session_state.target_word = random.choice(st.session_state.word_list)
    st.session_state.guesses = []
    st.session_state.current_guess = ""
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.letter_status = {chr(i): None for i in range(65, 91)}

# --- 4. CSS STYLING ---
st.markdown(f"""
<style>
    /* Main Container */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 700px;
    }}

    /* --- FORCE MOBILE KEYBOARD TO STAY HORIZONTAL --- */
    /* This forces Streamlit columns to share space instead of stacking on mobile */
    @media (max-width: 768px) {{
        div[data-testid="column"] {{
            width: auto !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
            padding: 0 1px !important; /* Tighter spacing on phone */
        }}
        div[data-testid="stHorizontalBlock"] {{
            gap: 2px !important;
        }}
    }}

    /* Grid Styles */
    .wordle-row {{
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-bottom: 5px;
    }}
    .letter-box {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 14vw;  
        height: 14vw;
        max-width: 55px;
        max-height: 55px;
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        text-transform: uppercase;
        border-radius: 4px;
    }}
    .correct {{ background-color: #6aaa64; border: 2px solid #6aaa64; }}
    .present {{ background-color: #c9b458; border: 2px solid #c9b458; }}
    .absent  {{ background-color: #3a3a3c; border: 2px solid #3a3a3c; }}
    .empty   {{ background-color: #c1e1ec; border: 2px solid #c1e1ec; color: black; }}
    .active  {{ background-color: #c1e1ec; border: 2px solid #888; color: black; animation: pop 0.1s; }}
    
    /* Button Styling */
    .stButton button {{
        padding: 0 !important;
        height: 12vw !important;
        max-height: 58px !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: none !important;
        width: 100%; 
    }}
    /* Make text smaller on mobile so "ENTER" fits */
    @media (max-width: 500px) {{
        .stButton button {{
            font-size: 0.8rem !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. UI RENDERING ---
st.title("Scrabble Wordle")

if st.session_state.message:
    st.info(st.session_state.message)

# GRID
grid_html = ""
rows_rendered = 0

# Past Guesses
for guess in st.session_state.guesses:
    grid_html += '<div class="wordle-row">'
    statuses = check_guess(guess, st.session_state.target_word)
    for idx, letter in enumerate(guess):
        grid_html += f'<div class="letter-box {statuses[idx]}">{letter}</div>'
    grid_html += '</div>'
    rows_rendered += 1

# Active Row
if not st.session_state.game_over and rows_rendered < 6:
    grid_html += '<div class="wordle-row">'
    for char in st.session_state.current_guess:
        grid_html += f'<div class="letter-box active">{char}</div>'
    for _ in range(5 - len(st.session_state.current_guess)):
        grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'
    rows_rendered += 1

# Empty Rows
while rows_rendered < 6:
    grid_html += '<div class="wordle-row">'
    for _ in range(5):
        grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'
    rows_rendered += 1

st.markdown(grid_html, unsafe_allow_html=True)

# --- 6. KEYBOARD RENDERING ---
st.write("")
keys = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

# Row 1
cols = st.columns(10)
for i, char in enumerate(keys[0]):
    with cols[i]:
        if st.button(char, key=char, use_container_width=True):
            handle_key_click(char)
            st.rerun()

# Row 2
cols = st.columns([0.5] + [1]*9 + [0.5])
with cols[0]: st.write("")
for i, char in enumerate(keys[1]):
    with cols[i+1]:
        if st.button(char, key=char, use_container_width=True):
            handle_key_click(char)
            st.rerun()
with cols[-1]: st.write("")

# Row 3
cols = st.columns([1.5] + [1]*7 + [1.5])
with cols[0]:
    if st.button("ENTER", key="ENTER", use_container_width=True):
        handle_key_click("ENTER")
        st.rerun()
for i, char in enumerate(keys[2]):
    with cols[i+1]:
        if st.button(char, key=char, use_container_width=True):
            handle_key_click(char)
            st.rerun()
with cols[-1]:
    if st.button("⌫", key="BACK", use_container_width=True):
        handle_key_click("⌫")
        st.rerun()

if st.session_state.game_over:
    st.write("")
    st.button("🔄 New Game", on_click=new_game, type="primary", use_container_width=True)

# --- 7. JAVASCRIPT BRIDGE ---
js_code = """
<script>
    const letterStatus = %s;
    
    function updateUI() {
        const buttons = Array.from(window.parent.document.querySelectorAll('button'));
        buttons.forEach(btn => {
            const text = btn.innerText.trim();
            if (letterStatus[text]) {
                if (letterStatus[text] === 'correct') {
                    btn.style.backgroundColor = '#6aaa64';
                    btn.style.color = 'white';
                } else if (letterStatus[text] === 'present') {
                    btn.style.backgroundColor = '#c9b458';
                    btn.style.color = 'white';
                } else if (letterStatus[text] === 'absent') {
                    btn.style.backgroundColor = '#3a3a3c'; 
                    btn.style.color = 'white';
                }
            }
            if (text === 'ENTER' || text === '⌫') {
                btn.style.backgroundColor = '#d3d6da';
                btn.style.color = 'black';
            }
        });
    }

    window.parent.document.addEventListener('keydown', function(e) {
        let key = e.key.toUpperCase();
        if (key === 'ENTER') key = 'ENTER';
        if (key === 'BACKSPACE') key = '⌫';
        
        const buttons = Array.from(window.parent.document.querySelectorAll('button'));
        const targetBtn = buttons.find(btn => btn.innerText.trim() === key);
        if (targetBtn) {
            targetBtn.click();
        }
    });

    setInterval(updateUI, 200);
</script>
""" % str(st.session_state.letter_status).replace("None", "null")

components.html(js_code, height=0, width=0)
