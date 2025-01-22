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

years = st.number_input(
    'Simulation Years:',
    min_value=1,
    max_value=50,
    value=30,
    help="Number of years to simulate the comparison"
)

# Create two columns for the layout
col1, col2, col3 = st.columns(3)

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

    # Move payment calculations here, after all inputs are defined
    loan_amount = house_price * (1 - down_payment/100)
    monthly_rate = interest_rate / (100 * 12)
    num_payments = years * 12  # Use years variable instead of hardcoded 30

    if interest_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    # Calculate first month's interest and principal
    first_interest = loan_amount * monthly_rate
    first_principal = monthly_payment - first_interest

    st.markdown("### Monthly Payment Breakdown")
    st.markdown(f"**Total Monthly Payment:** ${monthly_payment:,.2f}")
    st.markdown(f"**First Payment Breakdown:**")
    st.markdown(f"- Principal: ${first_principal:,.2f}")
    st.markdown(f"- Interest: ${first_interest:,.2f}")

    long_term_growth = st.slider(
        "Expected Annual Property Value Growth (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
        help="Expected annual increase in property value"
    )

    maintenance_rate = st.slider(
        "Annual Maintenance Rate (% of Property Value)",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Expected yearly maintenance and repairs as percentage of property value"
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

    monthly_investment_purchase = st.number_input(
        "Monthly Investment ($)",
        min_value=0,
        max_value=50000,
        value=0,
        step=100,
        help="Amount you plan to invest monthly while owning",
        key="purchase_investment"  # unique key to differentiate from rental investment
    )

# Rental and income inputs in right column
with col2:
    st.header("Rental Options")
    initial_investment = st.number_input(
        "Initial Investment ($)",
        min_value=0.0,
        max_value=10000000.0,
        value=float(house_price * down_payment/100),
        step=1000.0,
        help="Initial amount you could invest (equivalent to down payment if buying)"
    )

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
        help="Amount you plan to invest monthly while renting",
        key="rental_investment"  # unique key
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

# New utilities/expenses section in right column
with col3:
    st.header("Monthly Utilities & Expenses")

    st.markdown("### Purchase Scenario")
    electricity_purchase = st.number_input(
        "Electricity ($)",
        min_value=0,
        max_value=1000,
        value=150,
        step=10,
        help="Monthly electricity costs for owned home",
        key="electricity_purchase"
    )

    water_purchase = st.number_input(
        "Water ($)",
        min_value=0,
        max_value=500,
        value=50,
        step=10,
        help="Monthly water costs for owned home",
        key="water_purchase"
    )

    other_expenses_purchase = st.number_input(
        "Other Monthly Expenses ($)",
        min_value=0,
        max_value=1000,
        value=100,
        step=10,
        help="Other monthly housing-related expenses for owned home",
        key="other_purchase"
    )

    st.markdown("### Rental Scenario")
    electricity_rental = st.number_input(
        "Electricity ($)",
        min_value=0,
        max_value=1000,
        value=150,
        step=10,
        help="Monthly electricity costs for rental (0 if included in rent)",
        key="electricity_rental"
    )

    water_rental = st.number_input(
        "Water ($)",
        min_value=0,
        max_value=500,
        value=50,
        step=10,
        help="Monthly water costs for rental (0 if included in rent)",
        key="water_rental"
    )

    other_expenses_rental = st.number_input(
        "Other Monthly Expenses ($)",
        min_value=0,
        max_value=1000,
        value=100,
        step=10,
        help="Other monthly housing-related expenses for rental",
        key="other_rental"
    )

# Add a calculate button
def calculate_purchase_scenario(house_price, down_payment_pct, interest_rate, years,
                              property_tax_rate, maintenance_rate, insurance, appreciation_rate,
                              monthly_investment, investment_return):
    down_payment = house_price * (down_payment_pct / 100)
    loan_amount = house_price - down_payment
    monthly_rate = interest_rate / (100 * 12)
    num_payments = years * 12

    # Initialize investment portfolio
    investment_portfolio = 0

    # Calculate monthly mortgage payment (P&I)
    if interest_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    property_values = []
    equity_values = []
    remaining_loan = loan_amount
    total_costs = []  # Track all costs

    initial_wealth = -down_payment  # Start with negative down payment

    yearly_details = []

    total_interest_to_date = 0
    total_principal_to_date = 0

    for year in range(years):
        # Calculate home value with appreciation
        current_home_value = house_price * (1 + appreciation_rate/100)**year

        # Calculate yearly costs
        yearly_tax = current_home_value * (property_tax_rate/100)
        yearly_maintenance = current_home_value * (maintenance_rate/100)  # Calculate maintenance based on current value
        yearly_mortgage = monthly_payment * 12

        # Calculate interest and principal for the year
        yearly_interest_paid = 0
        yearly_principal_paid = 0
        for _ in range(12):
            interest_payment = remaining_loan * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_loan = max(0, remaining_loan - principal_payment)
            yearly_interest_paid += interest_payment
            yearly_principal_paid += principal_payment

        # Calculate equity (home value minus remaining loan)
        equity = current_home_value - remaining_loan

        # Calculate total yearly costs
        total_yearly_costs = yearly_mortgage + yearly_tax + yearly_maintenance + insurance

        # Update running totals
        total_interest_to_date += yearly_interest_paid
        total_principal_to_date += yearly_principal_paid

        # Calculate investment returns
        yearly_investment = monthly_investment * 12
        investment_returns = investment_portfolio * (investment_return/100)
        investment_portfolio = investment_portfolio * (1 + investment_return/100) + yearly_investment

        yearly_details.append({
            'Year': year + 1,
            'Property_Value': current_home_value,
            'Yearly_Mortgage': yearly_mortgage,
            'Property_Tax': yearly_tax,
            'Maintenance': yearly_maintenance,  # Use the calculated maintenance
            'Insurance': insurance,
            'Interest_Paid': yearly_interest_paid,
            'Principal_Paid': yearly_principal_paid,
            'Remaining_Loan': remaining_loan,
            'Equity': equity,
            'Yearly_Costs': total_yearly_costs,
            'Total_Interest_To_Date': total_interest_to_date,
            'Total_Principal_To_Date': total_principal_to_date,
            'Investment_Portfolio': investment_portfolio,
            'Investment_Returns': investment_returns,
            'New_Investments': yearly_investment,
        })

        property_values.append(current_home_value)
        equity_values.append(equity)

    return property_values, equity_values, yearly_details

def calculate_rental_scenario(monthly_rent, monthly_investment, years, rent_increase,
                            investment_return, rent_insurance, initial_investment=0):
    wealth_values = []
    investment_portfolio = initial_investment  # Start with initial investment
    yearly_details = []

    for year in range(years):
        # Calculate yearly costs
        yearly_rent = monthly_rent * 12 * (1 + rent_increase/100)**year
        yearly_investment = monthly_investment * 12
        yearly_costs = yearly_rent + rent_insurance

        # Grow existing investments
        investment_returns = investment_portfolio * (investment_return/100)
        investment_portfolio = investment_portfolio * (1 + investment_return/100)
        # Add new investments
        investment_portfolio += yearly_investment

        # Net wealth is just the investment portfolio
        current_wealth = investment_portfolio

        wealth_values.append(current_wealth)

        yearly_details.append({
            'Year': year + 1,
            'Yearly_Rent': yearly_rent,
            'Rent_Insurance': rent_insurance,
            'Investment_Portfolio': investment_portfolio,
            'Investment_Returns': investment_returns,
            'New_Investments': yearly_investment,
            'Net_Wealth': current_wealth,
            'Yearly_Costs': yearly_costs
        })

    return wealth_values, yearly_details

if st.button("Calculate Comparison", type="primary"):
    # Calculate monthly utilities for each scenario
    total_monthly_utilities_purchase = (electricity_purchase + water_purchase +
                                       other_expenses_purchase)
    yearly_utilities_purchase = total_monthly_utilities_purchase * 12

    total_monthly_utilities_rental = (electricity_rental + water_rental +
                                     other_expenses_rental)
    yearly_utilities_rental = total_monthly_utilities_rental * 12

    # Store input parameters
    purchase_params = {
        'House_Price': house_price,
        'Down_Payment_Percent': down_payment,
        'Interest_Rate': interest_rate,
        'Property_Tax_Rate': property_tax,
        'Maintenance_Rate': maintenance_rate,
        'Insurance': insurance,
        'Property_Growth_Rate': long_term_growth,
        'Monthly_Investment': monthly_investment_purchase,
        'Investment_Return': investment_return
    }

    rental_params = {
        'Monthly_Rent': monthly_rent,
        'Initial_Investment': initial_investment,
        'Monthly_Investment': monthly_investment,
        'Investment_Return': investment_return,
        'Rent_Insurance': rent_insurance,
        'Rent_Increase_Rate': rent_increase
    }

    # Calculate scenarios
    property_values, equity_values, purchase_details = calculate_purchase_scenario(
        house_price=house_price,
        down_payment_pct=down_payment,
        interest_rate=interest_rate,
        years=years,
        property_tax_rate=property_tax,
        maintenance_rate=maintenance_rate,
        insurance=insurance,
        appreciation_rate=long_term_growth,
        monthly_investment=monthly_investment_purchase,
        investment_return=investment_return
    )

    rental_wealth, rental_details = calculate_rental_scenario(
        monthly_rent=monthly_rent,
        monthly_investment=monthly_investment,
        years=years,
        rent_increase=rent_increase,
        investment_return=investment_return,
        rent_insurance=rent_insurance,
        initial_investment=initial_investment
    )

    # Create DataFrame for logging
    df = pd.DataFrame({
        'Year': range(1, years + 1),
        'Property_Value': property_values,
        'Home_Equity': equity_values,
        'Rental_Wealth': rental_wealth
    })

    # Add rental details
    rental_df = pd.DataFrame(rental_details)

    # Save parameters to separate CSV
    params_df = pd.DataFrame({
        'Parameter': ['Years'] + list(purchase_params.keys()) + list(rental_params.keys()),
        'Value': [years] + list(purchase_params.values()) + list(rental_params.values())
    })

    # Save to CSV files
    params_df.to_csv('input_parameters.csv', index=False)
    df.to_csv('comparison_results.csv', index=False)
    rental_df.to_csv('rental_detailed_analysis.csv', index=False)
    purchase_df = pd.DataFrame(purchase_details)
    purchase_df.to_csv('purchase_detailed_analysis.csv', index=False)

    # Display success message
    st.success("Results have been saved to CSV files: 'input_parameters.csv', 'comparison_results.csv', 'rental_detailed_analysis.csv', and 'purchase_detailed_analysis.csv'")

    # Create the figure
    fig = go.Figure()

    # Calculate cumulative costs for each year
    cumulative_purchase_costs = []
    cumulative_rental_costs = []
    running_purchase_cost = 0
    running_rental_cost = 0

    for year in range(years):
        # Purchase costs for this year
        yearly_purchase_cost = (
            purchase_df.iloc[year]['Yearly_Mortgage'] +
            purchase_df.iloc[year]['Property_Tax'] +
            purchase_df.iloc[year]['Maintenance'] +
            purchase_df.iloc[year]['Insurance']
        )
        running_purchase_cost += yearly_purchase_cost
        cumulative_purchase_costs.append(running_purchase_cost)

        # Rental costs for this year
        yearly_rental_cost = (
            rental_df.iloc[year]['Yearly_Rent'] +
            rental_df.iloc[year]['Rent_Insurance']
        )
        running_rental_cost += yearly_rental_cost
        cumulative_rental_costs.append(running_rental_cost)

    # Calculate net worth for each scenario
    purchase_net_worth = [
        property_values[i] - cumulative_purchase_costs[i]
        for i in range(years)
    ]

    rental_net_worth = [
        rental_df.iloc[i]['Investment_Portfolio'] - cumulative_rental_costs[i]
        for i in range(years)
    ]

    # Add property value line
    fig.add_trace(go.Scatter(
        x=list(range(years)),
        y=property_values,
        name='Property Value',
        line=dict(color='lightblue', dash='dash')
    ))

    # Add purchase scenario net worth
    fig.add_trace(go.Scatter(
        x=list(range(years)),
        y=purchase_net_worth,
        name='Purchase Net Worth',
        line=dict(color='blue')
    ))

    # Add rental scenario net worth
    fig.add_trace(go.Scatter(
        x=list(range(years)),
        y=rental_net_worth,
        name='Rental Net Worth',
        line=dict(color='red')
    ))

    fig.update_layout(
        title=f'Net Worth Comparison Over {years} Years (Including All Costs)',
        xaxis_title='Years',
        yaxis_title='Value ($)',
        height=600,
        showlegend=True
    )

    # After creating purchase_df and rental_df, add these calculations
    total_interest_paid = purchase_df['Interest_Paid'].sum()
    total_principal_paid = purchase_df['Principal_Paid'].sum()
    total_property_tax = purchase_df['Property_Tax'].sum()
    total_maintenance = purchase_df['Maintenance'].sum()
    total_home_insurance = insurance * years
    total_utilities_purchase = yearly_utilities_purchase * years
    total_utilities_rental = yearly_utilities_rental * years

    total_purchase_costs = (total_interest_paid + total_principal_paid +
                          total_property_tax + total_maintenance +
                          total_home_insurance + total_utilities_purchase)

    total_rent_paid = rental_df['Yearly_Rent'].sum()
    total_rent_insurance = rental_df['Rent_Insurance'].sum()
    total_rental_costs = total_rent_paid + total_rent_insurance + total_utilities_rental
    final_investment_value = rental_df['Investment_Portfolio'].iloc[-1]
    total_investment_returns = rental_df['Investment_Returns'].sum()
    total_new_investments = rental_df['New_Investments'].sum()

    # Display the graph
    st.plotly_chart(fig, use_container_width=True)

    # Update the header to use the actual years value
    st.header(f"Total Payments Over {years} Years")
    col_totals1, col_totals2 = st.columns(2)

    with col_totals1:
        st.markdown("### Purchase Scenario")
        st.markdown(f"**Total Interest Paid:** ${total_interest_paid:,.2f}")
        st.markdown(f"**Total Principal Paid:** ${total_principal_paid:,.2f}")
        st.markdown(f"**Total Property Tax:** ${total_property_tax:,.2f}")
        st.markdown(f"**Total Maintenance:** ${total_maintenance:,.2f}")
        st.markdown(f"**Total Home Insurance:** ${total_home_insurance:,.2f}")
        st.markdown(f"**Total Utilities & Other:** ${total_utilities_purchase:,.2f}")
        st.markdown(f"**Total Cost:** ${total_purchase_costs:,.2f}")
        st.markdown("#### Investment Portfolio")
        st.markdown(f"**Total New Investments:** ${purchase_df['New_Investments'].sum():,.2f}")
        st.markdown(f"**Total Investment Returns:** ${purchase_df['Investment_Returns'].sum():,.2f}")
        st.markdown(f"**Final Portfolio Value:** ${purchase_df['Investment_Portfolio'].iloc[-1]:,.2f}")

    with col_totals2:
        st.markdown("### Rental Scenario")
        st.markdown(f"**Total Rent Paid:** ${total_rent_paid:,.2f}")
        st.markdown(f"**Total Rent Insurance:** ${total_rent_insurance:,.2f}")
        st.markdown(f"**Total Utilities & Other:** ${total_utilities_rental:,.2f}")
        st.markdown(f"**Total Cost:** ${total_rental_costs:,.2f}")
        st.markdown("#### Investment Portfolio")
        st.markdown(f"**Initial Investment:** ${initial_investment:,.2f}")
        st.markdown(f"**Total New Investments:** ${total_new_investments:,.2f}")
        st.markdown(f"**Total Investment Returns:** ${total_investment_returns:,.2f}")
        st.markdown(f"**Final Portfolio Value:** ${final_investment_value:,.2f}")