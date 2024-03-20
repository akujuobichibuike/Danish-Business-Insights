# Import the required libraries and modules
import streamlit as st  # Used for creating the web app interface
import sqlite3  # Used for SQLite database operations
import plotly.express as px  # Used for creating interactive charts
import pandas as pd  # Used for data manipulation and analysis
from styles import apply_custom_css  # Custom function to apply CSS styling
import os  # Used for interacting with the file system

# Define a dictionary to map sector codes to their full names for better readability
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

# Function to establish a connection with the SQLite database
def get_db_connection():
    # Build the path to the database file using the current file location
    db_path = os.path.join(os.path.dirname(__file__), 'cvr_database.db')
    # Connect to the SQLite database and return the connection object
    return sqlite3.connect(db_path)

# Function to set up the database by creating necessary tables if they don't exist
def setup_database():
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # SQL query to check if the 'users' table exists in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    # Fetch the result of the query
    table_exists = cursor.fetchone()

    # Uncomment below lines to drop the 'users' table if it exists (optional, based on requirements)
    # if table_exists:
    #     cursor.execute("DROP TABLE users")

    # SQL query to create the 'users' table if it does not already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            sectors TEXT
        )
    """)
    # Commit the changes to the database
    conn.commit()

# Function to retrieve a list of sector choices from the sector_mappings dictionary
def get_sector_choices():
    # Return the values (sector names) from the sector_mappings dictionary as a list
    return list(sector_mappings.values())

# Function to get the range of years from the 'financials' table in the database
def get_year_range():
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Execute a SQL query to find the minimum and maximum year in the 'financials' table
    cursor.execute("SELECT MIN(year), MAX(year) FROM financials")
    # Fetch the result of the query
    min_year, max_year = cursor.fetchone()
    # Return the minimum and maximum year
    return min_year, max_year

# Function to fetch a list of companies in a given sector
def fetch_companies_in_sector(sector_code):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # SQL query to select companies from a specific sector, ordered by name
    query = """
    SELECT cvr_number, name
    FROM company
    WHERE industry_sector = ?
    ORDER BY name
    """
    # Execute the query with the sector_code as a parameter
    cursor.execute(query, (sector_code,))
    # Fetch all rows of the query result
    return cursor.fetchall()

# Function to fetch financial trends for a given sector and year range
def fetch_financial_trends(sector_name, year_range):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Find the sector code corresponding to the sector name
    sector_code = next(code for code, name in sector_mappings.items() if name == sector_name)
    # SQL query to select the average profit/loss and equity for each year in the given sector and year range
    query = """
    SELECT f.year, AVG(f.profit_loss) AS average_profit_loss, AVG(f.equity) AS average_equity
    FROM financials f
    JOIN company c ON f.cvr = c.cvr_number
    WHERE c.industry_sector = ? AND f.year BETWEEN ? AND ?
    GROUP BY f.year
    ORDER BY f.year
    """
    # Execute the query with sector_code, start year, and end year as parameters
    cursor.execute(query, (sector_code, year_range[0], year_range[1]))
    # Fetch all rows of the query result
    return cursor.fetchall()

# Function to fetch financial health indicators for a given sector and year range
def fetch_financial_health_indicators(sector_name, year_range):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Find the sector code corresponding to the sector name
    sector_code = next(code for code, name in sector_mappings.items() if name == sector_name)
    # SQL query to select average return on assets, return on investment, and solvency ratio for each year in the given sector and year range
    query = """
    SELECT 
        f.year, 
        AVG(f.return_on_assets) AS average_roa, 
        AVG(f.return_on_investment) AS average_roi, 
        AVG(f.solvency_ratio) AS average_solvency_ratio
    FROM financials f
    JOIN company c ON f.cvr = c.cvr_number
    WHERE c.industry_sector = ? AND f.year BETWEEN ? AND ?
    GROUP BY f.year
    ORDER BY f.year
    """
    # Execute the query with sector_code, start year, and end year as parameters
    cursor.execute(query, (sector_code, year_range[0], year_range[1]))
    # Fetch all rows of the query result
    return cursor.fetchall()

# Function to fetch the financial history of a specific company given its CVR number and a year range
def fetch_company_financial_history(cvr_number, year_range):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # SQL query to select year, profit/loss, equity, and return on assets for the given company and year range
    query = """
    SELECT year, profit_loss, equity, return_on_assets
    FROM financials
    WHERE cvr = ? AND year BETWEEN ? AND ?
    ORDER BY year
    """
    # Combine the CVR number and year range into a single tuple for the query parameters
    params = (cvr_number,) + year_range
    # Execute the query with the parameters
    cursor.execute(query, params)
    # Fetch all rows of the query result
    return cursor.fetchall()

# Function to display detailed information for a selected company using its CVR number
def display_company_info(cvr_number):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # SQL queries to select basic and financial information for the given company
    company_query = "SELECT name, industry_sector, email, phone_number, establishment_date, purpose FROM company WHERE cvr_number = ?"
    financial_query = "SELECT profit_loss, equity, return_on_assets, solvency_ratio FROM financials WHERE cvr = ? ORDER BY year DESC LIMIT 1"
    
    # Execute the queries
    cursor.execute(company_query, (cvr_number,))
    company_data = cursor.fetchone()
    
    cursor.execute(financial_query, (cvr_number,))
    financial_data = cursor.fetchone()
    
    # Check and display company data if available
    if company_data:
        # Unpack the company data into variables
        name, sector, email, phone, establishment_date, purpose = company_data
        # Display company information using Streamlit functions
        st.subheader(f'Company Information')
        st.markdown(f"**Company Name:** {name or 'Not provided'}")
        st.markdown(f"**Sector:** {sector_mappings.get(sector, 'Unknown Sector')}")
        st.markdown(f"**Establishment Date:** {establishment_date or 'Not available'}")
        st.markdown(f"**Company Purpose:** {purpose or 'Not provided'}")
        st.markdown(f"**Email:** {email or 'Not provided'}")
        st.markdown(f"**Phone Number:** {phone or 'Not provided'}")
    else:
        # Display error message if company data is not available
        st.error("Company information not available.")
    
    # Check and display financial data if available
    if financial_data:
        # Unpack the financial data into variables
        profit_loss, equity, roa, solvency_ratio = financial_data
        # Display financial information using Streamlit functions
        st.subheader("Financial Information (Most Recent Year)")
        st.metric("Profit/Loss", f"{profit_loss} DKK")
        st.metric("Equity", f"{equity} DKK")
        st.metric("Return on Assets", f"{roa * 100}%", delta_color="off")
        st.metric("Solvency Ratio", f"{solvency_ratio * 100}%", delta_color="off")
    else:
        # Display error message if financial data is not available
        st.error("Financial information not available.")

# Function to display a comparison of financial performance between a selected company and its sector
def display_sector_comparison(cvr_number, sector_code, year_range, company_name, sector_name):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # SQL queries to select financial data for the given company and its sector
    company_query = """
    SELECT year, profit_loss, equity, return_on_assets 
    FROM financials 
    WHERE cvr = ? AND year BETWEEN ? AND ? 
    ORDER BY year
    """
    sector_query = """
    SELECT year, AVG(profit_loss) AS avg_profit_loss, AVG(equity) AS avg_equity, AVG(return_on_assets) AS avg_roa 
    FROM financials f 
    JOIN company c ON f.cvr = c.cvr_number 
    WHERE c.industry_sector = ? AND f.year BETWEEN ? AND ? 
    GROUP BY f.year
    """
    
    # Execute the queries
    cursor.execute(company_query, (cvr_number, year_range[0], year_range[1]))
    company_data = cursor.fetchall()
    
    cursor.execute(sector_query, (sector_code, year_range[0], year_range[1]))
    sector_data = cursor.fetchall()

    # Check if data is available for both the company and its sector
    if company_data and sector_data:
        # Convert the query results to pandas DataFrames
        company_df = pd.DataFrame(company_data, columns=['Year', 'Profit/Loss', 'Equity', 'ROA'])
        sector_df = pd.DataFrame(sector_data, columns=['Year', 'Avg Profit/Loss', 'Avg Equity', 'Avg ROA'])

        # Merge the DataFrames for comparison
        combined_df = company_df.merge(sector_df, on='Year', suffixes=('', ' Avg'))
        
        # Create a line chart comparing the company and sector financials
        fig = px.line(combined_df, x='Year', y=['Profit/Loss', 'Avg Profit/Loss', 'Equity', 'Avg Equity', 'ROA', 'Avg ROA'], 
                      title=f"{company_name} vs {sector_name} Sector Financial Performance")
        # Set chart axis titles
        fig.update_xaxes(title_text='Year')
        fig.update_yaxes(title_text='Financial Metrics')
        # Set the legend title
        fig.update_layout(legend_title_text='Metric')
        # Display the chart in the Streamlit app
        st.plotly_chart(fig, use_container_width=True)

        # Display a detailed explanation of the comparison
        st.markdown(f"""
        The graph compares the financial performance of **{company_name}** against the average of the **{sector_name}** sector from {year_range[0]} to {year_range[1]}. This comparison includes key financial metrics: Profit/Loss, Equity, and Return on Assets (ROA).

        - **Profit/Loss** shows the net income or net loss of the company compared to the sector average, indicating profitability.
        - **Equity** reflects the net value of the company versus the sector, representing financial stability.
        - **ROA** compares how effectively the company and sector utilize assets to generate profit.

        This analysis helps investors understand how the selected company stands against the broader sector performance, providing insights for investment decisions.
        """)
    else:
        # Display a message if no data is available for comparison
        st.write(f"No data available for {company_name} or {sector_name} sector.")

def style_dataframe(df):
    # Apply styling only to numerical columns
    numerical_columns = ['Profit/Loss (DKK)', 'Equity', 'ROA']  # Update this list with your numerical columns
    
    # Define a function to apply conditional styling
    def apply_styling(value):
        if isinstance(value, (int, float)):  # Check if the value is numeric
            # Use a deeper shade of red for negative and green for positive
            return f'background-color: {"#ff4d4d" if value < 0 else "#29a329"}'
        return ''  # Return an empty string for non-numeric values
    
    # Apply the styling function to the DataFrame and format the numbers
    styled = df.style.applymap(apply_styling, subset=numerical_columns).format({
        'Profit/Loss (DKK)': "{:,.0f} DKK",  # Format with comma as thousands separator and no decimal places
        'Equity': "{:,.0f} DKK",  # Same formatting for Equity
        'ROA': "{:.2%}"  # Format ROA as percentage with two decimal places
    })
    
    return styled  

def style_hidden_gems_dataframe(df):
    # Apply styling only to numerical columns that exist in the DataFrame
    numerical_columns = ['Profit/Loss', 'Equity']  # Adjust based on actual data columns
    
    # Define a function to apply conditional styling
    def apply_styling(value):
        if isinstance(value, (int, float)):  # Check if the value is numeric
            return f'background-color: {"#ff4d4d" if value < 0 else "#29a329"}'  # Deeper shades for negative and positive
        return ''
    
    # Apply the styling function to the DataFrame and format the numbers
    styled = df.style.applymap(apply_styling, subset=numerical_columns).format({
        'Profit/Loss': "{:,.0f} DKK",  # Format Profit/Loss as currency
        'Equity': "{:,.0f} DKK",  # Format Equity as currency
    })
    
    return styled

# Function to fetch and display financial data for multi-company comparison
def fetch_financial_data_for_companies(cvr_numbers, year_range):
    # Ensure cvr_numbers is a list
    if not isinstance(cvr_numbers, list):
        cvr_numbers = [cvr_numbers]

    # Now cvr_numbers is guaranteed to be a list, so we can iterate over it
    placeholders = ','.join('?' * len(cvr_numbers))  # Create a placeholder for each CVR number

    # Your existing code to fetch data from the database...
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"""
    SELECT f.cvr, f.year, f.profit_loss, f.equity, f.return_on_assets
    FROM financials f
    INNER JOIN (
        SELECT cvr, MAX(year) AS recent_year
        FROM financials
        WHERE cvr IN ({placeholders}) AND year BETWEEN ? AND ?
        GROUP BY cvr
    ) AS recent_f ON f.cvr = recent_f.cvr AND f.year = recent_f.recent_year
    """
    params = cvr_numbers + list(year_range)
    cursor.execute(query, params)
    return cursor.fetchall()

# Function for finding hidding gems
def get_hidden_gems(sector_code, year_range):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT
        c.name AS 'Company Name',
        f.cvr AS 'CVR',
        MAX(f.year) AS 'Recent Year',
        f.profit_loss AS 'Profit/Loss',
        f.equity AS 'Equity',
        f.solvency_ratio AS 'Solvency Ratio'
    FROM financials f
    JOIN company c ON f.cvr = c.cvr_number
    WHERE c.industry_sector = ? AND f.year BETWEEN ? AND ?
    GROUP BY f.cvr
    HAVING COUNT(f.year) >= 5 AND f.solvency_ratio > 0.2 AND f.profit_loss < 0
    ORDER BY f.profit_loss
    """
    cursor.execute(query, (sector_code, year_range[0], year_range[1]))
    return cursor.fetchall()

