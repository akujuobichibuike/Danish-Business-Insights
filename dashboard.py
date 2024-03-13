import streamlit as st
import sqlite3
import plotly.express as px
import pandas as pd
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
    return sqlite3.connect(r"C:\Users\WCLENG-9\Desktop\Odingo Project\cvr_database.db")

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

def get_sector_choices():
    return list(sector_mappings.values())

def get_year_range():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(year), MAX(year) FROM financials")
    min_year, max_year = cursor.fetchone()
    return min_year, max_year

def fetch_companies_in_sector(sector_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT cvr_number, name
    FROM company
    WHERE industry_sector = ?
    ORDER BY name
    """
    cursor.execute(query, (sector_code,))
    return cursor.fetchall()

def fetch_financial_trends(sector_name, year_range):
    conn = get_db_connection()
    cursor = conn.cursor()
    sector_code = next(code for code, name in sector_mappings.items() if name == sector_name)
    query = """
    SELECT f.year, AVG(f.profit_loss) AS average_profit_loss, AVG(f.equity) AS average_equity
    FROM financials f
    JOIN company c ON f.cvr = c.cvr_number
    WHERE c.industry_sector = ? AND f.year BETWEEN ? AND ?
    GROUP BY f.year
    ORDER BY f.year
    """
    cursor.execute(query, (sector_code, year_range[0], year_range[1]))
    return cursor.fetchall()

def fetch_financial_health_indicators(sector_name, year_range):
    conn = get_db_connection()
    cursor = conn.cursor()
    sector_code = next(code for code, name in sector_mappings.items() if name == sector_name)
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
    cursor.execute(query, (sector_code, year_range[0], year_range[1]))
    return cursor.fetchall()

def fetch_company_financial_history(cvr_number, year_range):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT year, profit_loss, equity, return_on_assets
    FROM financials
    WHERE cvr = ? AND year BETWEEN ? AND ?
    ORDER BY year
    """
    params = (cvr_number,) + year_range
    cursor.execute(query, params)
    return cursor.fetchall()

# Displays detailed information for a selected company.
def display_company_info(cvr_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    company_query = "SELECT name, industry_sector, email, phone_number, establishment_date, purpose FROM company WHERE cvr_number = ?"
    financial_query = "SELECT profit_loss, equity, return_on_assets, solvency_ratio FROM financials WHERE cvr = ? ORDER BY year DESC LIMIT 1"
    
    cursor.execute(company_query, (cvr_number,))
    company_data = cursor.fetchone()
    
    cursor.execute(financial_query, (cvr_number,))
    financial_data = cursor.fetchone()
    
    if company_data:
        name, sector, email, phone, establishment_date, purpose = company_data
        st.subheader(f'Company Information')
        st.markdown(f"**Company Name:** {name or 'Not provided'}")
        st.markdown(f"**Sector:** {sector_mappings.get(sector, 'Unknown Sector')}")
        st.markdown(f"**Establishment Date:** {establishment_date or 'Not available'}")
        st.markdown(f"**Company Purpose:** {purpose or 'Not provided'}")
        st.markdown(f"**Email:** {email or 'Not provided'}")
        st.markdown(f"**Phone Number:** {phone or 'Not provided'}")
    else:
        st.error("Company information not available.")
    
    if financial_data:
        profit_loss, equity, roa, solvency_ratio = financial_data
        st.subheader("Financial Information (Most Recent Year)")
        st.metric("Profit/Loss", f"{profit_loss} DKK")
        st.metric("Equity", f"{equity} DKK")
        st.metric("Return on Assets", f"{roa * 100}%", delta_color="off")
        st.metric("Solvency Ratio", f"{solvency_ratio * 100}%", delta_color="off")
    else:
        st.error("Financial information not available.")
        
def display_sector_comparison(cvr_number, sector_code, year_range, company_name, sector_name):
    conn = get_db_connection()
    cursor = conn.cursor()

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
    
    cursor.execute(company_query, (cvr_number, year_range[0], year_range[1]))
    company_data = cursor.fetchall()
    
    cursor.execute(sector_query, (sector_code, year_range[0], year_range[1]))
    sector_data = cursor.fetchall()

    if company_data and sector_data:
        # Assuming the data is in the same order and length
        company_df = pd.DataFrame(company_data, columns=['Year', 'Profit/Loss', 'Equity', 'ROA'])
        sector_df = pd.DataFrame(sector_data, columns=['Year', 'Avg Profit/Loss', 'Avg Equity', 'Avg ROA'])

        # Combine the data for comparison
        combined_df = company_df.merge(sector_df, on='Year', suffixes=('', ' Avg'))
        
        # Plot the comparison
        fig = px.line(combined_df, x='Year', y=['Profit/Loss', 'Avg Profit/Loss', 'Equity', 'Avg Equity', 'ROA', 'Avg ROA'], 
                      title=f"{company_name} vs {sector_name} Sector Financial Performance")
        fig.update_xaxes(title_text='Year')
        fig.update_yaxes(title_text='Financial Metrics')
        fig.update_layout(legend_title_text='Metric')
        st.plotly_chart(fig, use_container_width=True)

        # Detailed explanation text
        st.markdown(f"""
        The graph compares the financial performance of **{company_name}** against the average of the **{sector_name}** sector from {year_range[0]} to {year_range[1]}. This comparison includes key financial metrics: Profit/Loss, Equity, and Return on Assets (ROA).

        - **Profit/Loss** shows the net income or net loss of the company compared to the sector average, indicating profitability.
        - **Equity** reflects the net value of the company versus the sector, representing financial stability.
        - **ROA** compares how effectively the company and sector utilize assets to generate profit.

        This analysis helps investors understand how the selected company stands against the broader sector performance, providing insights for investment decisions.
        """)
    else:
        st.write(f"No data available for {company_name} or {sector_name} sector.")
        
def fetch_financial_data_for_two_companies(cvr_number1, cvr_number2, year_range):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT cvr, year, profit_loss, equity, return_on_assets
    FROM financials
    WHERE cvr IN (?, ?) AND year BETWEEN ? AND ?
    ORDER BY year, cvr
    """
    params = (cvr_number1, cvr_number2, year_range[0], year_range[1])
    cursor.execute(query, params)
    return cursor.fetchall()
        
# Main Function for the App
def run_dashboard():
    apply_custom_css()
    st.sidebar.header("Filters")
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
    view_data = st.sidebar.selectbox("View Data", ["Financial Trends", "Financial Health Indicators", "Sector Comparison", "Company Analysis", "Company to Company Comparison", "Company Information"])

    if view_data == "Financial Trends":
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
            The Financial Trends graph above displays the average profit/loss and equity for the {sector_choice} sector over the selected period from {selected_start_year} to {selected_end_year}. These trends offer insights into the financial trajectory and stability of the sector.
            
            - **Average Profit/Loss:** This measure indicates the overall profitability of the sector. Positive values represent a net profit, while negative values indicate a net loss. Trends in this metric can show whether the sector is becoming more or less profitable over time.
            
            - **Average Equity:** This represents the net value of the sector, calculated as assets minus liabilities. It reflects the amount that would be returned to shareholders if all assets were liquidated and all debts repaid. Changes in average equity can indicate growth, stability, or decline in the sector's financial health.
            
            By analyzing these trends, you, as an investor, can better assess how well the sector is doing financially and how stable it is over time. This information is crucial for making informed choices about where to invest your money and how to plan your financial strategy effectively.
            """)
        else:
            st.write("No financial trends available for the selected sector and year range.")
    
    elif view_data == "Financial Health Indicators":
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
                
    elif view_data == "Sector Comparison":
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
            
    elif view_data == "Company Analysis":
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
                
    elif view_data == "Company to Company Comparison":
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            company_options = [(cvr, name) for cvr, name in companies]
            cvr_number1, company_name1 = st.sidebar.selectbox("Select the first company for comparison", company_options, format_func=lambda x: x[1])
            cvr_number2, company_name2 = st.sidebar.selectbox("Select the second company for comparison", company_options, format_func=lambda x: x[1])

            if st.sidebar.button('Compare Companies'):
                comparison_data = fetch_financial_data_for_two_companies(cvr_number1, cvr_number2, (selected_start_year, selected_end_year))
                if comparison_data:
                    df = pd.DataFrame(comparison_data, columns=['CVR', 'Year', 'Profit/Loss (DKK)', 'Equity', 'ROA'])
                    df['Company'] = df['CVR'].map({cvr_number1: company_name1, cvr_number2: company_name2})
                    
                    for metric in ['Profit/Loss (DKK)', 'Equity', 'ROA']:
                        fig = px.bar(df, x='Company', y=metric, barmode='group', color='Company', title=f'{metric} Comparison for {company_name1} vs {company_name2}')
                        fig.update_xaxes(title_text='Company')
                        fig.update_yaxes(title_text=metric)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Detailed explanation text
                    st.markdown(f"""
                    Comparing **{company_name1}** and **{company_name2}** provides a side-by-side view of their financial performance. This comparison includes Profit/Loss, Equity, and Return on Assets (ROA), key metrics that highlight each company's financial strengths and weaknesses.
                    - **Profit/Loss** comparison reveals which company is more profitable.
                    - **Equity** comparison shows the financial stability and net value of each company.
                    - **ROA** comparison indicates how effectively each company uses its assets to generate profit.
                    
                    This information aids in making strategic investment decisions, identifying which company presents a better financial profile.
                    """)
                else:
                    st.write("No data available for the selected companies.")
                    
    elif view_data == "Company Information":
        companies = fetch_companies_in_sector(sector_code)
        if companies:
            company_options = [(cvr, name) for cvr, name in companies]
            selected_company = st.sidebar.selectbox("Select a company", company_options, format_func=lambda x: x[1], key="company_info")
            selected_cvr = selected_company[0]  # Assuming selected_company is a tuple (cvr_number, company_name)

            display_company_info(selected_cvr)
        else:
            st.write("No companies available in the selected sector.")