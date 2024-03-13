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

# Function to fetch and display financial data for two companies for comparison
def fetch_financial_data_for_two_companies(cvr_number1, cvr_number2, year_range):
    # Establish a connection to the database
    conn = get_db_connection()
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # SQL query to select financial data for two companies over the given year range
    query = """
    SELECT cvr, year, profit_loss, equity, return_on_assets
    FROM financials
    WHERE cvr IN (?, ?) AND year BETWEEN ? AND ?
    ORDER BY year, cvr
    """
    # Combine the parameters into a single tuple
    params = (cvr_number1, cvr_number2, year_range[0], year_range[1])
    # Execute the query with the parameters
    cursor.execute(query, params)
    # Fetch all rows of the query result
    return cursor.fetchall()

# Main function to run the Streamlit dashboard
def run_dashboard():
    # Apply custom CSS styles to the Streamlit app
    apply_custom_css()
    # Create a sidebar header for filters
    st.sidebar.header("Filters")
    # Retrieve and display sector choices in the sidebar
    sectors = get_sector_choices()
    sector_choice = st.sidebar.selectbox("Select Sector", sectors, format_func=lambda x: sector_mappings.get(x, x))

    # Get the available year range from the database
    min_year, max_year = get_year_range()
    # Allow the user to select a start year within the range
    start_year = st.sidebar.text_input("Start Year", value=str(min_year))
    # Allow the user to select an end year within the range
    end_year = st.sidebar.text_input("End Year", value=str(max_year))

    # Attempt to convert the selected year range to integers
    try:
        selected_start_year = int(start_year)
        selected_end_year = int(end_year)
    except ValueError:
        # Display an error message if the conversion fails and revert to the full range
        st.sidebar.error("Please enter valid years")
        selected_start_year, selected_end_year = min_year, max_year
        
    # Map the selected sector choice to its code
    sector_code = next(code for code, name in sector_mappings.items() if name == sector_choice)
    
    # Display the main header for the dashboard
    st.header("Investor Dashboard")
    # Create a sidebar selection box for different data views
    view_data = st.sidebar.selectbox("View Data", ["Financial Trends", "Financial Health Indicators", "Sector Comparison", "Company Analysis", "Company to Company Comparison", "Company Information"])

    # Handle different data views based on the user's selection
    if view_data == "Financial Trends":
        # Fetch and display financial trends for the selected sector and year range
        trends_data = fetch_financial_trends(sector_choice, (selected_start_year, selected_end_year))
        if trends_data:
            # Convert the fetched data into a DataFrame
            trends_df = pd.DataFrame(trends_data, columns=['Year', 'Average Profit/Loss', 'Average Equity'])
            # Create a line chart for the financial trends
            fig = px.line(trends_df, x='Year', y=['Average Profit/Loss', 'Average Equity'], title = f'Financial Trends for the {sector_choice}' sector, markers=True)
            # Configure chart axes and layout
            fig.update_xaxes(title_text='Year')
            fig.update_yaxes(title_text='Values in DKK', tickprefix="DKK")
            fig.update_layout(legend_title_text='Metric')
            # Display the chart in the Streamlit app
            st.plotly_chart(fig, use_container_width=True)
            
            # Display a detailed explanation of the financial trends
            st.markdown(f"""
            The Financial Trends graph above displays the average profit/loss and equity for the {sector_choice} sector over the selected period from {selected_start_year} to {selected_end_year}. These trends offer insights into the financial trajectory and stability of the sector.
            
            - **Average Profit/Loss:** This measure indicates the overall profitability of the sector. Positive values represent a net profit, while negative values indicate a net loss. Trends in this metric can show whether the sector is becoming more or less profitable over time.
            
            - **Average Equity:** This represents the net value of the sector, calculated as assets minus liabilities. It reflects the amount that would be returned to shareholders if all assets were liquidated and all debts repaid. Changes in average equity can indicate growth, stability, or decline in the sector's financial health.
            
            By analyzing these trends, you, as an investor, can better assess how well the sector is doing financially and how stable it is over time. This information is crucial for making informed choices about where to invest your money and how to plan your financial strategy effectively.
            """)
        else:
            # Display a message if no financial trends data is available
            st.write("No financial trends available for the selected sector and year range.")
    
    elif view_data == "Financial Health Indicators":
        # Fetch and display financial health indicators for the selected sector and year range
        health_data = fetch_financial_health_indicators(sector_choice, (selected_start_year, selected_end_year))
        if health_data:
            # Convert the fetched data into a DataFrame
            health_df = pd.DataFrame(health_data, columns=['Year', 'Average ROA', 'Average ROI', 'Average Solvency Ratio'])
            # Create a line chart for the financial health indicators
            fig = px.line(health_df, x='Year', y=['Average ROA', 'Average ROI', 'Average Solvency Ratio'], title=f'Financial Health Indicators for the {sector_choice} sector', markers=True)
            # Configure chart axes and layout
            fig.update_xaxes(title_text='Year')
            fig.update_yaxes(title_text='Ratio/Percentage', tickprefix="DKK")
            fig.update_layout(legend_title_text='Indicator')
            # Display the chart in the Streamlit app
            st.plotly_chart(fig, use_container_width=True)
            
            # Display a detailed explanation of the financial health indicators
            st.markdown(f"""
            The graph above presents the financial health indicators for the {sector_choice} sector over the selected period from {selected_start_year} to {selected_end_year}. These indicators provide insights into the sector's financial stability and performance. 

            - **Return on Assets (ROA):** This ratio indicates how efficiently a sector is generating profit from its assets. A higher ROA suggests that the sector is using its assets more effectively to produce profit.
            - **Return on Investment (ROI):** This measures the gain or loss generated on an investment relative to the amount of money invested. It gives an idea of the profitability of the investments in the sector.
            - **Solvency Ratio:** This ratio indicates the sector's ability to meet its long-term obligations. A higher solvency ratio suggests that the sector is more capable of sustaining operations in the long term.

            These metrics together provide a comprehensive view of the sector’s financial health and operational efficiency.
            """)
        else:
            # Display a message if no financial health data is available
            st.write("No financial health data available for the selected sector and year range.")
                
    elif view_data == "Sector Comparison":
        # Fetch and display a list of companies in the selected sector for comparison
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            # Allow the user to select a company from the list for comparison
            selected_company_tuple = st.sidebar.selectbox("Select a Company for Comparison", companies, format_func=lambda x: x[1])
            # Extract the CVR number and name of the selected company
            cvr_number = selected_company_tuple[0]
            company_name = selected_company_tuple[1]
            # Get the full name of the selected sector for display
            sector_name = sector_mappings.get(sector_code, "Selected Sector")
            
            # Display comparison data when the user clicks the 'Compare with Sector' button
            if st.sidebar.button('Compare with Sector'):
                display_sector_comparison(cvr_number, sector_code, (selected_start_year, selected_end_year), company_name, sector_name)
        else:
            # Display a message if no companies are available for comparison in the selected sector
            st.write("No companies available in the selected sector.")
            
    elif view_data == "Company Analysis":
        # Fetch and display a list of companies in the selected sector for analysis
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            # Allow the user to select a company from the list for analysis
            selected_company = st.sidebar.selectbox("Select a Company for Analysis", companies, format_func=lambda x: x[1])
            # Extract the CVR number of the selected company
            cvr_number = selected_company[0]
            
            # Display financial data for the selected company when the user clicks the 'Show Financial Data' button
            if st.sidebar.button('Show Financial Data'):
                company_data = fetch_company_financial_history(cvr_number, (selected_start_year, selected_end_year))
                if company_data:
                    # Convert the fetched data into a DataFrame
                    df = pd.DataFrame(company_data, columns=['Year', 'Profit/Loss (DKK)', 'Equity', 'ROA'])
                    
                    # Create and display a line chart for the company's profit/loss history
                    profit_loss_fig = px.line(df, x='Year', y='Profit/Loss (DKK)', title=f'Profit/Loss of {selected_company[1]}')
                    st.plotly_chart(profit_loss_fig, use_container_width=True)

                    # Create and display a line chart for the company's equity history
                    equity_fig = px.line(df, x='Year', y='Equity', title=f'Equity of {selected_company[1]}')
                    st.plotly_chart(equity_fig, use_container_width=True)

                    # Create and display a line chart for the company's ROA history
                    roa_fig = px.line(df, x='Year', y='ROA', title=f'Return on Assets (ROA) of {selected_company[1]}')
                    st.plotly_chart(roa_fig, use_container_width=True)
                    
                    # Display a detailed explanation of the company's financial analysis
                    st.markdown(f"""
                    The financial analysis of **{selected_company[1]}** shows the annual Profit/Loss (DKK), Equity, and Return on Assets (ROA). These metrics are crucial for assessing the company's financial health and operational efficiency.
                
                    - **Profit/Loss** provides insight into the company's profitability and financial performance.
                    - **Equity** indicates the company's net value, reflecting its financial stability.
                    - **ROA** measures how efficiently the company's assets are used to generate profit.
                    
                    This comprehensive financial overview helps in making informed investment decisions.
                    """)   
                else:
                    # Display a message if no financial data is available for the selected company
                    st.write("No financial data available for the selected company.")
                
    elif view_data == "Company to Company Comparison":
        # Fetch and display a list of companies in the selected sector for comparison
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            # Create a list of company options for comparison
            company_options = [(cvr, name) for cvr, name in companies]
            # Allow the user to select the first company for comparison
            cvr_number1, company_name1 = st.sidebar.selectbox("Select the first company for comparison", company_options, format_func=lambda x: x[1])
            # Allow the user to select the second company for comparison
            cvr_number2, company_name2 = st.sidebar.selectbox("Select the second company for comparison", company_options, format_func=lambda x: x[1])

            # Display comparison data when the user clicks the 'Compare Companies' button
            if st.sidebar.button('Compare Companies'):
                comparison_data = fetch_financial_data_for_two_companies(cvr_number1, cvr_number2, (selected_start_year, selected_end_year))
                if comparison_data:
                    # Convert the fetched data into a DataFrame and add a 'Company' column for identification
                    df = pd.DataFrame(comparison_data, columns=['CVR', 'Year', 'Profit/Loss (DKK)', 'Equity', 'ROA'])
                    df['Company'] = df['CVR'].map({cvr_number1: company_name1, cvr_number2: company_name2})
                    
                    # Create and display bar charts for financial comparison between the two companies
                    for metric in ['Profit/Loss (DKK)', 'Equity', 'ROA']:
                        fig = px.bar(df, x='Company', y=metric, barmode='group', color='Company', title=f'{metric} Comparison for {company_name1} vs {company_name2}')
                        fig.update_xaxes(title_text='Company')
                        fig.update_yaxes(title_text=metric)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Display a detailed explanation of the company-to-company financial comparison
                    st.markdown(f"""
                    Comparing **{company_name1}** and **{company_name2}** provides a side-by-side view of their financial performance. This comparison includes Profit/Loss, Equity, and Return on Assets (ROA), key metrics that highlight each company's financial strengths and weaknesses.
                    - **Profit/Loss** comparison reveals which company is more profitable.
                    - **Equity** comparison shows the financial stability and net value of each company.
                    - **ROA** comparison indicates how effectively each company uses its assets to generate profit.
                    
                    This information aids in making strategic investment decisions, identifying which company presents a better financial profile.
                    """)
                else:
                    # Display a message if no data is available for the selected companies
                    st.write("No data available for the selected companies.")
                    
    elif view_data == "Company Information":
        # Fetch and display a list of companies in the selected sector for information viewing
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            # Create a list of company options for information viewing
            company_options = [(cvr, name) for cvr, name in companies]
            # Allow the user to select a company for viewing its information
            selected_company = st.sidebar.selectbox("Select a company", company_options, format_func=lambda x: x[1], key="company_info")
            # Extract the CVR number of the selected company
            selected_cvr = selected_company[0]

            # Display the information for the selected company
            display_company_info(selected_cvr)
        else:
            # Display a message if no companies are available in the selected sector
            st.write("No companies available in the selected sector.")
