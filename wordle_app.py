import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Scrabble Wordle", page_icon="🟩", layout="centered")

# --- 2. CORE STATE & LOGIC ---
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
    st.session_state.game_started = False

# --- 3. HELPER FUNCTIONS ---
def check_guess(guess, target):
    result = ["absent"] * 5
    target_chars_count = {}
    for char in target:
        target_chars_count[char] = target_chars_count.get(char, 0) + 1
    
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result[i] = "correct"
            target_chars_count[letter] -= 1
            st.session_state.letter_status[letter] = "correct"
            
    for i, letter in enumerate(guess):
        if result[i] == "correct": continue 
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
    if st.session_state.game_over: return
    if key == "ENTER": submit_guess()
    elif key == "⌫": st.session_state.current_guess = st.session_state.current_guess[:-1]
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

def start_game():
    st.session_state.game_started = True

# --- 4. CSS STYLING ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 700px;
    }

    /* GRID STYLES */
    .wordle-row { display: flex; justify-content: center; gap: 4px; margin-bottom: 4px; }
    .letter-box {
        display: flex; justify-content: center; align-items: center;
        width: 14vw; height: 14vw; max-width: 52px; max-height: 52px;
        font-size: 1.8rem; font-weight: bold; color: white;
        text-transform: uppercase; border-radius: 4px;
    }
    .correct { background-color: #6aaa64; border: 2px solid #6aaa64; }
    .present { background-color: #c9b458; border: 2px solid #c9b458; }
    .absent  { background-color: #3a3a3c; border: 2px solid #3a3a3c; }
    .empty   { background-color: #c1e1ec; border: 2px solid #c1e1ec; color: black; }
    .active  { background-color: #c1e1ec; border: 2px solid #888; color: black; }

    /* HIDE HIDDEN BUTTONS */
    button[kind="secondary"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        position: absolute !important;
    }
    
    [data-testid="column"] {
        display: none !important;
    }

    /* NEW GAME BUTTON - Keep primary buttons visible */
    button[kind="primary"] {
        display: block !important;
        visibility: visible !important;
        width: 100% !important;
        height: 50px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Reduce spacing */
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    
    hr {
        margin: 0.5rem 0 !important;
    }

    /* Hide visual noise */
    .stDeployButton, #MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 5. UI RENDERING ---

# START SCREEN
if not st.session_state.game_started:
    st.title("Scrabble Wordle")
    st.info("Tap to enable keyboard!")
    st.button("👉 START GAME 👈", on_click=start_game, type="primary", use_container_width=True)
    st.stop()

st.title("Scrabble Wordle")

if st.session_state.message:
    st.warning(st.session_state.message)

# GRID
grid_html = ""
rows_rendered = 0
for guess in st.session_state.guesses:
    grid_html += '<div class="wordle-row">'
    statuses = check_guess(guess, st.session_state.target_word)
    for idx, letter in enumerate(guess):
        grid_html += f'<div class="letter-box {statuses[idx]}">{letter}</div>'
    grid_html += '</div>'
    rows_rendered += 1

if not st.session_state.game_over and rows_rendered < 6:
    grid_html += '<div class="wordle-row">'
    for char in st.session_state.current_guess:
        grid_html += f'<div class="letter-box active">{char}</div>'
    for _ in range(5 - len(st.session_state.current_guess)):
        grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'
    rows_rendered += 1

while rows_rendered < 6:
    grid_html += '<div class="wordle-row">'
    for _ in range(5):
        grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'
    rows_rendered += 1
st.markdown(grid_html, unsafe_allow_html=True)

# --- 6. KEYBOARD RENDERING ---

# Create a container that we'll hide completely
hidden_container = st.container()
with hidden_container:
    # Hidden buttons for state management
    for char in [chr(i) for i in range(65, 91)]:
        if st.button(char, key=f"hidden_{char}", type="secondary"):
            handle_key_click(char)
            st.rerun()
    
    if st.button("ENTER", key="hidden_enter", type="secondary"):
        handle_key_click("ENTER")
        st.rerun()
        
    if st.button("⌫", key="hidden_back", type="secondary"):
        handle_key_click("⌫")
        st.rerun()

# HTML Keyboard
keyboard_html = """
<div class="keyboard">
    <div class="keyboard-row">
        <button class="key-btn" data-key="Q">Q</button>
        <button class="key-btn" data-key="W">W</button>
        <button class="key-btn" data-key="E">E</button>
        <button class="key-btn" data-key="R">R</button>
        <button class="key-btn" data-key="T">T</button>
        <button class="key-btn" data-key="Y">Y</button>
        <button class="key-btn" data-key="U">U</button>
        <button class="key-btn" data-key="I">I</button>
        <button class="key-btn" data-key="O">O</button>
        <button class="key-btn" data-key="P">P</button>
    </div>
    <div class="keyboard-row">
        <div style="flex: 0.5"></div>
        <button class="key-btn" data-key="A">A</button>
        <button class="key-btn" data-key="S">S</button>
        <button class="key-btn" data-key="D">D</button>
        <button class="key-btn" data-key="F">F</button>
        <button class="key-btn" data-key="G">G</button>
        <button class="key-btn" data-key="H">H</button>
        <button class="key-btn" data-key="J">J</button>
        <button class="key-btn" data-key="K">K</button>
        <button class="key-btn" data-key="L">L</button>
        <div style="flex: 0.5"></div>
    </div>
    <div class="keyboard-row">
        <button class="key-btn wide-key" data-key="ENTER">ENTER</button>
        <button class="key-btn" data-key="Z">Z</button>
        <button class="key-btn" data-key="X">X</button>
        <button class="key-btn" data-key="C">C</button>
        <button class="key-btn" data-key="V">V</button>
        <button class="key-btn" data-key="B">B</button>
        <button class="key-btn" data-key="N">N</button>
        <button class="key-btn" data-key="M">M</button>
        <button class="key-btn wide-key" data-key="⌫">⌫</button>
    </div>
</div>
<style>
    .keyboard {
        margin: 10px auto 0;
        max-width: 500px;
        user-select: none;
    }
    .keyboard-row {
        display: flex;
        justify-content: center;
        gap: 4px;
        margin-bottom: 6px;
    }
    .key-btn {
        flex: 1;
        min-width: 0;
        height: 55px;
        font-size: 15px;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        background-color: #818384;
        color: white;
        cursor: pointer;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
        transition: opacity 0.1s;
    }
    .key-btn.wide-key {
        flex: 1.5;
        font-size: 12px;
    }
    .key-btn:active {
        opacity: 0.5;
    }
    @media (max-width: 600px) {
        .key-btn {
            height: 48px;
            font-size: 13px;
        }
        .key-btn.wide-key {
            font-size: 11px;
        }
        .keyboard-row {
            gap: 3px;
            margin-bottom: 4px;
        }
        .keyboard {
            margin: 5px auto 0;
        }
    }
    @media (max-width: 400px) {
        .key-btn {
            height: 42px;
            font-size: 11px;
        }
        .key-btn.wide-key {
            font-size: 10px;
        }
        .keyboard-row {
            gap: 2px;
            margin-bottom: 3px;
        }
    }
</style>
"""

# --- 7. JAVASCRIPT BRIDGE ---
js_code = """
<script>
    const letterStatus = %s;
    
    function updateKeyboardColors() {
        const keys = document.querySelectorAll('.key-btn');
        keys.forEach(btn => {
            const text = btn.getAttribute('data-key');
            
            if (letterStatus[text]) {
                if (letterStatus[text] === 'correct') {
                    btn.style.backgroundColor = '#6aaa64';
                } else if (letterStatus[text] === 'present') {
                    btn.style.backgroundColor = '#c9b458';
                } else if (letterStatus[text] === 'absent') {
                    btn.style.backgroundColor = '#3a3a3c'; 
                }
            }
            
            if (text === 'ENTER' || text === '⌫') {
                btn.style.backgroundColor = '#d3d6da';
                btn.style.color = 'black';
            }
        });
    }
    
    function handleKeyClick(key) {
        const buttons = Array.from(window.parent.document.querySelectorAll('button'));
        const targetBtn = buttons.find(btn => btn.innerText.trim() === key || btn.getAttribute('data-testid') === key);
        if (targetBtn) {
            targetBtn.click();
        }
    }
    
    // Click handlers for keyboard buttons
    document.querySelectorAll('.key-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const key = this.getAttribute('data-key');
            handleKeyClick(key);
        });
    });
    
    // Physical keyboard support
    function handlePhysicalKey(e) {
        let key = e.key.toUpperCase();
        if (key === 'ENTER') key = 'ENTER';
        if (key === 'BACKSPACE') key = '⌫';
        
        if (key.match(/^[A-Z]$/) || key === 'ENTER' || key === '⌫') {
            handleKeyClick(key);
            e.preventDefault();
        }
    }
    
    window.parent.document.addEventListener('keydown', handlePhysicalKey);
    
    // Update colors periodically
    setInterval(updateKeyboardColors, 200);
    updateKeyboardColors();
</script>
""" % str(st.session_state.letter_status).replace("None", "null")

components.html(keyboard_html + js_code, height=220)

# NEW GAME BUTTON
if st.session_state.game_over:
    st.write("")
    st.button("🔄 New Game", on_click=new_game, type="primary", use_container_width=True)