# Main function to run the Streamlit dashboard
# Main Function for the App
def run_dashboard():
    apply_custom_css()
    st.sidebar.header("Filters 🔍")
    sectors = get_sector_choices()
    sector_choice = st.sidebar.selectbox("Select Sector", sectors, format_func=lambda x: sector_mappings.get(x, x))

    min_year, max_year = get_year_range()
    start_year = st.sidebar.text_input("Start Year", value=str(min_year))
    end_year = st.sidebar.text_input("End Year", value=str(max_year))

    try:
        selected_start_year = int(start_year)
        selected_end_year = int(end_year)
    except ValueError:
        st.sidebar.error("Please enter valid years")
        selected_start_year, selected_end_year = min_year, max_year
        
    sector_code = next(code for code, name in sector_mappings.items() if name == sector_choice)  # Convert sector name to code
    
    st.header("Investor Dashboard")
    view_data = st.sidebar.selectbox("View Data", ["Financial Trends Analysis 📊", "Financial Health Indicators 💪", "Sector Comparison ⚖️", "Company Analysis 🔎", "Multi-Company Comparison 🤝", "Company Information 🛈", "Hidden Gems: Profit Dips & Financial Strength 🌟"])

    if view_data == "Financial Trends Analysis 📊":
        st.header('Financial Trends Analysis')
        trends_data = fetch_financial_trends(sector_choice, (selected_start_year, selected_end_year))
        if trends_data:
            trends_df = pd.DataFrame(trends_data, columns=['Year', 'Average Profit/Loss', 'Average Equity'])
            fig = px.line(trends_df, x='Year', y=['Average Profit/Loss', 'Average Equity'], title = f'Financial Trends for {sector_choice}', markers=True)
            fig.update_xaxes(title_text='Year')
            fig.update_yaxes(title_text='Values in DKK', tickprefix="DKK")
            fig.update_layout(legend_title_text='Metric')
            st.plotly_chart(fig, use_container_width=True)
            
            # Explanation text
            st.markdown(f"""
            The Financial Trends Analysis graph above displays the average profit/loss and equity for the {sector_choice} sector over the selected period from {selected_start_year} to {selected_end_year}. These trends offer insights into the financial trajectory and stability of the sector.
            
            - **Average Profit/Loss:** This measure indicates the overall profitability of the sector. Positive values represent a net profit, while negative values indicate a net loss. Trends in this metric can show whether the sector is becoming more or less profitable over time.
            
            - **Average Equity:** This represents the net value of the sector, calculated as assets minus liabilities. It reflects the amount that would be returned to shareholders if all assets were liquidated and all debts repaid. Changes in average equity can indicate growth, stability, or decline in the sector's financial health.
            
            By analyzing these trends, you, as an investor, can better assess how well the sector is doing financially and how stable it is over time. This information is crucial for making informed choices about where to invest your money and how to plan your financial strategy effectively.
            """)
        else:
            st.write("No financial trends available for the selected sector and year range.")
    
    elif view_data == "Financial Health Indicators 💪":
        st.header('Financial Health Indicators')
        health_data = fetch_financial_health_indicators(sector_choice, (selected_start_year, selected_end_year))
        if health_data:
            health_df = pd.DataFrame(health_data, columns=['Year', 'Average ROA', 'Average ROI', 'Average Solvency Ratio'])
            fig = px.line(health_df, x='Year', y=['Average ROA', 'Average ROI', 'Average Solvency Ratio'], title=f'Financial Health Indicators of {sector_choice}', markers=True)
            fig.update_xaxes(title_text='Year')
            fig.update_yaxes(title_text='Ratio/Percentage', tickprefix="DKK")
            fig.update_layout(legend_title_text='Indicator')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            The graph above presents the financial health indicators for the {sector_choice} sector over the selected period from {selected_start_year} to {selected_end_year}. These indicators provide insights into the sector's financial stability and performance. 

            - **Return on Assets (ROA):** This ratio indicates how efficiently a sector is generating profit from its assets. A higher ROA suggests that the sector is using its assets more effectively to produce profit.
            - **Return on Investment (ROI):** This measures the gain or loss generated on an investment relative to the amount of money invested. It gives an idea of the profitability of the investments in the sector.
            - **Solvency Ratio:** This ratio indicates the sector's ability to meet its long-term obligations. A higher solvency ratio suggests that the sector is more capable of sustaining operations in the long term.

            These metrics together provide a comprehensive view of the sector’s financial health and operational efficiency.
            """)
        else:
            st.write("No financial health data available for the selected sector and year range.")
                
    elif view_data == "Sector Comparison ⚖️":
        st.header('Sector Comparison')
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            selected_company_tuple = st.sidebar.selectbox("Select a Company for Comparison", companies, format_func=lambda x: x[1])
            cvr_number = selected_company_tuple[0]
            company_name = selected_company_tuple[1]
            sector_name = sector_mappings.get(sector_code, "Selected Sector")
            
            if st.sidebar.button('Compare with Sector'):
                display_sector_comparison(cvr_number, sector_code, (selected_start_year, selected_end_year), company_name, sector_name)
        else:
            st.write("No companies available in the selected sector.")
            
    elif view_data == "Company Analysis 🔎":
        st.header('Company Analysis')
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            selected_company = st.sidebar.selectbox("Select a Company for Analysis", companies, format_func=lambda x: x[1])
            cvr_number = selected_company[0]  # Get the CVR number of the selected company
            
            if st.sidebar.button('Show Financial Data'):
                company_data = fetch_company_financial_history(cvr_number, (selected_start_year, selected_end_year))
                if company_data:
                    df = pd.DataFrame(company_data, columns=['Year', 'Profit/Loss (DKK)', 'Equity', 'ROA'])
                    
                    # Profit/Loss Chart
                    profit_loss_fig = px.line(df, x='Year', y='Profit/Loss (DKK)', title=f'Profit/Loss of {selected_company[1]}')
                    st.plotly_chart(profit_loss_fig, use_container_width=True)

                    # Equity Chart
                    equity_fig = px.line(df, x='Year', y='Equity', title=f'Equity of {selected_company[1]}')
                    st.plotly_chart(equity_fig, use_container_width=True)

                    # ROA Chart
                    roa_fig = px.line(df, x='Year', y='ROA', title=f'Return on Assets (ROA) of {selected_company[1]}')
                    st.plotly_chart(roa_fig, use_container_width=True)
                    
                    # Detailed explanation text
                    st.markdown(f"""
                    The financial analysis of **{selected_company[1]}** shows the annual Profit/Loss (DKK), Equity, and Return on Assets (ROA). These metrics are crucial for assessing the company's financial health and operational efficiency.
                
                    - **Profit/Loss** provides insight into the company's profitability and financial performance.
                    - **Equity** indicates the company's net value, reflecting its financial stability.
                    - **ROA** measures how efficiently the company's assets are used to generate profit.
                    
                    This comprehensive financial overview helps in making informed investment decisions.
                    """)   
                else:
                    st.write("No financial data available for the selected company.")
                
    elif view_data == "Multi-Company Comparison 🤝":
        st.header('Multi-Company Comparison')
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            company_options = [(cvr, name) for cvr, name in companies]
            selected_companies = st.multiselect("Select companies for comparison", company_options, format_func=lambda x: x[1])

            if st.button('Compare Companies'):
                comparison_data = []
                for cvr_number, company_name in selected_companies:
                    company_data = fetch_financial_data_for_companies(cvr_number, (selected_start_year, selected_end_year))
                    for data in company_data:
                        comparison_data.append((company_name,) + data)

                if comparison_data:
                    df = pd.DataFrame(comparison_data, columns=['Company', 'CVR', 'Year', 'Profit/Loss (DKK)', 'Equity', 'ROA'])
                    
                    styled_df = style_dataframe(df)
                    st.dataframe(styled_df)
                    
                    st.markdown("""
                    **Financial Performance Comparison:**
                    
                    The selected companies are compared based on their financial performance metrics such as Profit/Loss, Equity, and Return on Assets (ROA). These metrics highlight the financial strengths and weaknesses of each company, providing insights into their profitability, financial stability, and asset utilization efficiency.
                    
                    This comparative analysis aids investors in making strategic investment decisions, identifying which companies present a better financial profile or show signs of potential recovery or growth.
                    
                    """)
                else:
                    st.write("No data available for the selected companies.")
               
    elif view_data == "Company Information 🛈":
        st.header("Company Information")
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            company_options = [(cvr, name) for cvr, name in companies]
            selected_company = st.sidebar.selectbox("Select a company", company_options, format_func=lambda x: x[1], key="company_info")
            selected_cvr = selected_company[0]  # Assuming selected_company is a tuple (cvr_number, company_name)

            display_company_info(selected_cvr)
        else:
            st.write("No companies available in the selected sector.")
            
    elif view_data == "Hidden Gems: Profit Dips & Financial Strength 🌟":
        st.header("Hidden Gems: Profit Dips & Financial Strength")
        st.markdown(f"""
        **Hidden Gems in {sector_choice}**
    
        Explore companies with solid financials that recently faced profit declines. These hidden gems, poised for a potential rebound, offer intriguing investment opportunities:
    
        - **Company Name:** Identifies the business.
        - **CVR:** Unique business registration number.
        - **Recent Year:** Latest fiscal year analyzed.
        - **Profit/Loss:** Net income or loss, indicating financial shifts.
        - **Equity:** Company's financial stability metric.
        - **Solvency Ratio:** Firm's capacity to fulfil long-term obligations.
    
        Below are the hidden gems from the "{sector_choice}" sector, showcasing strong equity and solvency yet recent profit dips.
        """)
    
        hidden_gems_data = get_hidden_gems(sector_code, (selected_start_year, selected_end_year))
        hidden_gems_df = pd.DataFrame(hidden_gems_data, columns=['Company Name', 'CVR', 'Recent Year', 'Profit/Loss', 'Equity', 'Solvency Ratio'])

        if not hidden_gems_df.empty:
            styled_hidden_gems_df = style_hidden_gems_dataframe(hidden_gems_df)
            st.dataframe(styled_hidden_gems_df)
        else:
            st.write(f"No hidden gems found in the {sector_choice} sector during the specified time frame.")

