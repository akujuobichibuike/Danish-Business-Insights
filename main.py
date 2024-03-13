# Import the necessary modules
import streamlit as st  # Streamlit library for building web apps
from auth import run_auth_page  # Function to handle the authentication page logic
from dashboard import run_dashboard  # Function to handle the dashboard logic
from styles import apply_custom_css  # Function to apply custom CSS styles

def show_landing_page():
    # Function to display the landing page of the web app
    apply_custom_css()  # Apply the custom CSS styles to the Streamlit app
    st.title("Danish Business Insights Platform")  # Display the main title of the app

    # Display the introductory markdown text explaining the app's purpose and features
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

    # Button to start the authentication process or navigate to the next page
    if st.button("Get Started"):
        st.session_state['page'] = 'auth'  # Change the session state to move to the authentication page

def main():
    # Main function to control the app's flow
    apply_custom_css()  # Apply the custom CSS styles to the Streamlit app

    # Initialize session state variables if they are not already set
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Session state to track if the user is logged in
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'  # Session state to control the current page view
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True  # Session state to toggle between login and registration views

    # Determine which page to display based on the session state
    if st.session_state.page == 'landing':
        show_landing_page()  # Show the landing page
    elif st.session_state.page == 'auth' and not st.session_state.logged_in:
        run_auth_page()  # Show the authentication page if not logged in
    elif st.session_state.logged_in:
        run_dashboard()  # Show the dashboard page if logged in

# Run the main function when the script is executed directly
if __name__ == "__main__":
    main()
