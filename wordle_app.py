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
    st.session_state.game_started = False # For the click-to-start overlay

# --- 3. HELPER FUNCTIONS ---
def check_guess(guess, target):
    result = ["absent"] * 5
    target_chars_count = {}
    for char in target:
        target_chars_count[char] = target_chars_count.get(char, 0) + 1
    
    # Green Pass
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result[i] = "correct"
            target_chars_count[letter] -= 1
            st.session_state.letter_status[letter] = "correct"
            
    # Yellow Pass
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

# --- 4. THE "FLOAT" CSS LAYOUT ---
st.markdown("""
<style>
    /* Center App */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 600px;
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

    /* KEYBOARD LAYOUT - THE FIX */
    /* We target the div wrapping the buttons and make them display inline */
    div.row-widget.stButton {
        display: inline-block !important;
        width: 9% !important; /* Fits 10 keys + margin */
        margin: 0.5% !important;
        padding: 0 !important;
    }
    
    /* Special Widths for Enter/Backspace */
    div.row-widget.stButton[data-testid="stButton"] button {
        width: 100%;
    }
    
    /* Button Styling */
    .stButton button {
        padding: 0 !important;
        height: 50px !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 4px !important;
    }
    
    /* Mobile adjustments */
    @media (max-width: 600px) {
        .stButton button {
            font-size: 0.9rem !important;
            height: 45px !important;
        }
        div.row-widget.stButton {
            width: 9% !important;
            margin: 0.5% !important;
        }
    }

    /* Hide elements that mess up layout */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 5. UI RENDERING ---

# CLICK TO START OVERLAY (Fixes PC Focus)
if not st.session_state.game_started:
    st.title("Scrabble Wordle")
    st.info("Click the button below to enable keyboard typing!")
    st.button("👉 CLICK HERE TO START 👈", on_click=start_game, type="primary", use_container_width=True)
    st.stop() # Stop rendering the rest until clicked

st.title("Scrabble Wordle")

if st.session_state.message:
    st.warning(st.session_state.message)

# RENDER GAME GRID (HTML)
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

# --- 6. KEYBOARD RENDERING (NO COLUMNS - INLINE BLOCK METHOD) ---
st.write("---")

# Helper to render a row of keys
def render_keys(key_string):
    # We render buttons sequentially. CSS makes them sit side-by-side.
    for char in key_string:
        if st.button(char, key=char):
            handle_key_click(char)
            st.rerun()

# Row 1
with st.container():
    # CSS Hack: Apply centering to this container?
    # Streamlit containers are hard to target, so we rely on the Inline-Block CSS above
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    render_keys("QWERTYUIOP")
    st.markdown('</div>', unsafe_allow_html=True)

# Row 2
with st.container():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    render_keys("ASDFGHJKL")
    st.markdown('</div>', unsafe_allow_html=True)

# Row 3 (Mix of Enter/Chars/Back)
with st.container():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    # Custom manual layout for last row to get Enter/Back sizing right
    if st.button("ENTER", key="ENTER"):
        handle_key_click("ENTER")
        st.rerun()
    
    render_keys("ZXCVBNM")
    
    if st.button("⌫", key="BACK"):
        handle_key_click("⌫")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# New Game
if st.session_state.game_over:
    st.write("")
    st.button("🔄 New Game", on_click=new_game, type="primary", use_container_width=True)

# --- 7. JAVASCRIPT & COLORS ---
js_code = """
<script>
    const letterStatus = %s;
    
    function updateUI() {
        // Target all buttons
        const buttons = Array.from(window.parent.document.querySelectorAll('button'));
        
        buttons.forEach(btn => {
            const text = btn.innerText.trim();
            
            // 1. Color Logic
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
            
            // 2. Special Sizing Logic for Layout
            // We manually set widths here to help the CSS if it fails
            if (text.length === 1) {
                // Single letter keys
                btn.style.minWidth = '20px'; 
            } else if (text === 'ENTER' || text === '⌫') {
                // Special keys need to be wider
                btn.parentElement.style.width = '14% !important';
                btn.style.backgroundColor = '#d3d6da';
                btn.style.color = 'black';
            }
        });
    }

    // KEYBOARD LISTENER
    function handleKey(e) {
        let key = e.key.toUpperCase();
        if (key === 'ENTER') key = 'ENTER';
        if (key === 'BACKSPACE') key = '⌫';
        
        const buttons = Array.from(window.parent.document.querySelectorAll('button'));
        const targetBtn = buttons.find(btn => btn.innerText.trim() === key);
        
        if (targetBtn) {
            targetBtn.click();
            e.preventDefault();
        }
    }

    window.parent.document.addEventListener('keydown', handleKey);
    setInterval(updateUI, 200);
</script>
""" % str(st.session_state.letter_status).replace("None", "null")

components.html(js_code, height=0, width=0)
