import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from translation_utils import create_language_selector, translate_text, translate_number_input, translate_slider

def calculate_purchase_scenario(house_price, down_payment_pct, interest_rate, years,
                              property_tax_rate, maintenance_rate, insurance, insurance_inflation,
                              appreciation_rate, monthly_investment, investment_return, 
                              investment_increase_rate, utilities_data):
    """
    Updated calculation with inflation considerations for various costs
    utilities_data should contain:
    {
        'electricity': {'base': float, 'inflation': float},
        'water': {'base': float, 'inflation': float},
        'other': {'base': float, 'inflation': float}
    }
    """
    down_payment = house_price * (down_payment_pct / 100)
    loan_amount = house_price - down_payment
    monthly_rate = interest_rate / (100 * 12)
    num_payments = years * 12

    investment_portfolio = 0
    current_monthly_investment = monthly_investment

    if interest_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    property_values = []
    equity_values = []
    remaining_loan = loan_amount
    yearly_details = []
    
    total_interest_to_date = 0
    total_principal_to_date = 0
    current_insurance = insurance

    for year in range(years):
        # Update insurance with inflation
        current_insurance *= (1 + insurance_inflation/100)
        
        # Calculate utilities with inflation for this year
        current_utilities = {
            'electricity': utilities_data['electricity']['base'] * 
                         (1 + utilities_data['electricity']['inflation']/100)**year,
            'water': utilities_data['water']['base'] * 
                    (1 + utilities_data['water']['inflation']/100)**year,
            'other': utilities_data['other']['base'] * 
                    (1 + utilities_data['other']['inflation']/100)**year
        }
        yearly_utilities = sum(current_utilities.values()) * 12

        current_home_value = house_price * (1 + appreciation_rate/100)**year
        yearly_tax = current_home_value * (property_tax_rate/100)
        yearly_maintenance = current_home_value * (maintenance_rate/100)
        yearly_mortgage = monthly_payment * 12

        yearly_interest_paid = 0
        yearly_principal_paid = 0
        for _ in range(12):
            interest_payment = remaining_loan * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_loan = max(0, remaining_loan - principal_payment)
            yearly_interest_paid += interest_payment
            yearly_principal_paid += principal_payment

        equity = current_home_value - remaining_loan
        
        # Update monthly investment amount with inflation
        current_monthly_investment *= (1 + investment_increase_rate/100)
        yearly_investment = current_monthly_investment * 12
        
        investment_returns = investment_portfolio * (investment_return/100)
        investment_portfolio = investment_portfolio * (1 + investment_return/100) + yearly_investment

        total_yearly_costs = (yearly_mortgage + yearly_tax + yearly_maintenance + 
                            current_insurance + yearly_utilities)

        total_interest_to_date += yearly_interest_paid
        total_principal_to_date += yearly_principal_paid

        yearly_details.append({
            'Year': year + 1,
            'Property_Value': current_home_value,
            'Yearly_Mortgage': yearly_mortgage,
            'Property_Tax': yearly_tax,
            'Maintenance': yearly_maintenance,
            'Insurance': current_insurance,
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
            'Yearly_Utilities': yearly_utilities
        })

        property_values.append(current_home_value)
        equity_values.append(equity)

    return property_values, equity_values, yearly_details

