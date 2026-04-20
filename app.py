import streamlit as st
import ollama
import json

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Hamster Chat", page_icon="🐹", layout="centered")

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600&display=swap');

/* ── ROOT ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #0e0720 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2d9f3;
}

/* Noise texture overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

/* Ambient glow blobs */
.stApp::after {
    content: '';
    position: fixed;
    top: -200px;
    left: -150px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.stApp > * { position: relative; z-index: 1; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 780px !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.025) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(20px);
}

section[data-testid="stSidebar"] > div {
    padding: 20px 16px;
}

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

/* ── CHAT INPUT ── */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.04) !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    padding: 12px 16px !important;
}

div[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 24px !important;
    color: #e2d9f3 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 18px !important;
    caret-color: #a78bfa;
}

div[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(167, 139, 250, 0.4) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,255,255,0.25) !important;
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

/* Avatar styling */
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    border-radius: 50% !important;
    width: 30px !important;
    height: 30px !important;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-color: rgba(139, 92, 246, 0.8) transparent transparent transparent !important;
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

/* ── ERROR ── */
.stAlert {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
    border-radius: 12px !important;
    color: rgba(255,150,150,0.9) !important;
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
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 18px 24px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(10px);
    position: sticky;
    top: 0;
    z-index: 100;
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


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
        font-family: 'Space Grotesk', sans-serif;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.3);
        text-transform: uppercase;
        margin-bottom: 12px;
    ">Your vibe</div>
    """, unsafe_allow_html=True)

    user_sticker_choice = st.selectbox(
        "Emotion",
        ["None"] + list(STICKER_MAP.keys()),
        label_visibility="collapsed",
    )

    # Preview selected sticker
    if user_sticker_choice != "None":
        bg, fg = EMOTION_COLORS.get(user_sticker_choice, ("#e9d5ff", "#4c1d95"))
        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            margin: 12px 0;
        ">
            <div style="font-size: 11px; color: rgba(255,255,255,0.3); margin-bottom: 8px;">preview</div>
            <span style="
                display: inline-block;
                background: {bg}22;
                color: {bg};
                border: 1px solid {bg}44;
                border-radius: 20px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 500;
            ">{user_sticker_choice}</span>
        </div>
        """, unsafe_allow_html=True)
        st.image(STICKER_MAP[user_sticker_choice], width=130)

    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

    # Divider
    st.markdown("""
    <div style="
        border-top: 1px solid rgba(255,255,255,0.06);
        margin: 8px 0 16px;
    "></div>
    """, unsafe_allow_html=True)

    # Message count
    msg_count = len(st.session_state.messages)
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: rgba(255,255,255,0.3);
        padding: 0 2px;
        margin-bottom: 12px;
    ">
        <span>memory</span>
        <span style="color: rgba(167,139,250,0.7);">{msg_count} msg{"s" if msg_count != 1 else ""}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 clear memory"):
        st.session_state.messages = []
        st.rerun()

    # Emotion key
    st.markdown("""
    <div style="
        margin-top: 24px;
        font-size: 11px;
        letter-spacing: 0.08em;
        color: rgba(255,255,255,0.25);
        text-transform: uppercase;
        margin-bottom: 10px;
    ">emotion key</div>
    """, unsafe_allow_html=True)

    for emotion, (bg, fg) in list(EMOTION_COLORS.items())[:8]:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 3px 0;
        ">
            <div style="
                width: 8px; height: 8px;
                border-radius: 50%;
                background: {bg};
                flex-shrink: 0;
            "></div>
            <span style="font-size: 12px; color: rgba(255,255,255,0.4);">{emotion}</span>
        </div>
        """, unsafe_allow_html=True)


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


# ── INPUT & RESPONSE ──────────────────────────────────────────────────────────
if prompt := st.chat_input("say something fr fr..."):

    # ── User message
    user_data = {"role": "user", "content": prompt}
    if user_sticker_choice != "None":
        user_data["sticker"] = STICKER_MAP[user_sticker_choice]

    st.session_state.messages.append(user_data)

    with st.chat_message("user"):
        st.markdown(prompt)
        if "sticker" in user_data:
            st.image(user_data["sticker"], width=140)

    # ── Build context
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

    # ── AI response
    with st.chat_message("assistant"):
        # Typing indicator placeholder
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div style="
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px 18px 18px 4px;
            display: inline-flex;
            width: fit-content;
        ">
            <span style="font-size: 13px; color: rgba(255,255,255,0.35); font-style: italic;">hamster is thinking</span>
            <span style="display:flex;gap:3px;margin-left:4px;">
                <span style="width:5px;height:5px;border-radius:50%;background:rgba(167,139,250,0.6);animation:pulse 1s infinite 0s"></span>
                <span style="width:5px;height:5px;border-radius:50%;background:rgba(167,139,250,0.4);animation:pulse 1s infinite 0.2s"></span>
                <span style="width:5px;height:5px;border-radius:50%;background:rgba(167,139,250,0.2);animation:pulse 1s infinite 0.4s"></span>
            </span>
        </div>
        <style>
        @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1); }
        }
        </style>
        """, unsafe_allow_html=True)

        try:
            response = ollama.chat(
                model="hamster-bot",
                messages=context,
                format="json",
            )

            data = json.loads(response["message"]["content"])
            reply_text = data.get("message", "")
            emotion = (data.get("emotion") or "").lower().strip() or None

            # Clear typing indicator
            typing_placeholder.empty()

            # Render reply
            st.markdown(reply_text)

            # Emotion badge
            if emotion and emotion in EMOTION_COLORS:
                bg, fg = EMOTION_COLORS[emotion]
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

            # Sticker
            ai_sticker = STICKER_MAP.get(emotion, None) if emotion else None
            if ai_sticker:
                st.image(ai_sticker, width=140)

            # Save to session
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply_text,
                "emotion": emotion,
                "sticker": ai_sticker,
            })

        except json.JSONDecodeError:
            typing_placeholder.empty()
            st.error("the hamster fumbled the json ngl 💀")

        except Exception as e:
            typing_placeholder.empty()
            st.error(f"hamster got cooked: {e}")