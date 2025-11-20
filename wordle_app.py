import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random

# --- 1. CONFIGURATION & STYLES ---
st.set_page_config(page_title="Scrabble Wordle", page_icon="🟩")

# --- 2. CORE LOGIC & STATE ---
if 'word_list' not in st.session_state:
    # Initialize word list once
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
    st.session_state.current_guess = ""  # The letters currently being typed
    st.session_state.game_over = False
    st.session_state.message = ""
    # Track status of each letter for the keyboard: 'correct', 'present', 'absent', or None
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
            # Only upgrade status to present if it's not already correct
            if st.session_state.letter_status[letter] != "correct":
                st.session_state.letter_status[letter] = "present"
        else:
            # Mark as absent if not found (and not already marked green/yellow from another instance)
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
    
    # Valid guess
    st.session_state.guesses.append(guess)
    check_guess(guess, st.session_state.target_word) # Updates letter status
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
# We generate CSS dynamically to color the keyboard buttons!
keyboard_css = ""
for char, status in st.session_state.letter_status.items():
    if status == "correct":
        color = "#6aaa64" # Green
        font_color = "white"
    elif status == "present":
        color = "#c9b458" # Yellow
        font_color = "white"
    elif status == "absent":
        color = "#3a3a3c" # Dark Gray
        font_color = "white"
    else:
        continue # Default grey
    
    # This CSS hack targets the button by its text content (using aria-label matching if possible, but here simple text mapping)
    # Note: Standard CSS cannot select by text content easily. 
    # Instead, we rely on the button rendering standard Streamlit buttons.
    # We simply rely on the grid visuals for now, but here is the CSS for the TILES.
    pass 

st.markdown(f"""
<style>
    /* Main Container */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 700px;
    }}
    
    /* Grid Row */
    .wordle-row {{
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-bottom: 5px;
    }}

    /* Grid Tile */
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
    
    /* Tile Colors */
    .correct {{ background-color: #6aaa64; border: 2px solid #6aaa64; }}
    .present {{ background-color: #c9b458; border: 2px solid #c9b458; }}
    .absent  {{ background-color: #3a3a3c; border: 2px solid #3a3a3c; }}
    .empty   {{ background-color: #c1e1ec; border: 2px solid #c1e1ec; color: black; }}
    .active  {{ background-color: #c1e1ec; border: 2px solid #888; color: black; animation: pop 0.1s; }}

    /* Keyboard Container */
    .keyboard-container {{
        margin-top: 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }}
    .kb-row {{
        display: flex;
        gap: 6px;
        justify-content: center;
        width: 100%;
    }}
    
    /* Buttons */
    .stButton button {{
        padding: 0 !important;
        width: 8vw !important;
        height: 12vw !important;
        max-width: 45px !important;
        max-height: 58px !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. UI RENDERING ---
st.title("Scrabble Wordle")

if st.session_state.message:
    st.info(st.session_state.message)

# RENDER THE GRID
grid_html = ""
rows_rendered = 0

# 1. Render Past Guesses
for guess in st.session_state.guesses:
    grid_html += '<div class="wordle-row">'
    statuses = check_guess(guess, st.session_state.target_word)
    for idx, letter in enumerate(guess):
        grid_html += f'<div class="letter-box {statuses[idx]}">{letter}</div>'
    grid_html += '</div>'
    rows_rendered += 1

# 2. Render Current Active Typing Row (If game not over)
if not st.session_state.game_over and rows_rendered < 6:
    grid_html += '<div class="wordle-row">'
    # Fill filled slots
    for char in st.session_state.current_guess:
        grid_html += f'<div class="letter-box active">{char}</div>'
    # Fill empty slots
    for _ in range(5 - len(st.session_state.current_guess)):
        grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'
    rows_rendered += 1

# 3. Render Remaining Empty Rows
while rows_rendered < 6:
    grid_html += '<div class="wordle-row">'
    for _ in range(5):
        grid_html += '<div class="letter-box empty"></div>'
    grid_html += '</div>'
    rows_rendered += 1

st.markdown(grid_html, unsafe_allow_html=True)

# --- 6. KEYBOARD RENDERING ---
st.write("") # Spacer

keys = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM"
]

# Helper to get button color based on status
def get_key_style(key):
    status = st.session_state.letter_status.get(key)
    if status == 'correct': return "background-color: #6aaa64 !important; color: white !important;"
    if status == 'present': return "background-color: #c9b458 !important; color: white !important;"
    if status == 'absent':  return "background-color: #3a3a3c !important; color: white !important;"
    return "background-color: #d3d6da !important; color: black !important;"

# We use standard columns for layout, but we inject style via the button key argument? 
# No, Streamlit styling is hard. 
# Instead: We render the keyboard normally, but use 'type="primary"' for colored keys is limited.
# The BEST way in pure Streamlit to mimic the keyboard is using cols.

# Row 1
cols = st.columns(10)
for i, char in enumerate(keys[0]):
    with cols[i]:
        # Apply styling hack? Difficult in pure Python. 
        # We will rely on the User Interface "Simulated" via emojis or just standard buttons.
        # To actually color them, we need to inject CSS that targets the specific button index.
        # That is very brittle.
        # Instead, we will use the standard grey buttons, but if you want, we can mark them.
        
        # Let's attempt a clever CSS injection for this specific run
        btn_id = f"btn_{char}"
        status = st.session_state.letter_status.get(char)
        
        # Emoji indicator for color blind accessibility + color workaround
        label = char
        if status == 'correct': label = "🟩" + char
        elif status == 'present': label = "🟨" + char
        elif status == 'absent': label = "⬛" + char
        
        if st.button(char, key=char, use_container_width=True):
            handle_key_click(char)
            st.rerun()

# Row 2
cols = st.columns([0.5] + [1]*9 + [0.5]) # Centering hack
with cols[0]: st.write("")
for i, char in enumerate(keys[1]):
    with cols[i+1]:
        if st.button(char, key=char, use_container_width=True):
            handle_key_click(char)
            st.rerun()
with cols[-1]: st.write("")

# Row 3 (Enter, Z-M, Backspace)
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

# New Game Button (Only shows if game over)
if st.session_state.game_over:
    st.write("")
    st.button("🔄 New Game", on_click=new_game, type="primary", use_container_width=True)

# --- 7. INJECT KEYBOARD COLORS ---
# This script finds the buttons with specific text and colors them.
# It's a Javascript hack injected into the page.
js_code = """
<script>
    const letterStatus = %s;
    
    function colorKeyboard() {
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            const text = btn.innerText;
            if (letterStatus[text]) {
                if (letterStatus[text] === 'correct') {
                    btn.style.backgroundColor = '#6aaa64';
                    btn.style.color = 'white';
                    btn.style.borderColor = '#6aaa64';
                } else if (letterStatus[text] === 'present') {
                    btn.style.backgroundColor = '#c9b458';
                    btn.style.color = 'white';
                    btn.style.borderColor = '#c9b458';
                } else if (letterStatus[text] === 'absent') {
                    btn.style.backgroundColor = '#787c7e';
                    btn.style.color = 'white';
                    btn.style.borderColor = '#787c7e';
                }
            }
            // Special styling for Enter/Backspace
            if (text === 'ENTER' || text === '⌫') {
                btn.style.backgroundColor = '#d3d6da';
                btn.style.color = 'black';
            }
        });
    }
    // Run periodically to catch re-renders
    setInterval(colorKeyboard, 100);
</script>
""" % str(st.session_state.letter_status).replace("None", "null")

st.components.v1.html(js_code, height=0, width=0)
