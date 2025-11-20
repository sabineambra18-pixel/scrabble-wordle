import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random

# --- 1. CONFIGURATION & STYLES ---
st.set_page_config(page_title="Scrabble Wordle", page_icon="🟩")

# Custom CSS to make it look like the real game
st.markdown("""
<style>
    /* Main grid styling */
    .letter-box {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 60px;
        height: 60px;
        margin: 2px;
        font-size: 30px;
        font-weight: bold;
        color: white;
        text-transform: uppercase;
        border-radius: 4px;
    }
    .correct { background-color: #6aaa64; border: 2px solid #6aaa64; } /* Green */
    .present { background-color: #c9b458; border: 2px solid #c9b458; } /* Yellow */
    .absent  { background-color: #787c7e; border: 2px solid #787c7e; } /* Grey */
    .empty   { background-color: #ffffff; border: 2px solid #d3d6da; color: black; }
    
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
    """
    Scrapes the Collins Dictionary Scrabble word list page.
    Finds all unique 5-letter uppercase words.
    """
    url = "https://scrabble.collinsdictionary.com/word-lists/five-letter-words-in-scrabble/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all text from the page
        page_text = soup.get_text()
        
        # Regex to find all 5-letter uppercase words
        # \b ensures we match whole words only
        found_words = re.findall(r'\b[A-Z]{5}\b', page_text)
        
        # Convert to set to remove duplicates (e.g., if 'TOOLS' appears in menu and list)
        unique_words = sorted(list(set(found_words)))
        
        return unique_words
    except Exception as e:
        st.error(f"Error fetching words: {e}")
        # Fallback list just in case the site is down
        return ["APPLE", "BRAIN", "CRANE", "DREAM", "EAGLE", "FEAST", "GRAPE"]

# --- 3. GAME LOGIC HELPER ---
def check_guess(guess, target):
    """
    Compares the guess with the target word.
    Returns a list of statuses: 'correct', 'present', 'absent'
    """
    result = ["absent"] * 5
    target_chars_count = {}
    
    # Count frequency of letters in target for handling duplicates correctly
    for char in target:
        target_chars_count[char] = target_chars_count.get(char, 0) + 1
    
    # First pass: Find exact matches (Greens)
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result[i] = "correct"
            target_chars_count[letter] -= 1
            
    # Second pass: Find wrong spots (Yellows)
    for i, letter in enumerate(guess):
        if result[i] == "correct":
            continue # Skip already marked greens
            
        if letter in target_chars_count and target_chars_count[letter] > 0:
            result[i] = "present"
            target_chars_count[letter] -= 1
            
    return result

# --- 4. INITIALIZATION ---
# Load words
with st.spinner("Loading 12,915 words from Collins Dictionary..."):
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
    st.session_state.current_guess = "" # Clear input

# --- 5. UI & INTERACTION ---
st.title("Scrabble Wordle Unlimited")
st.write(f"Playing with **{len(WORD_LIST):,}** valid Scrabble words.")

# Input handling
def submit_guess():
    guess = st.session_state.current_guess.upper().strip()
    
    # Validate input
    if len(guess) != 5:
        st.session_state.message = "Word must be 5 letters long."
        return
    if not guess.isalpha():
        st.session_state.message = "Letters only please."
        return
    if guess not in WORD_LIST:
        st.session_state.message = "Not in word list."
        return
    
    # Process valid guess
    st.session_state.guesses.append(guess)
    st.session_state.current_guess = "" # Clear input
    st.session_state.message = ""
    
    # Check Win/Loss
    if guess == st.session_state.target_word:
        st.session_state.message = "🎉 YOU WON! 🎉"
        st.session_state.game_over = True
    elif len(st.session_state.guesses) >= 6:
        st.session_state.message = f"Game Over! The word was {st.session_state.target_word}"
        st.session_state.game_over = True

# Input Box
if not st.session_state.game_over:
    st.text_input("Type a 5-letter word", key="current_guess", on_change=submit_guess, max_chars=5)
else:
    st.button("🔄 New Game", on_click=reset_game, type="primary")

if st.session_state.message:
    st.warning(st.session_state.message)

# --- 6. RENDER GRID ---
# We always show 6 rows. Fill empty rows with blank boxes.
for i in range(6):
    cols = st.columns(5)
    
    # Determine content for this row
    if i < len(st.session_state.guesses):
        # Render a guessed row
        this_guess = st.session_state.guesses[i]
        statuses = check_guess(this_guess, st.session_state.target_word)
        
        for idx, col in enumerate(cols):
            letter = this_guess[idx]
            status = statuses[idx]
            col.markdown(f'<div class="letter-box {status}">{letter}</div>', unsafe_allow_html=True)
    else:
        # Render an empty row
        for col in cols:
            col.markdown('<div class="letter-box empty"></div>', unsafe_allow_html=True)

# --- 7. DEBUG (Optional: remove comments to see the word while testing) ---
# st.write(f"Debug: {st.session_state.target_word}")