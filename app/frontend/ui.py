import streamlit as st
import requests

API_URL_ANALYZE = "http://127.0.0.1:8000/analyze"
API_URL_CHAT = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="AI Design Critique", layout="wide")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None


# ---------------- UI CARD ----------------
def render_card(item):
    severity = item.get("severity", "Info")

    if severity == "Critical":
        color = "#ff4b4b"
    elif severity == "Recommended":
        color = "#ffa500"
    else:
        color = "#4caf50"

    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color};
            padding: 12px;
            margin-bottom: 10px;
            background-color: #111;
            border-radius: 8px;
        ">
            <b>{item.get('category', 'N/A')}</b><br>
            <b>Issue:</b> {item.get('issue', 'N/A')}<br>
            <b>Reason:</b> {item.get('reason', 'N/A')}<br>
            <b>Suggestion:</b> {item.get('suggestion', 'N/A')}<br>
            <b>Severity:</b> {severity}
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- HEADER ----------------
st.title("🎨 AI Design Critique Assistant")
st.write("Upload UI → Analyze → Chat with AI 🚀")

st.divider()

# ---------------- IMAGE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload UI Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.session_state.uploaded_image = uploaded_file

# 🔥 SMALL IMAGE PREVIEW (TOP LIKE CHATGPT)
if st.session_state.uploaded_image:
    st.image(
        st.session_state.uploaded_image,
        caption="Uploaded UI",
        width=250  # 🔥 FIX: small size
    )

    if st.button("Analyze Design"):
        with st.spinner("🔍 Analyzing UI... please wait..."):
            files = {"file": st.session_state.uploaded_image.getvalue()}
            response = requests.post(API_URL_ANALYZE, files=files)

            if response.status_code == 200:
                result = response.json()

                if "analysis" in result:
                    st.session_state.analysis = result["analysis"]
                    st.success("✅ Analysis complete!")
                else:
                    st.error("Analysis failed")
                    st.json(result)
            else:
                st.error("API Error")


# ---------------- ANALYSIS ----------------
if st.session_state.analysis:
    st.subheader("📊 Analysis")

    for item in st.session_state.analysis:
        render_card(item)


# ---------------- CHAT ----------------
st.divider()
st.subheader("💬 Chat with AI")

# show messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
user_input = st.chat_input("Ask follow-up question...")

if user_input:
    # show user msg
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # 🔥 AI LOADING MESSAGE (IMPORTANT UX FIX)
    with st.chat_message("assistant"):
        with st.spinner("🤖 AI is thinking..."):

            response = requests.post(
                API_URL_CHAT,
                json={
                    "question": user_input,
                    "analysis": st.session_state.analysis
                }
            )

            if response.status_code == 200:
                reply = response.json().get("reply", "No response")
            else:
                reply = "Error from server"

            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})