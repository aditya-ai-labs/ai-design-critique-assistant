import streamlit as st
import requests
import uuid

API_URL_ANALYZE = "http://127.0.0.1:8000/analyze"
API_URL_CHAT = "http://127.0.0.1:8000/chat"
API_URL_IMPROVE = "http://127.0.0.1:8000/improve"
API_URL_EXPORT = "http://127.0.0.1:8000/export"

st.set_page_config(page_title="AI Design Critique", layout="wide")

# ---------------- SESSION INIT ----------------
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "current_session" not in st.session_state:
    session_id = str(uuid.uuid4())
    st.session_state.sessions[session_id] = {
        "messages": [],
        "analysis": None,
        "image": None,
        "improved_image": None,
        "title": "New Chat"
    }
    st.session_state.current_session = session_id

current_id = st.session_state.get("current_session")

if current_id not in st.session_state.sessions:
    current_id = list(st.session_state.sessions.keys())[0]
    st.session_state.current_session = current_id

session = st.session_state.sessions[current_id]

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("💬 Chat Sessions")

    if st.button("➕ New Chat"):
        session_id = str(uuid.uuid4())
        st.session_state.sessions[session_id] = {
            "messages": [],
            "analysis": None,
            "image": None,
            "improved_image": None,
            "title": "New Chat"
        }
        st.session_state.current_session = session_id
        st.rerun()

    if st.button("🗑 Delete Current Chat"):
        del st.session_state.sessions[st.session_state.current_session]

        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {
            "messages": [],
            "analysis": None,
            "image": None,
            "improved_image": None,
            "title": "New Chat"
        }
        st.session_state.current_session = new_id
        st.rerun()

    # ✅ FIXED SESSION LIST LOOP
    for sid, data in st.session_state.sessions.items():
        label = data.get("title", "New Chat")[:20]

        if st.button(f"💬 {label}", key=f"session_{sid}"):
            st.session_state.current_session = sid
            st.rerun()

    st.divider()

    # ---------------- EXTRA FEATURES ----------------
    st.subheader("📢 Feedback")
    feedback = st.text_area("Your feedback...")
    if st.button("Submit Feedback"):
        st.success("Thanks for your feedback! 🙌")

    st.divider()

    st.subheader("ℹ️ About Us")
    st.write("AI Design Critique Assistant helps analyze UI/UX designs using AI.")

    st.divider()

    st.subheader("📞 Contact")
    st.write("📱 9006938584")
    st.write("📧 learningaiwithaadi@gmail.com")

# ---------------- UI CARD ----------------
def render_card(item):
    color = "#4caf50"
    if item.get("severity") == "Critical":
        color = "#ff4b4b"
    elif item.get("severity") == "Recommended":
        color = "#ffa500"

    st.markdown(
        f"""
        <div style="border-left:5px solid {color};padding:10px;margin:10px 0;background:#111;border-radius:8px;">
        <b>{item.get('category')}</b><br>
        Issue: {item.get('issue')}<br>
        Suggestion: {item.get('suggestion')}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- HEADER ----------------
st.title("🎨 AI Design Critique Assistant")
st.divider()

# ---------------- IMAGE ----------------
uploaded_file = st.file_uploader("Upload UI", type=["png", "jpg", "jpeg"])

if uploaded_file:
    session["image"] = uploaded_file

if session["image"]:
    st.image(session["image"], width=250)

    if st.button("Analyze Design"):
        with st.spinner("Analyzing..."):
            res = requests.post(API_URL_ANALYZE, files={"file": session["image"].getvalue()})

            if res.status_code == 200:
                session["analysis"] = res.json().get("analysis")
                session["title"] = "UI Analysis"

# ---------------- ANALYSIS ----------------
if session["analysis"]:
    st.subheader("📊 Analysis")
    for item in session["analysis"]:
        render_card(item)

# ---------------- IMPROVED UI ----------------
if session["analysis"]:
    if st.button("✨ Generate Improved UI"):
        with st.spinner("Generating improved UI..."):
            res = requests.post(API_URL_IMPROVE, json={"analysis": session["analysis"]})

            if res.status_code == 200:
                session["improved_image"] = res.json().get("image")

if session["improved_image"]:
    st.subheader("🖼 Improved UI")
    st.image(session["improved_image"])

# ---------------- PDF DOWNLOAD ----------------
if session["analysis"]:
    res = requests.post(
        API_URL_EXPORT,
        json={
            "analysis": session["analysis"],
            "image": session["improved_image"]
        }
    )

    st.download_button(
        "📄 Download Report",
        res.content,
        file_name="design_report.pdf",
        mime="application/pdf"
    )

# ---------------- CHAT ----------------
st.subheader("💬 Chat")

# ✅ SHOW BOTH USER + AI MESSAGES
for msg in session.get("messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask...")

if user_input:
    # ✅ SHOW USER MESSAGE IN UI (FIX)
    with st.chat_message("user"):
        st.markdown(user_input)

    session["messages"].append({"role": "user", "content": user_input})

    if session["title"] == "New Chat":
        session["title"] = user_input[:20]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = requests.post(
                API_URL_CHAT,
                json={
                    "question": user_input,
                    "analysis": session["analysis"]
                }
            )

            reply = res.json().get("reply", "Error")
            st.markdown(reply)

    session["messages"].append({"role": "assistant", "content": reply})

    st.rerun()