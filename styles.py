import streamlit as st

# Define global CSS styles
CUSTOM_CSS = """
<style>
body {
    color: #333;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background-color: #4F8BF9;
}
h1 {
    color: #2E3D49;
}
.stButton > button {
    color: #ffffff;
    background-color: #4F8BF9;
    border-radius: 5px;
    padding: 10px 20px;
    margin: 5px 0;
    transition: background-color 0.3s;
}

.stButton > button:hover {
    background-color: #3a6f8f;
}
</style>
"""

def apply_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)