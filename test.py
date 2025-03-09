import streamlit as st

st.write("Checking API Key...")

if "API_KEY" in st.secrets:
    st.success("✅ API Key is loaded successfully!")
    st.write(f"API Key starts with: {st.secrets['API_KEY'][:5]}*****")  # Debugging
else:
    st.error("❌ API Key not found! Please check Streamlit Cloud secrets.")
