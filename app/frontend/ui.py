import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/analyze"

# Page config
st.set_page_config(page_title="AI Design Critique", layout="wide")


# ✅ DEFINE FUNCTION FIRST (IMPORTANT FIX)
def render_card(item):
    severity = item.get("severity", "Info")

    # Color based on severity
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


# Title
st.markdown("# 🎨 AI Design Critique Assistant")
st.markdown("Upload your UI and get expert-level feedback 🚀")

st.divider()

# Upload section
uploaded_file = st.file_uploader("📤 Upload UI Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(uploaded_file, caption="Uploaded UI", width="stretch")

    with col2:
        if st.button("🔍 Analyze Design"):

            with st.spinner("Analyzing your design..."):

                files = {"file": uploaded_file.getvalue()}
                response = requests.post(API_URL, files=files)

                if response.status_code == 200:
                    result = response.json()

                    st.subheader("📊 Analysis Result")

                    if "analysis" in result and isinstance(result["analysis"], list):

                        for item in result["analysis"]:
                            render_card(item)

                    else:
                        st.error("⚠️ Analysis failed")
                        st.json(result)

                else:
                    st.error("API Error")