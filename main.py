# main.py
import streamlit as st
from auth import run_auth_page
from dashboard import run_dashboard
from styles import apply_custom_css

def show_landing_page():
    apply_custom_css()  # Ensure the custom CSS is applied
    st.title("Danish Business Insights Platform")
    st.markdown("""
    ## Discover Data-Driven Investment Opportunities

    Welcome to our Investment Analysis Dashboard, tailored to deliver comprehensive insights into the Danish business landscape. This platform is designed to empower investors with detailed data, enabling informed decision-making and strategic investment in Denmark’s vibrant sectors.

    **Explore our dashboard features:**
    - **Financial Trends Analysis:** Gain insights into the financial dynamics of selected Danish sectors, tracking key metrics like average profit/loss and equity over time.
    - **Financial Health Indicators:** Assess the financial vitality of sectors with critical indicators, including Return on Assets (ROA), Return on Investment (ROI), and solvency ratios.
    - **Sector Comparison:** Benchmark the financial performance of chosen companies against the average metrics of their sectors, aiding in smarter investment choices.
    - **Company Analysis:** Conduct thorough evaluations of individual companies, analyzing their financial trajectories and operational efficiencies over the years.
    - **Company to Company Comparison:** Make comparative analyses between two companies, identifying superior investment prospects based on robust financial data.
    
    Embark on your journey to smarter investing by leveraging our platform’s in-depth analysis and sectoral insights of the Danish business environment.
    """)

    if st.button("Get Started"):
        st.session_state['page'] = 'auth'

def main():
    apply_custom_css()

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True

    # Control flow based on session state
    if st.session_state.page == 'landing':
        show_landing_page()
    elif st.session_state.page == 'auth' and not st.session_state.logged_in:
        run_auth_page()
    elif st.session_state.logged_in:
        run_dashboard()

if __name__ == "__main__":
    main()