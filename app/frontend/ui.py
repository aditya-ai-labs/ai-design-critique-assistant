import streamlit as st
import requests

API_URL_ANALYZE = "http://127.0.0.1:8000/analyze"
API_URL_CHAT = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="AI Design Critique", layout="wide")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis" not in st.session_state:
    st.session_state.analysis = None


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
            padding: 15px;
            margin-bottom: 15px;
            background-color: #111;
            border-radius: 10px;
        ">
            <h4>{item.get('category', 'N/A')}</h4>
            <p><b>Issue:</b> {item.get('issue', 'N/A')}</p>
            <p><b>Reason:</b> {item.get('reason', 'N/A')}</p>
            <p><b>Suggestion:</b> {item.get('suggestion', 'N/A')}</p>
            <p><b>Severity:</b> {severity}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- HEADER ----------------
st.title("🎨 AI Design Critique Assistant")
st.write("Upload your UI and chat with AI mentor 🚀")

st.divider()

# ---------------- IMAGE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload UI Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(uploaded_file, caption="Uploaded UI", width='stretch')

    with col2:
        if st.button("Analyze Design"):
            with st.spinner("Analyzing..."):
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(API_URL_ANALYZE, files=files)

                if response.status_code == 200:
                    result = response.json()

                    if "analysis" in result:
                        st.session_state.analysis = result["analysis"]
                        st.success("Analysis complete!")
                    else:
                        st.error("Analysis failed")
                        st.json(result)
                else:
                    st.error("API Error")


# ---------------- SHOW ANALYSIS ----------------
if st.session_state.analysis:
    st.subheader("📊 Analysis")

    for item in st.session_state.analysis:
        render_card(item)


# ---------------- CHAT UI ----------------
st.divider()
st.subheader("💬 Chat with AI Mentor")

# show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
user_input = st.chat_input("Ask follow-up question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

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

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)