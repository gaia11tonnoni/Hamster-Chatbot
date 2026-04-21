import streamlit as st
import ollama
import json

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hamster Chat",
    page_icon="🐹",
    layout="wide",  # ← important (gives sidebar space)
    initial_sidebar_state="expanded"  # ← forces sidebar visible
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600&display=swap');

html, body, .stApp {
    background: #0e0720 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2d9f3;
}

/* KEEP visuals but don’t break layout */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    opacity: 0.4;
    pointer-events: none;
}

/* DO NOT kill layout width */
.block-container {
    padding: 1.5rem !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Hide clutter only */
#MainMenu, footer {visibility: hidden;}

/* ── SELECTBOX ── */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(168, 85, 247, 0.25) !important;
    border-radius: 12px !important;
    color: #e2d9f3 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    width: 100%;
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.5) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important;
    padding: 8px 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(239, 68, 68, 0.12) !important;
    border-color: rgba(239, 68, 68, 0.3) !important;
    color: rgba(255, 130, 130, 0.9) !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 4px 0 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown > div {
    background: rgba(139, 92, 246, 0.18);
    border: 1px solid rgba(139, 92, 246, 0.28);
    border-radius: 18px 18px 4px 18px;
    padding: 10px 14px;
    font-size: 14px;
    line-height: 1.6;
    display: inline-block;
    max-width: 80%;
    float: right;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown > div {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px 18px 18px 4px;
    padding: 10px 14px;
    font-size: 14px;
    line-height: 1.6;
    display: inline-block;
    max-width: 80%;
}

/* ── IMAGES (stickers) ── */
img { border-radius: 12px !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.3);
    border-radius: 4px;
}


</style>
""", unsafe_allow_html=True)

# ── STICKER MAP ───────────────────────────────────────────────────────────────
STICKER_MAP = {
    "happy":     "hamster/happy.gif",
    "sad":       "hamster/screaming.gif",
    "angry":     "hamster/angry.gif",
    "surprised": "hamster/concerned.gif",
    "actually":  "hamster/ermActully.gif",
    "love":      "hamster/love-you-hamster.gif",
    "normal":    "hamster/oh-wow.gif",
    "staring":   "hamster/stare.gif",
    "sus":       "hamster/sus.gif",
    "yes":       "hamster/thumbUp.gif",
    "no":        "hamster/thumbDown.gif",
    "thinking":  "hamster/toung.gif",
}

# ── STICKER MAP ───────────────────────────────────────────────────────────────
STICKER_MAP = {
    "happy":     "hamster/happy.gif",
    "sad":       "hamster/screaming.gif",
    "angry":     "hamster/angry.gif",
    "surprised": "hamster/concerned.gif",
    "actually":  "hamster/ermActully.gif",
    "love":      "hamster/love-you-hamster.gif",
    "normal":    "hamster/oh-wow.gif",
    "staring":   "hamster/stare.gif",
    "sus":       "hamster/sus.gif",
    "yes":       "hamster/thumbUp.gif",
    "no":        "hamster/thumbDown.gif",
    "thinking":  "hamster/toung.gif",
}

EMOTION_COLORS = {
    "happy":     ("#fef08a", "#854d0e"),
    "sad":       ("#bfdbfe", "#1e3a5f"),
    "angry":     ("#fecaca", "#7f1d1d"),
    "surprised": ("#fed7aa", "#7c2d12"),
    "actually":  ("#e9d5ff", "#4c1d95"),
    "love":      ("#fbcfe8", "#831843"),
    "normal":    ("#d1fae5", "#064e3b"),
    "staring":   ("#e0e7ff", "#1e1b4b"),
    "sus":       ("#fef9c3", "#713f12"),
    "yes":       ("#bbf7d0", "#14532d"),
    "no":        ("#fecaca", "#7f1d1d"),
    "thinking":  ("#ddd6fe", "#2e1065"),
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    position: fixed;
    top: 50;
    width: 100%;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 18px 24px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(14, 7, 32, 0.9);
    backdrop-filter: blur(10px);
    z-index: 999;
">
    <div style="
        width: 38px; height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
        box-shadow: 0 0 20px rgba(139,92,246,0.4);
    ">🐹</div>
    <div>
        <div style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #e9d5ff;
            letter-spacing: -0.02em;
        ">Hamster AI</div>
        <div style="font-size: 11px; color: rgba(255,255,255,0.3); margin-top: 1px;">
            brain-rot mode: <span style="color: #4ade80;">ON</span>
        </div>
    </div>
    <div style="
        margin-left: auto;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #4ade80;
        box-shadow: 0 0 0 3px rgba(74,222,128,0.15), 0 0 10px rgba(74,222,128,0.4);
    "></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🐹 Hamster Control Panel")

    user_sticker_choice = st.selectbox(
        "Your vibe",
        ["None"] + list(STICKER_MAP.keys())
    )

    if st.button("Clear memory"):
        st.session_state.messages = []
        st.rerun()

# ── CHAT HISTORY ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Emotion badge for assistant
        if msg["role"] == "assistant" and "emotion" in msg and msg["emotion"]:
            emotion = msg["emotion"]
            bg, fg = EMOTION_COLORS.get(emotion, ("#e9d5ff", "#4c1d95"))
            st.markdown(f"""
            <div style="margin-top: 6px;">
                <span style="
                    display: inline-block;
                    background: {bg}20;
                    color: {bg};
                    border: 1px solid {bg}40;
                    border-radius: 20px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 500;
                ">{emotion}</span>
            </div>
            """, unsafe_allow_html=True)

        # Sticker image
        if "sticker" in msg and msg["sticker"]:
            st.image(msg["sticker"], width=140)

# ── INPUT ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("say something..."):

    user_msg = {"role": "user", "content": prompt}

    if user_sticker_choice != "None":
        user_msg["sticker"] = STICKER_MAP[user_sticker_choice]

    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)
        if "sticker" in user_msg:
            st.image(user_msg["sticker"], width=120)

    # ── CONTEXT ───────────────────────────────────────────────────────────────
    context = [
        {
            "role": "system",
            "content": (
                "You are a teenager in a TikTok comment section in 2026. "
                "Your tone is brain-rot, ironic, and high-energy. "
                "Use slang: 'aura farming', 'cooked', 'crash out', 'demure', 'based', 'rizz'. "
                "Respond ONLY in JSON. "
                "Structure: {\"message\": \"your text\", \"emotion\": \"tag or null\"} "
                "CRITICAL: Use 'emotion' ONLY if a reaction is truly needed for the joke or vibe. Otherwise set it to null. "
                "Emotions: [happy, sad, angry, surprised, actually, love, normal, staring, sus, yes, no, thinking]"
            ),
        }
    ]

    for m in st.session_state.messages:
        context.append({"role": m["role"], "content": m["content"]})

    # ── AI RESPONSE ───────────────────────────────────────────────────────────
    with st.chat_message("assistant"):
        try:
            response = ollama.chat(
                model="hamster-bot",
                messages=context,
                format="json"
            )

            data = json.loads(response["message"]["content"])
            reply = data.get("message", "")
            emotion = data.get("emotion")

            st.markdown(reply)

            sticker = STICKER_MAP.get(emotion)
            if sticker:
                st.image(sticker, width=120)

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "emotion": emotion,
                "sticker": sticker
            })

        except json.JSONDecodeError:
            st.error("the hamster fumbled the json ngl 💀")

        except Exception as e:
            st.error(f"hamster got cooked: {e}")