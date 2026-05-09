import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/analyze"

st.title("🎨 AI Design Critique Assistant")

uploaded_file = st.file_uploader("Upload UI Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded UI", use_column_width=True)

    if st.button("Analyze Design"):
        with st.spinner("Analyzing..."):

            files = {"file": uploaded_file.getvalue()}
            response = requests.post(API_URL, files=files)

            if response.status_code == 200:
                result = response.json()

                st.subheader("📊 Analysis Result")

                for item in result["analysis"]:
                    st.markdown(f"### {item['category']}")
                    st.write(f"**Issue:** {item['issue']}")
                    st.write(f"**Reason:** {item['reason']}")
                    st.write(f"**Suggestion:** {item['suggestion']}")
                    st.write(f"**Severity:** {item['severity']}")
                    st.divider()