# Import the necessary modules for the application
import sqlite3  # Provides functions to interact with SQLite database
import bcrypt  # Used for hashing and checking passwords
import streamlit as st  # Main module for creating web application
import os  # Provides functions to interact with the operating system
from styles import apply_custom_css  # Custom function to apply CSS styles

# Define a dictionary that maps sector codes to their full names
sector_mappings = {
    'A': 'Agriculture, hunting, forestry and fishing',
    'B': 'Raw material extraction',
    'C': 'Manufacturing',
    'D': 'Electricity, gas and district heating supply',
    'E': 'Water supply; sewage system, waste management and cleaning of soil and groundwater',
    'F': 'Building and construction business',
    'G': 'Wholesale and retail trade; repair of motor vehicles and motorcycles',
    'H': 'Transport and cargo handling',
    'I': 'Accommodation facilities and restaurant business',
    'J': 'Information and communication',
    'K': 'Banking and financial services, insurance',
    'L': 'Real estate',
    'M': 'Liberal, scientific and technical services',
    'N': 'Administrative and support services',
    'O': 'Public administration and defence; social Security',
    'P': 'Teaching',
    'Q': 'Health care and social measures',
    'R': 'Culture, amusements and sports',
    'S': 'Other services',
    'T': 'Private households with hired help; households’ production of goods and services for their own use'
}

def get_db_connection():
    # Create a database connection using the sqlite3 library
    db_path = os.path.join(os.path.dirname(__file__), 'cvr_database.db')  # Determine the path of the database file
    return sqlite3.connect(db_path)  # Connect to the SQLite database at the specified path

def setup_database():
    # Initialize the database and create tables if they don't exist
    conn = get_db_connection()  # Establish a database connection
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")  # Check if the 'users' table exists
    table_exists = cursor.fetchone()  # Retrieve the result of the query

    # If the 'users' table doesn't exist, create it
    if not table_exists:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                sectors TEXT
            )
        """)  # Execute a SQL command to create the 'users' table
    conn.commit()  # Commit the changes to the database

def hash_password(password):
    # Hash a password using bcrypt for secure storage
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Encode and hash the password

def verify_password(stored_password, provided_password):
    # Verify a provided password against the stored hashed password
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)  # Check the provided password against the hashed version

def login_user(username, password):
    # Authenticate a user by checking their credentials against the database
    conn = get_db_connection()  # Establish a database connection
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))  # Retrieve the hashed password for the given username
    user_data = cursor.fetchone()  # Fetch the result of the query

    # If user data is found and the password matches, return True, otherwise False
    return user_data and verify_password(user_data[0], password)  # Verify the provided password against the stored hash

def register_user(username, password, sectors):
    # Register a new user with a hashed password and sectors of interest
    conn = get_db_connection()  # Establish a database connection
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    hashed_password = hash_password(password)  # Hash the provided password
    sectors_str = ';'.join(sectors)  # Convert the list of sectors into a semicolon-separated string

    try:
        cursor.execute("INSERT INTO users (username, password, sectors) VALUES (?, ?, ?)", (username, hashed_password, sectors_str))  # Insert a new record into the 'users' table
        conn.commit()  # Commit the changes to the database
        return True  # Return True if registration is successful
    except sqlite3.IntegrityError:
        return False  # Return False if there is a database error (e.g., username already exists)

def toggle_view():
    # Toggle the view between login and registration on the Streamlit interface
    st.session_state['show_login'] = not st.session_state['show_login']  # Switch between True and False in session state

def run_auth_page():
    # Main function to run the authentication page in the Streamlit app
    apply_custom_css()  # Apply custom CSS styles to the Streamlit interface
    setup_database()  # Ensure the database is set up and ready to use

    # Check if the login form should be shown or not
    if st.session_state.show_login:
        # Display the login form
        with st.form("login_form"):
            st.write("## Login")  # Section title
            login_username = st.text_input("Username", key="login_username")  # Username input
            login_password = st.text_input("Password", type="password", key="login_password")  # Password input
            submit_login = st.form_submit_button("Login")  # Login button

            # Process the login form
            if submit_login and login_user(login_username, login_password):
                st.session_state.logged_in = True  # Set the session state to logged in
                st.session_state.username = login_username  # Store the username in the session state
                st.success(f"Welcome back, {login_username}!")  # Welcome message
                st.rerun()  # Rerun the app to update the state
            elif submit_login:
                st.error("Invalid username or password.")  # Show error on failed login

        # Registration button to switch to the registration form
        if st.button("Register"):
            toggle_view()  # Switch to the registration form when the button is clicked
    else:
        # Display the registration form
        with st.form("register_form"):
            st.write("## Register New Account")  # Section title
            reg_username = st.text_input("Username", key="reg_username")  # Username input for registration
            reg_password = st.text_input("Password", type="password", key="reg_password")  # Password input for registration
            selected_sectors = st.multiselect(
                "Select sectors of interest:", 
                options=list(sector_mappings.values()), 
                key='reg_sectors'
            )  # Multiselect for choosing sectors of interest
            submit_register = st.form_submit_button("Register")  # Registration button

            # Process the registration form
            if submit_register and register_user(reg_username, reg_password, list(selected_sectors)):
                st.session_state.logged_in = True  # Set the session state to logged in
                st.session_state.username = reg_username  # Store the new username in the session state
                st.success("Registration successful. Logging you in...")  # Success message
                st.rerun()  # Rerun the app to update the state
            elif submit_register:
                st.error("Username already exists. Please try a different one.")  # Show error on failed registration
