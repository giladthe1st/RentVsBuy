import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("Rent vs. Buy Calculator")
st.write("Compare the financial implications of renting versus buying a home")

# Common inputs
annual_income = st.number_input(
    "Annual Household Income ($)",
    min_value=0,
    max_value=1000000,
    value=100000,
    step=1000,
    help="Total yearly household income before taxes"
)

# Create two columns for the layout
col1, col2 = st.columns(2)

# Purchase-related inputs in left column
with col1:
    st.header("Purchase Options")
    house_price = st.number_input(
        "House Price ($)",
        min_value=0,
        max_value=10000000,
        value=500000,
        step=1000,
        help="Enter the total price of the house you're considering"
    )

    interest_rate = st.slider(
        "Mortgage Interest Rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=6.5,
        step=0.1,
        help="Annual mortgage interest rate"
    )

    down_payment = st.slider(
        "Down Payment (%)",
        min_value=0,
        max_value=100,
        value=20,
        help="Percentage of house price as down payment"
    )

    long_term_growth = st.slider(
        "Expected Annual Property Value Growth (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
        help="Expected annual increase in property value"
    )

    maintenance_costs = st.number_input(
        "Annual Maintenance Costs ($)",
        min_value=0,
        max_value=100000,
        value=5000,
        step=100,
        help="Expected yearly maintenance and repairs"
    )

    property_tax = st.slider(
        "Property Tax Rate (%)",
        min_value=0.0,
        max_value=5.0,
        value=1.2,
        step=0.1,
        help="Annual property tax as percentage of home value"
    )

    insurance = st.number_input(
        "Annual Home Insurance ($)",
        min_value=0,
        max_value=50000,
        value=2400,
        step=100,
        help="Yearly home insurance premium"
    )

# Rental and income inputs in right column
with col2:
    st.header("Rental Options")
    monthly_rent = st.number_input(
        "Monthly Rent ($)",
        min_value=0,
        max_value=50000,
        value=2500,
        step=100,
        help="Monthly rental payment"
    )

    monthly_investment = st.number_input(
        "Monthly Investment ($)",
        min_value=0,
        max_value=50000,
        value=0,
        step=100,
        help="Amount you plan to invest monthly while renting"
    )

    investment_return = st.slider(
        "Expected Annual Investment Return (%)",
        min_value=0.0,
        max_value=20.0,
        value=7.0,
        step=0.1,
        help="Expected annual return on investments"
    )

    rent_insurance = st.number_input(
        "Annual Rental Insurance ($)",
        min_value=0,
        max_value=10000,
        value=300,
        step=50,
        help="Yearly rental insurance premium"
    )

    rent_increase = st.slider(
        "Expected Annual Rent Increase (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
        help="Expected yearly increase in rent"
    )

# Add a calculate button
def calculate_purchase_scenario(house_price, down_payment_pct, interest_rate, years,
                              property_tax_rate, maintenance_costs, insurance, appreciation_rate):
    down_payment = house_price * (down_payment_pct / 100)
    loan_amount = house_price - down_payment
    monthly_rate = interest_rate / (100 * 12)
    num_payments = years * 12

    # Calculate monthly mortgage payment (P&I)
    if interest_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    property_values = []
    equity_values = []
    remaining_loan = loan_amount

    for year in range(years):
        # Calculate home value with appreciation
        current_home_value = house_price * (1 + appreciation_rate/100)**year

        # Calculate yearly costs
        yearly_tax = current_home_value * (property_tax_rate/100)
        yearly_mortgage = monthly_payment * 12
        yearly_costs = yearly_tax + maintenance_costs + insurance

        # Calculate remaining loan balance
        for _ in range(12):
            interest_payment = remaining_loan * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_loan = max(0, remaining_loan - principal_payment)

        # Calculate equity (home value minus remaining loan)
        equity = current_home_value - remaining_loan

        property_values.append(current_home_value)
        equity_values.append(equity)

    return property_values, equity_values

def calculate_rental_scenario(monthly_rent, monthly_investment, years, rent_increase,
                            investment_return, rent_insurance):
    wealth_values = []
    investment_portfolio = 0

    for year in range(years):
        # Calculate yearly costs
        yearly_rent = monthly_rent * 12 * (1 + rent_increase/100)**year
        yearly_investment = monthly_investment * 12

        # Grow existing investments
        investment_portfolio = investment_portfolio * (1 + investment_return/100)
        # Add new investments
        investment_portfolio += yearly_investment

        # Calculate net wealth (investments minus yearly rental costs)
        current_wealth = investment_portfolio - (yearly_rent + rent_insurance)
        wealth_values.append(current_wealth)

    return wealth_values

if st.button("Calculate Comparison", type="primary"):
    years = 30  # You can make this adjustable if desired

    # Calculate purchase scenario
    property_values, equity_values = calculate_purchase_scenario(
        house_price=house_price,
        down_payment_pct=down_payment,
        interest_rate=interest_rate,
        years=years,
        property_tax_rate=property_tax,
        maintenance_costs=maintenance_costs,
        insurance=insurance,
        appreciation_rate=long_term_growth
    )

    # Calculate rental scenario
    rental_wealth = calculate_rental_scenario(
        monthly_rent=monthly_rent,
        monthly_investment=monthly_investment,
        years=years,
        rent_increase=rent_increase,
        investment_return=investment_return,
        rent_insurance=rent_insurance
    )

    # Create the figure
    fig = go.Figure()

    # Add property value line
    fig.add_trace(go.Scatter(
        x=list(range(years)),
        y=property_values,
        name='Property Value',
        line=dict(color='blue')
    ))

    # Add equity line
    fig.add_trace(go.Scatter(
        x=list(range(years)),
        y=equity_values,
        name='Home Equity',
        line=dict(color='green')
    ))

    # Add rental wealth line
    fig.add_trace(go.Scatter(
        x=list(range(years)),
        y=rental_wealth,
        name='Rental Scenario Wealth',
        line=dict(color='red')
    ))

    fig.update_layout(
        title='Property Value and Home Equity Over Time',
        xaxis_title='Years',
        yaxis_title='Value ($)',
        height=600,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

def calculate_net_worth(monthly_savings, years, interest_rate=0.07):
    net_worth = []
    annual_savings = monthly_savings * 12
    current_worth = 0

    for year in range(years):
        current_worth = (current_worth * (1 + interest_rate)) + annual_savings
        net_worth.append(current_worth)

    return net_worth

def update_graph(data, years):
    if not data or not years:
        return {}

    df = pd.DataFrame(data)

    # Calculate monthly savings for each column
    monthly_savings = {
        'Low': float(df['Low'].iloc[-1]),
        'Medium': float(df['Medium'].iloc[-1]),
        'High': float(df['High'].iloc[-1])
    }

    # Create the figure using plotly
    fig = go.Figure()

    # Calculate net worth over time for each scenario
    for scenario, savings in monthly_savings.items():
        net_worth = calculate_net_worth(savings, years)
        fig.add_trace(go.Scatter(
            x=list(range(years)),
            y=net_worth,
            name=f'{scenario} Income Scenario',
            mode='lines'
        ))

    fig.update_layout(
        title='Projected Net Worth Over Time',
        xaxis_title='Years',
        yaxis_title='Net Worth ($)',
        height=500
    )

    return fig

# Replace the Dash components with Streamlit components
years = st.number_input('Simulation Years:', min_value=1, max_value=50, value=30)

# When you have your data ready, call the function and display the plot
if 'your_data' in locals():  # Replace with your actual data condition
    fig = update_graph(your_data, years)
    st.plotly_chart(fig)