def calculate_rental_scenario(monthly_rent, rent_inflation, monthly_investment,
                            investment_increase_rate, years, investment_return,
                            rent_insurance, rent_insurance_inflation,
                            utilities_data, initial_investment=0):
    """
    Updated rental calculation with inflation considerations
    """
    wealth_values = []
    investment_portfolio = initial_investment
    yearly_details = []
    
    current_monthly_investment = monthly_investment
    current_rent = monthly_rent
    current_insurance = rent_insurance

    for year in range(years):
        # Update rent insurance with inflation
        current_insurance *= (1 + rent_insurance_inflation/100)
        
        # Calculate utilities with inflation for this year
        current_utilities = {
            'electricity': utilities_data['electricity']['base'] * 
                         (1 + utilities_data['electricity']['inflation']/100)**year,
            'water': utilities_data['water']['base'] * 
                    (1 + utilities_data['water']['inflation']/100)**year,
            'other': utilities_data['other']['base'] * 
                    (1 + utilities_data['other']['inflation']/100)**year
        }
        yearly_utilities = sum(current_utilities.values()) * 12

        # Update rent with inflation
        current_rent *= (1 + rent_inflation/100)
        yearly_rent = current_rent * 12
        
        # Update investment amount with inflation
        current_monthly_investment *= (1 + investment_increase_rate/100)
        yearly_investment = current_monthly_investment * 12

        yearly_costs = yearly_rent + current_insurance + yearly_utilities

        investment_returns = investment_portfolio * (investment_return/100)
        investment_portfolio = investment_portfolio * (1 + investment_return/100) + yearly_investment

        current_wealth = investment_portfolio

        wealth_values.append(current_wealth)

        yearly_details.append({
            'Year': year + 1,
            'Yearly_Rent': yearly_rent,
            'Rent_Insurance': current_insurance,
            'Investment_Portfolio': investment_portfolio,
            'Investment_Returns': investment_returns,
            'New_Investments': yearly_investment,
            'Net_Wealth': current_wealth,
            'Yearly_Costs': yearly_costs,
            'Yearly_Utilities': yearly_utilities
        })

    return wealth_values, yearly_details

