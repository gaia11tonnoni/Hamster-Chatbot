import streamlit as st
import ollama
import json
import os

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Hamster Chat", layout="centered")

# --- PURPLE THEME CSS ---
st.markdown("""
<style>

/* App background */
.stApp {
    background: linear-gradient(135deg, #2b1055, #7597de);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Chat message containers */
.stChatMessage {
    border-radius: 16px;
    padding: 10px;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
}

/* User messages */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: rgba(168, 85, 247, 0.25);
    border: 1px solid rgba(168, 85, 247, 0.4);
}

/* Assistant messages */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(99, 102, 241, 0.20);
    border: 1px solid rgba(99, 102, 241, 0.35);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #a855f7, #6366f1);
    color: white;
    border-radius: 20px;
    border: none;
    padding: 0.6rem 1rem;
    transition: 0.2s ease;
}

.stButton>button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 15px rgba(168, 85, 247, 0.6);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(20, 10, 40, 0.85);
}

/* Images */
img {
    border-radius: 16px;
    box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.3);
}

/* Selectbox */
div[data-baseweb="select"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# --- STICKER MAP ---
STICKER_MAP = {
    "happy": "hamster/happy.gif",
    "sad": "hamster/screaming.gif",
    "angry": "hamster/angry.gif",
    "surprised": "hamster/concerned.gif",
    "actually": "hamster/ermActully.gif",
    "love": "hamster/love-you-hamster.gif",
    "normal": "hamster/oh-wow.gif",
    "staring": "hamster/stare.gif",
    "sus": "hamster/sus.gif",
    "yes": "hamster/thumbUp.gif",
    "no": "hamster/thumbDown.gif",
    "thinking": "hamster/toung.gif"
}

st.markdown("<h1 style='text-align:center; color:#e9d5ff;'>Hamster AI</h1>", unsafe_allow_html=True)


# --- SESSION MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## Your Stickers")
    st.write("Choose an emotion to attach to your message")

    user_sticker_choice = st.selectbox(
        "Emotion",
        ["None"] + list(STICKER_MAP.keys())
    )

    if user_sticker_choice != "None":
        st.image(STICKER_MAP[user_sticker_choice], width=120)
        st.caption("Current emotion state")

    if st.button("Clear Memory"):
        st.session_state.messages = []
        st.rerun()


# --- CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sticker" in msg:
            st.image(msg["sticker"], width=150)


# --- INPUT ---
if prompt := st.chat_input("Type your message..."):

    user_data = {
        "role": "user",
        "content": prompt
    }

    if user_sticker_choice != "None":
        user_data["sticker"] = STICKER_MAP[user_sticker_choice]

    st.session_state.messages.append(user_data)

    with st.chat_message("user"):
        st.markdown(prompt)
        if "sticker" in user_data:
            st.image(user_data["sticker"], width=150)

    # --- BUILD CONTEXT ---
    context = [
        {
            "role": "system",
            "content": (
                "You are a teenage. Use meme language. "
                "Reply in English. Always return JSON in this format: "
                "{\"message\": \"...\", \"emotion\": \"...\"}"
            )
        }
    ]

    for m in st.session_state.messages:
        context.append({
            "role": m["role"],
            "content": m["content"]
        })

    # --- MODEL RESPONSE ---
    with st.chat_message("assistant"):
        with st.spinner("Hamster is thinking"):
            try:
                response = ollama.chat(
                    model="hamster-bot",
                    messages=context,
                    format="json"
                )

                data = json.loads(response["message"]["content"])

                reply_text = data.get("message", "")
                emotion = data.get("emotion", "normal").lower()

                ai_sticker = STICKER_MAP.get(emotion, STICKER_MAP["normal"])

                st.markdown(reply_text)
                st.image(ai_sticker, width=150)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply_text,
                    "sticker": ai_sticker
                })

            except Exception:
                st.error("The hamster got confused by the code")
