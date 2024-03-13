import sqlite3
import bcrypt
import streamlit as st
import os
from styles import apply_custom_css

# Define sector mappings
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
    # Assuming your database file is in the root directory of your project
    db_path = os.path.join(os.path.dirname(__file__), 'cvr_database.db')
    return sqlite3.connect(db_path)

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the 'users' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()

    # If the table exists and you want to reset it, uncomment the following lines
    # if table_exists:
    #     cursor.execute("DROP TABLE users")

    # Create the 'users' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            sectors TEXT
        )
    """)
    conn.commit()

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    return user_data and verify_password(user_data[0], password)

def register_user(username, password, sectors):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    sectors_str = ';'.join(sectors)
    try:
        cursor.execute("INSERT INTO users (username, password, sectors) VALUES (?, ?, ?)", (username, hashed_password, sectors_str))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def toggle_view():
    st.session_state['show_login'] = not st.session_state['show_login']

def run_auth_page():
    apply_custom_css()
    setup_database()  # Ensure the database table is set up
    if st.session_state.show_login:
        with st.form("login_form"):
            st.write("## Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login and login_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}!")
                st.rerun()
            elif submit_login:
                st.error("Invalid username or password.")

        if st.button("Register"):
            toggle_view()

    else:
        with st.form("register_form"):
            st.write("## Register New Account")
            reg_username = st.text_input("Username", key="reg_username")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            selected_sectors = st.multiselect(
                "Select sectors of interest:", 
                options=list(sector_mappings.values()), 
                key='reg_sectors'
            )
            submit_register = st.form_submit_button("Register")
            
            if submit_register and register_user(reg_username, reg_password, list(selected_sectors)):
                st.session_state.logged_in = True
                st.session_state.username = reg_username
                st.success("Registration successful. Logging you in...")
                st.rerun()
            elif submit_register:
                st.error("Username already exists. Please try a different one.")
