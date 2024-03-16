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
    ## Discover Data-Driven Investment Opportunities 🚀

    Welcome to our Investment Analysis Dashboard, designed to empower investors with actionable insights into the Danish business landscape. Dive into data-driven analyses to make informed decisions and strategically invest in Denmark’s dynamic sectors.

    **Dashboard Features:**
    - **Financial Trends Analysis 📊:** Explore the financial dynamics of selected sectors, tracking key metrics like average profit/loss and equity.
    - **Financial Health Indicators 💪:** Evaluate sectors' vitality through critical indicators such as Return on Assets (ROA), Return on Investment (ROI), and solvency ratios.
    - **Sector Comparison ⚖️:** Compare the financial performance of companies against sector averages, identifying standout performers.
    - **Company Analysis 🔍:** Delve into detailed financial trajectories and operational efficiencies of individual companies.
    - **Multi-Company Comparison 🤝:** Conduct comparative analyses of multiple companies within a sector, unveiling the strongest investment prospects based on comprehensive financial data.
    - **Hidden Gems 💎:** Uncover undervalued companies with strong financial health but recent profit dips, presenting potential rebound opportunities.

    Embark on your journey to smarter investing with our platform’s in-depth analysis and sectoral insights. Elevate your investment strategy in the Danish business environment!
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