def show():
    # Check if we're in deployment environment
    is_deployed = os.getenv('DEPLOYMENT_ENV') == 'production'
    
    # Initialize language only if deployed
    current_lang = 'en'  # Default to English
    if is_deployed:
        current_lang = create_language_selector()
    
    st.title(translate_text("Rent vs. Buy Calculator", current_lang))
    st.write(translate_text("Compare the financial implications of renting versus buying a home", current_lang))

    # Common inputs
    annual_income = translate_number_input(
        translate_text("Annual Household Income ($)", current_lang),
        current_lang,
        min_value=0,
        max_value=1000000,
        value=100000,
        step=1000,
        help=translate_text("Total yearly household income before taxes", current_lang)
    )

    years = translate_number_input(
        translate_text('Simulation Years:', current_lang),
        current_lang,
        min_value=1,
        max_value=50,
        value=30,
        help=translate_text("Number of years to simulate the comparison", current_lang)
    )

    # Create columns for the layout
    col1, col2, col3 = st.columns(3)

    # Purchase-related inputs in left column
    with col1:
        st.header(translate_text("Purchase Options", current_lang))
        house_price = translate_number_input(
            translate_text("House Price ($)", current_lang),
            current_lang,
            min_value=0,
            max_value=10000000,
            value=500000,
            step=1000,
            help=translate_text("Enter the total price of the house you're considering", current_lang)
        )

        interest_rate = translate_slider(
            translate_text("Mortgage Interest Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=15.0,
            value=6.5,
            step=0.1,
            help=translate_text("Annual mortgage interest rate", current_lang)
        )

        down_payment = translate_slider(
            translate_text("Down Payment (%)", current_lang),
            current_lang,
            min_value=0,
            max_value=100,
            value=20,
            help=translate_text("Percentage of house price as down payment", current_lang)
        )

        # Move payment calculations here, after all inputs are defined
        loan_amount = house_price * (1 - down_payment/100)
        monthly_rate = interest_rate / (100 * 12)
        num_payments = years * 12

        if interest_rate == 0:
            monthly_payment = loan_amount / num_payments
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

        # Calculate first month's interest and principal
        first_interest = loan_amount * monthly_rate
        first_principal = monthly_payment - first_interest

        st.markdown(translate_text("### Monthly Payment Breakdown", current_lang))
        st.markdown(translate_text(f"**Total Monthly Payment:** ${monthly_payment:,.2f}", current_lang))
        st.markdown(translate_text(f"**First Payment Breakdown:**", current_lang))
        st.markdown(translate_text(f"- Principal: ${first_principal:,.2f}", current_lang))
        st.markdown(translate_text(f"- Interest: ${first_interest:,.2f}", current_lang))

        long_term_growth = translate_slider(
            translate_text("Expected Annual Property Value Growth (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help=translate_text("Expected annual increase in property value", current_lang)
        )

        maintenance_rate = translate_slider(
            translate_text("Annual Maintenance Rate (% of Property Value)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help=translate_text("Expected yearly maintenance and repairs as percentage of property value", current_lang)
        )

        property_tax = translate_slider(
            translate_text("Property Tax Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=5.0,
            value=1.2,
            step=0.1,
            help=translate_text("Annual property tax as percentage of home value", current_lang)
        )

        col_homeins1, col_homeins_inflation = st.columns(2)
        with col_homeins1:
            insurance = translate_number_input(
                translate_text("Annual Home Insurance ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=2400,
                step=100,
                key="home_insurance"
            )
        with col_homeins_inflation:
            insurance_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="home_insurance_inflation"
            )

        col_inv_purchase1, col_inv_purchase_inflation = st.columns(2)
        with col_inv_purchase1:
            monthly_investment_purchase = translate_number_input(
                translate_text("Monthly Investment ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                key="purchase_investment"
            )
        with col_inv_purchase_inflation:
            investment_increase_rate_purchase = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="purchase_investment_increase_rate"
            )

    # Rental and income inputs in middle column
    with col2:
        st.header(translate_text("Rental Options", current_lang))
        initial_investment = translate_number_input(
            translate_text("Initial Investment ($)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10000000.0,
            value=float(house_price * down_payment/100),
            step=1000.0,
            help=translate_text("Initial amount you could invest (equivalent to down payment if buying)", current_lang)
        )

        investment_return = translate_slider(
            translate_text("Expected Annual Investment Return (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.1,
            help=translate_text("Expected annual return on investments", current_lang)
        )

        col_rent1, col_rent_inflation = st.columns(2)
        with col_rent1:
            monthly_rent = translate_number_input(
                translate_text("Monthly Rent ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=2500,
                step=100,
                key="rent_amount"
            )
        with col_rent_inflation:
            rent_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.1,
                key="rent_inflation"
            )

        col_rent_ins1, col_rent_ins_inflation = st.columns(2)
        with col_rent_ins1:
            rent_insurance = translate_number_input(
                translate_text("Annual Rental Insurance ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=10000,
                value=300,
                step=50,
                key="rent_insurance")
        with col_rent_ins_inflation:
            rent_insurance_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="rent_insurance_inflation"
            )

        col_inv_rental1, col_inv_rental_inflation = st.columns(2)
        with col_inv_rental1:
            monthly_investment = translate_number_input(
                translate_text("Monthly Investment ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                key="rental_investment"
            )
        with col_inv_rental_inflation:
            investment_increase_rate = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="rental_investment_increase_rate"
            )

    # New utilities/expenses section in right column
    with col3:
        st.header(translate_text("Monthly Utilities & Expenses", current_lang))

        st.markdown(translate_text("### Purchase Scenario", current_lang))
        col_utility1, col_inflation1 = st.columns(2)
        with col_utility1:
            electricity_purchase = translate_number_input(
                translate_text("Electricity ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=1000,
                value=150,
                step=10,
                key="electricity_purchase"
            )
        with col_inflation1:
            electricity_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="electricity_inflation"
            )

        col_utility2, col_inflation2 = st.columns(2)
        with col_utility2:
            water_purchase = translate_number_input(
                translate_text("Water ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=500,
                value=50,
                step=10,
                key="water_purchase"
            )
        with col_inflation2:
            water_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="water_inflation"
            )

        col_utility3, col_inflation3 = st.columns(2)
        with col_utility3:
            other_expenses_purchase = translate_number_input(
                translate_text("Other Monthly Expenses ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=1000,
                value=100,
                step=10,
                key="other_purchase"
            )
        with col_inflation3:
            other_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="other_inflation"
            )

        st.markdown(translate_text("### Rental Scenario", current_lang))
        
        col_utility4, col_inflation4 = st.columns(2)
        with col_utility4:
            electricity_rental = translate_number_input(
                translate_text("Electricity ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=1000,
                value=150,
                step=10,
                key="electricity_rental",
                help=translate_text("Monthly electricity costs for rental (0 if included in rent)", current_lang)
            )
        with col_inflation4:
            electricity_rental_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="electricity_rental_inflation"
            )

        col_utility5, col_inflation5 = st.columns(2)
        with col_utility5:
            water_rental = translate_number_input(
                translate_text("Water ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=500,
                value=50,
                step=10,
                key="water_rental",
                help=translate_text("Monthly water costs for rental (0 if included in rent)", current_lang)
            )
        with col_inflation5:
            water_rental_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="water_rental_inflation"
            )

        col_utility6, col_inflation6 = st.columns(2)
        with col_utility6:
            other_expenses_rental = translate_number_input(
                translate_text("Other Monthly Expenses ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=1000,
                value=100,
                step=10,
                key="other_rental",
                help=translate_text("Other monthly housing-related expenses for rental", current_lang)
            )
        with col_inflation6:
            other_rental_inflation = translate_slider(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="other_rental_inflation"
            )

    if st.button(translate_text("Calculate Comparison", current_lang), type="primary"):
        # Purchase scenario utilities data
        utilities_data = {
            'electricity': {'base': electricity_purchase, 'inflation': electricity_inflation},
            'water': {'base': water_purchase, 'inflation': water_inflation},
            'other': {'base': other_expenses_purchase, 'inflation': other_inflation}
        }

        # Rental scenario utilities data
        rental_utilities_data = {
            'electricity': {'base': electricity_rental, 'inflation': electricity_rental_inflation},
            'water': {'base': water_rental, 'inflation': water_rental_inflation},
            'other': {'base': other_expenses_rental, 'inflation': other_rental_inflation}
        }

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
            'Rent_Increase_Rate': rent_inflation
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
            insurance_inflation=insurance_inflation,
            appreciation_rate=long_term_growth,
            monthly_investment=monthly_investment_purchase,
            investment_return=investment_return,
            investment_increase_rate=investment_increase_rate_purchase,
            utilities_data=utilities_data
        )

        rental_wealth, rental_details = calculate_rental_scenario(
            monthly_rent=monthly_rent,
            rent_inflation=rent_inflation,
            monthly_investment=monthly_investment,
            investment_increase_rate=investment_increase_rate,
            years=years,
            investment_return=investment_return,
            rent_insurance=rent_insurance,
            rent_insurance_inflation=rent_insurance_inflation,
            utilities_data=rental_utilities_data,
            initial_investment=initial_investment
        )

        # Create DataFrame for logging
        df = pd.DataFrame({
            'Year': range(1, years + 1),
            'Property_Value': property_values,
            'Home_Equity': equity_values,
            'Rental_Wealth': rental_wealth
        })

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
                purchase_details[year]['Yearly_Mortgage'] +
                purchase_details[year]['Property_Tax'] +
                purchase_details[year]['Maintenance'] +
                purchase_details[year]['Insurance']
            )
            running_purchase_cost += yearly_purchase_cost
            cumulative_purchase_costs.append(running_purchase_cost)

            # Rental costs for this year
            yearly_rental_cost = (
                rental_details[year]['Yearly_Rent'] +
                rental_details[year]['Rent_Insurance']
            )
            running_rental_cost += yearly_rental_cost
            cumulative_rental_costs.append(running_rental_cost)

        # Calculate net worth for each scenario
        purchase_net_worth = [
            property_values[i] - cumulative_purchase_costs[i] + purchase_details[i]['Investment_Portfolio']
            for i in range(years)
        ]

        rental_net_worth = [
            rental_details[i]['Investment_Portfolio'] - cumulative_rental_costs[i]
            for i in range(years)
        ]

        # Add purchase scenario net worth
        fig.add_trace(go.Scatter(
            x=list(range(years)),
            y=purchase_net_worth,
            name=translate_text('Purchase Net Worth', current_lang),
            line=dict(color='blue')
        ))

        # Add rental scenario net worth
        fig.add_trace(go.Scatter(
            x=list(range(years)),
            y=rental_net_worth,
            name=translate_text('Rental Net Worth', current_lang),
            line=dict(color='red')
        ))

        fig.update_layout(
            title=translate_text(f'Net Worth Comparison Over {years} Years (Including All Costs)', current_lang),
            xaxis_title=translate_text('Years', current_lang),
            yaxis_title=translate_text('Value ($)', current_lang),
            height=600,
            showlegend=True
        )

        # Display the graph
        st.plotly_chart(fig, use_container_width=True)

        # Calculate summary statistics
        total_interest_paid = sum(year['Interest_Paid'] for year in purchase_details)
        total_principal_paid = sum(year['Principal_Paid'] for year in purchase_details)
        total_property_tax = sum(year['Property_Tax'] for year in purchase_details)
        total_maintenance = sum(year['Maintenance'] for year in purchase_details)
        total_home_insurance = sum(year['Insurance'] for year in purchase_details)
        total_utilities_purchase = sum(year['Yearly_Utilities'] for year in purchase_details)

        total_purchase_costs = (total_interest_paid + total_principal_paid +
                              total_property_tax + total_maintenance +
                              total_home_insurance + total_utilities_purchase)

        total_rent_paid = sum(year['Yearly_Rent'] for year in rental_details)
        total_rent_insurance = sum(year['Rent_Insurance'] for year in rental_details)
        total_utilities_rental = sum(year['Yearly_Utilities'] for year in rental_details)
        total_rental_costs = total_rent_paid + total_rent_insurance + total_utilities_rental

        final_investment_value_rental = rental_details[-1]['Investment_Portfolio']
        total_investment_returns_rental = sum(year['Investment_Returns'] for year in rental_details)
        total_new_investments_rental = sum(year['New_Investments'] for year in rental_details)

        final_investment_value_purchase = purchase_details[-1]['Investment_Portfolio']
        total_investment_returns_purchase = sum(year['Investment_Returns'] for year in purchase_details)
        total_new_investments_purchase = sum(year['New_Investments'] for year in purchase_details)

        # Display summary statistics
        st.header(translate_text(f"Total Payments Over {years} Years", current_lang))
        col_totals1, col_totals2 = st.columns(2)

        with col_totals1:
            st.markdown(translate_text("### Purchase Scenario", current_lang))
            st.markdown(translate_text(f"**Total Interest Paid:** ${total_interest_paid:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Principal Paid:** ${total_principal_paid:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Property Tax:** ${total_property_tax:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Maintenance:** ${total_maintenance:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Home Insurance:** ${total_home_insurance:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Utilities & Other:** ${total_utilities_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Cost:** ${total_purchase_costs:,.2f}", current_lang))
            st.markdown(translate_text("#### Investment Portfolio", current_lang))
            st.markdown(translate_text(f"**Total New Investments:** ${total_new_investments_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Investment Returns:** ${total_investment_returns_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Final Portfolio Value:** ${final_investment_value_purchase:,.2f}", current_lang))

        with col_totals2:
            st.markdown(translate_text("### Rental Scenario", current_lang))
            st.markdown(translate_text(f"**Total Rent Paid:** ${total_rent_paid:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Rent Insurance:** ${total_rent_insurance:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Utilities & Other:** ${total_utilities_rental:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Cost:** ${total_rental_costs:,.2f}", current_lang))
            st.markdown(translate_text("#### Investment Portfolio", current_lang))
            st.markdown(translate_text(f"**Initial Investment:** ${initial_investment:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total New Investments:** ${total_new_investments_rental:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Investment Returns:** ${total_investment_returns_rental:,.2f}", current_lang))
            st.markdown(translate_text(f"**Final Portfolio Value:** ${final_investment_value_rental:,.2f}", current_lang))

        # Create DataFrames and save to CSV
        results_df = pd.DataFrame({
            'Year': range(1, years + 1),
            'Property_Value': property_values,
            'Home_Equity': equity_values,
            'Rental_Wealth': rental_wealth
        })

        params_df = pd.DataFrame({
            'Parameter': ['Years'] + list(purchase_params.keys()) + list(rental_params.keys()),
            'Value': [years] + list(purchase_params.values()) + list(rental_params.values())
        })

        purchase_df = pd.DataFrame(purchase_details)
        rental_df = pd.DataFrame(rental_details)

        # Create output folder if it doesn't exist
        output_folder = 'output_data'
        os.makedirs(output_folder, exist_ok=True)

        # Save all data to CSV files
        params_df.to_csv(os.path.join(output_folder, 'input_parameters.csv'), index=False)
        results_df.to_csv(os.path.join(output_folder, 'comparison_results.csv'), index=False)
        rental_df.to_csv(os.path.join(output_folder, 'rental_detailed_analysis.csv'), index=False)
        purchase_df.to_csv(os.path.join(output_folder, 'purchase_detailed_analysis.csv'), index=False)

if __name__ == "__main__":
    show()