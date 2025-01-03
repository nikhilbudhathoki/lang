import streamlit as st
from main import main as main_page
from main2 import main as second_page

# Set the page configuration here
st.set_page_config(layout="wide", page_title="Combined App")

def run():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["TRANSLATOR", "META DATA"])

    if page == "TRANSLATOR":
        main_page()
    elif page == "META DATA":
        second_page()

if __name__ == "__main__":
    run()
