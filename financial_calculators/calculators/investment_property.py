import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from numpy_financial import irr
from typing import Dict, List, Tuple
from translation_utils import create_language_selector, translate_text, translate_number_input
import os
from utils.financial_calculator import FinancialCalculator
from utils.constants import CLOSING_COSTS_INFO_URL

def calculate_loan_details(price: float, down_payment_pct: float, interest_rate: float, loan_years: int) -> Tuple[float, float]:
    """Calculate monthly mortgage payment and loan amount."""
    loan_amount = price * (1 - down_payment_pct / 100)
    monthly_rate = interest_rate / (12 * 100)
    num_payments = loan_years * 12
    
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return monthly_payment, loan_amount

def calculate_noi(annual_income: float, operating_expenses: float) -> float:
    """Calculate Net Operating Income."""
    return annual_income - operating_expenses

def calculate_cap_rate(noi: float, property_value: float) -> float:
    """Calculate Capitalization Rate."""
    return (noi / property_value) * 100

def calculate_coc_return(annual_cash_flow: float, total_investment: float) -> float:
    """Calculate Cash on Cash Return."""
    return (annual_cash_flow / total_investment) * 100

def calculate_irr(initial_investment: float, cash_flows: List[float], final_value: float) -> float:
    """Calculate Internal Rate of Return."""
    flows = [-initial_investment] + cash_flows + [final_value]
    try:
        result = irr(flows)
        if np.isnan(result):
            return 0.0
        return result * 100
    except:
        return 0.0  # Return 0% if IRR calculation fails

def calculate_tax_brackets(annual_salary: float) -> Dict[str, float]:
    """Calculate tax deductions based on 2025 tax brackets."""
    brackets = [
        (47564, 0.2580),
        (57375, 0.2775),
        (101200, 0.3325),
        (114750, 0.3790),
        (177882, 0.4340),
        (200000, 0.4672),
        (253414, 0.4758),
        (400000, 0.5126),
        (float('inf'), 0.5040)
    ]
    
    tax_paid = {}
    remaining_income = annual_salary
    prev_bracket = 0
    
    for bracket, rate in brackets:
        if remaining_income <= 0:
            break
            
        taxable_amount = min(remaining_income, bracket - prev_bracket)
        DOLLAR = "&#36;"
        bracket_range = DOLLAR + str(prev_bracket) + " up to " + DOLLAR + str(bracket)
        tax_paid[bracket_range] = taxable_amount * rate
        remaining_income -= taxable_amount
        prev_bracket = bracket
    
    return tax_paid

def show():
    """Main function to display the investment property calculator."""
    
    # Check if we're in deployment environment
    is_deployed = os.getenv('DEPLOYMENT_ENV') == 'production'
    
    # Initialize language only if deployed
    current_lang = 'en'  # Default to English
    if is_deployed:
        current_lang = create_language_selector()
    
    st.title(translate_text("Investment Property Calculator", current_lang))
    st.write(translate_text("Evaluate potential real estate investments and analyze their financial performance", current_lang))

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(translate_text("Property Details", current_lang))
        
        # Property type selection
        property_type = st.selectbox(
            translate_text("Property Type", current_lang),
            ["Single Family", "Multi-Family", "Condo"],
            help=translate_text("Select the type of property you're analyzing", current_lang)
        )
        
        # Purchase details
        purchase_price = translate_number_input(
            translate_text("Purchase Price ($)", current_lang),
            current_lang,
            min_value=0,
            value=300000,
            step=1000,
            help=translate_text("Enter the total purchase price of the property", current_lang)
        )
        
        # Calculate and display closing costs
        closing_costs = FinancialCalculator.calculate_closing_costs(purchase_price)
        with st.expander(translate_text("View Closing Costs Breakdown", current_lang)):
            st.markdown(f"""
            #### {translate_text('One-Time Closing Costs', current_lang)}
            - {translate_text('Legal Fees', current_lang)}: ${closing_costs['legal_fees']:,.2f}
            - {translate_text('Bank Appraisal Fee', current_lang)}: ${closing_costs['bank_appraisal_fee']:,.2f}
            - {translate_text('Interest Adjustment', current_lang)}: ${closing_costs['interest_adjustment']:,.2f}
            - {translate_text('Title Insurance', current_lang)}: ${closing_costs['title_insurance']:,.2f}
            - {translate_text('Land Transfer Tax', current_lang)}: ${closing_costs['land_transfer_tax']:,.2f}
            
            **{translate_text('Total Closing Costs', current_lang)}: ${closing_costs['total']:,.2f}**
            
            [Learn more about closing costs]({CLOSING_COSTS_INFO_URL})
            """)
        
        down_payment_pct = translate_number_input(
            translate_text("Down Payment (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            help=translate_text("Percentage of purchase price as down payment", current_lang)
        )
        down_payment_amount = purchase_price * (down_payment_pct / 100)
        st.markdown(f"Down Payment Amount: **${down_payment_amount:,.2f}**")
        
        interest_rate = translate_number_input(
            translate_text("Interest Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=20.0,
            value=4.0,
            step=0.1,
            help=translate_text("Enter the annual interest rate for the mortgage", current_lang)
        )
        
        loan_years = translate_number_input(
            translate_text("Loan Term (Years)", current_lang),
            current_lang,
            min_value=1,
            max_value=40,
            value=30,
            help=translate_text("Enter the length of the mortgage in years", current_lang)
        )
        
        holding_period = translate_number_input(
            translate_text("Expected Holding Period (Years)", current_lang),
            current_lang,
            min_value=1,
            max_value=50,
            value=30,
            help=translate_text("How long do you plan to hold this investment?", current_lang)
        )

    with col2:
        st.subheader(translate_text("Income Analysis", current_lang))
        
        # Create columns for salary and its increase rate
        salary_col1, salary_col2 = st.columns([2, 1])
        
        with salary_col1:
            # Annual salary input
            annual_salary = translate_number_input(
                translate_text("Annual Salary ($)", current_lang),
                current_lang,
                min_value=0,
                value=80000,
                step=1000,
                help=translate_text("Enter your annual salary for tax calculation", current_lang)
            )
        
        with salary_col2:
            salary_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.1,
                help=translate_text("Expected annual percentage increase in salary", current_lang)
            )
        
        # Create columns for rent and its increase rate
        rent_col1, rent_col2 = st.columns([2, 1])
        
        with rent_col1:
            monthly_rent = translate_number_input(
                translate_text("Expected Monthly Rent ($)", current_lang),
                current_lang,
                min_value=0,
                value=2000,
                step=100,
                help=translate_text("Enter the expected monthly rental income", current_lang)
            )
        
        with rent_col2:
            annual_rent_increase = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0,
                max_value=10,
                value=3,
                help=translate_text("Expected annual percentage increase in rental income", current_lang)
            )
        
        other_income = translate_number_input(
            translate_text("Other Monthly Income ($)", current_lang),
            current_lang,
            min_value=0,
            value=0,
            step=50,
            help=translate_text("Additional income from parking, laundry, storage, etc.", current_lang)
        )
        
        vacancy_rate = translate_number_input(
            translate_text("Vacancy Rate (%)", current_lang),
            current_lang,
            min_value=0,
            max_value=20,
            value=5,
            help=translate_text("Expected percentage of time the property will be vacant", current_lang)
        )

    # Calculate initial mortgage details
    monthly_payment, loan_amount = calculate_loan_details(
        purchase_price,
        down_payment_pct,
        interest_rate,
        loan_years
    )

    # Display initial mortgage details
    st.subheader(translate_text("Initial Mortgage Details", current_lang))
    mort_col1, mort_col2, mort_col3, mort_col4, mort_col5 = st.columns(5)
    
    with mort_col1:
        st.metric(
            translate_text("Loan Amount", current_lang),
            f"${loan_amount:,.2f}",
            help=translate_text("Total amount borrowed for the mortgage", current_lang)
        )
    with mort_col2:
        st.metric(
            translate_text("Monthly Payment", current_lang),
            f"${monthly_payment:,.2f}",
            help=translate_text("Monthly mortgage payment", current_lang)
        )
    with mort_col3:
        st.metric(
            translate_text("Annual Payment", current_lang),
            f"${monthly_payment * 12:,.2f}",
            help=translate_text("Total yearly mortgage payment", current_lang)
        )
    with mort_col4:
        st.metric(
            translate_text("Down Payment", current_lang),
            f"${down_payment_amount:,.2f}",
            help=translate_text("Initial down payment amount", current_lang)
        )
    with mort_col5:
        st.metric(
            translate_text("Closing Costs", current_lang),
            f"${closing_costs['total']:,.2f}",
            help=translate_text("One-time closing costs for property purchase", current_lang)
        )

    # Operating Expenses Section
    st.subheader(translate_text("Operating Expenses", current_lang))
    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        property_tax = translate_number_input(
            translate_text("Annual Property Tax ($)", current_lang),
            current_lang,
            min_value=0,
            value=3000,
            step=100,
            help=translate_text("Annual property tax amount", current_lang)
        )
        
        insurance = translate_number_input(
            translate_text("Annual Insurance ($)", current_lang),
            current_lang,
            min_value=0,
            value=1200,
            step=100,
            help=translate_text("Annual property insurance cost", current_lang)
        )
        
        utilities = translate_number_input(
            translate_text("Monthly Utilities ($)", current_lang),
            current_lang,
            min_value=0,
            value=0,
            step=50,
            help=translate_text("Monthly utilities cost (if paid by owner)", current_lang)
        )
        
        mgmt_fee = translate_number_input(
            translate_text("Monthly Property Management Fee ($)", current_lang),
            current_lang,
            min_value=0,
            value=200,
            step=50,
            help=translate_text("Monthly property management fee", current_lang)
        )

    with exp_col2:
        maintenance_pct = translate_number_input(
            translate_text("Maintenance & Repairs (% of property value)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help=translate_text("Expected annual maintenance costs as percentage of property value", current_lang)
        )
        
        hoa_fees = translate_number_input(
            translate_text("Monthly HOA Fees ($)", current_lang),
            current_lang,
            min_value=0,
            value=0,
            step=50,
            help=translate_text("Monthly HOA or condo fees if applicable", current_lang)
        )

    with exp_col3:
        property_tax_inflation = translate_number_input(
            translate_text("Property Tax Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help=translate_text("Expected annual increase in property tax", current_lang)
        )
        
        insurance_inflation = translate_number_input(
            translate_text("Insurance Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help=translate_text("Expected annual increase in insurance cost", current_lang)
        )
        
        utilities_inflation = translate_number_input(
            translate_text("Utilities Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help=translate_text("Expected annual increase in utilities cost", current_lang)
        )
        
        mgmt_fee_inflation = translate_number_input(
            translate_text("Management Fee Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help=translate_text("Expected annual increase in property management fee", current_lang)
        )
        
        hoa_inflation = translate_number_input(
            translate_text("HOA Fees Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help=translate_text("Expected annual increase in HOA fees", current_lang)
        )

    # Calculate monthly operating expenses
    monthly_maintenance = (purchase_price * (maintenance_pct / 100)) / 12
    monthly_operating_expenses = (
        (property_tax / 12) +
        (insurance / 12) +
        utilities +
        mgmt_fee +
        monthly_maintenance +
        hoa_fees
    )

    # Display total operating expenses
    st.metric(
        translate_text("Total Monthly Operating Expenses", current_lang),
        f"${monthly_operating_expenses:,.2f}",
        help=translate_text("Sum of all monthly operating expenses", current_lang)
    )

    # Financial Analysis Section
    st.subheader(translate_text("Financial Analysis", current_lang))

    # Calculate key metrics
    monthly_gross_income = monthly_rent + other_income
    monthly_vacancy_loss = monthly_gross_income * (vacancy_rate / 100)
    monthly_effective_income = monthly_gross_income - monthly_vacancy_loss
    
    monthly_cash_flow = (
        monthly_effective_income -
        monthly_payment -
        monthly_operating_expenses
    )
    
    annual_noi = (monthly_effective_income - monthly_operating_expenses) * 12
    cap_rate = calculate_cap_rate(annual_noi, purchase_price)
    cash_on_cash = calculate_coc_return(monthly_cash_flow * 12, down_payment_amount)

    # Display key metrics in columns
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            translate_text("Monthly Cash Flow", current_lang),
            f"${monthly_cash_flow:,.2f}",
            help=translate_text("Net monthly income after all expenses and mortgage payment", current_lang)
        )
        st.metric(
            translate_text("Annual Cash Flow", current_lang),
            f"${monthly_cash_flow * 12:,.2f}",
            help=translate_text("Total yearly cash flow (monthly cash flow × 12)", current_lang)
        )
    
    with metrics_col2:
        st.metric(
            translate_text("Net Operating Income (NOI)", current_lang),
            f"${annual_noi:,.2f}",
            help=translate_text("Annual income after operating expenses but before mortgage payments", current_lang)
        )
        st.metric(
            translate_text("Cap Rate", current_lang),
            f"{cap_rate:.2f}%",
            help=translate_text("Net Operating Income divided by property value", current_lang)
        )
    
    with metrics_col3:
        st.metric(
            translate_text("Cash on Cash Return", current_lang),
            f"{cash_on_cash:.2f}%",
            help=translate_text("Annual cash flow divided by down payment", current_lang)
        )
        st.metric(
            translate_text("Down Payment", current_lang),
            f"${down_payment_amount:,.2f}",
            help=translate_text("Initial cash investment required", current_lang)
        )

    # Appreciation Scenarios
    st.subheader(translate_text("Property Value Appreciation Scenarios", current_lang))
    
    appreciation_col1, appreciation_col2, appreciation_col3 = st.columns(3)
    
    with appreciation_col1:
        conservative_rate = translate_number_input(
            translate_text("Conservative Growth Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help=translate_text("Annual property value appreciation rate - conservative estimate", current_lang)
        )
    
    with appreciation_col2:
        moderate_rate = translate_number_input(
            translate_text("Moderate Growth Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help=translate_text("Annual property value appreciation rate - moderate estimate", current_lang)
        )
    
    with appreciation_col3:
        optimistic_rate = translate_number_input(
            translate_text("Optimistic Growth Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help=translate_text("Annual property value appreciation rate - optimistic estimate", current_lang)
        )

    # Calculate future values and IRR for each scenario
    years = list(range(holding_period + 1))
    
    # Calculate loan amortization to track principal paid
    loan_schedule = []
    remaining_balance = loan_amount
    total_principal_paid = 0
    principal_paid_by_year = [0]  # Start with 0 for year 0
    
    for _ in range(loan_years * 12):
        interest_payment = remaining_balance * (interest_rate / (12 * 100))
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        total_principal_paid += principal_payment
        
        if len(principal_paid_by_year) < ((_ + 1) // 12 + 1):
            principal_paid_by_year.append(total_principal_paid)
    
    # Fill remaining years after loan is paid off
    while len(principal_paid_by_year) <= holding_period:
        principal_paid_by_year.append(total_principal_paid)

    # Calculate annual cash flows with rent increase and expense inflation
    annual_cash_flows = []
    for year in range(holding_period):
        # Calculate rent for this year with annual increase
        year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
        year_monthly_income = year_monthly_rent + other_income
        year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
        year_effective_monthly_income = year_monthly_income - year_monthly_vacancy_loss
        year_effective_income = year_effective_monthly_income * 12
        
        # Calculate inflated expenses for this year
        year_property_tax = property_tax * (1 + property_tax_inflation/100)**year
        year_insurance = insurance * (1 + insurance_inflation/100)**year
        year_utilities = utilities * (1 + utilities_inflation/100)**year * 12
        year_mgmt_fee = mgmt_fee * (1 + mgmt_fee_inflation/100)**year * 12
        year_maintenance = monthly_maintenance * 12 * (1 + conservative_rate/100)**year  # Maintenance increases with property value
        year_hoa = hoa_fees * (1 + hoa_inflation/100)**year * 12
        
        # Calculate total expenses for this year
        year_expenses = (
            year_property_tax +
            year_insurance +
            year_utilities +
            year_mgmt_fee +
            year_maintenance +
            year_hoa
        )
        
        # Only include mortgage payment if still within loan term
        annual_mortgage = monthly_payment * 12 if year < loan_years else 0
        
        year_cash_flow = (
            year_effective_income -
            annual_mortgage -
            year_expenses
        )
        annual_cash_flows.append(year_cash_flow)
    
    # Initialize arrays for each scenario - now calculating equity value
    conservative_equity = []
    moderate_equity = []
    optimistic_equity = []
    
    for year in range(holding_period + 1):
        # Base equity is down payment + principal paid - closing costs
        base_equity = down_payment_amount + principal_paid_by_year[year] - closing_costs['total']
        
        # Add appreciation for each scenario
        conservative_appreciation = purchase_price * ((1 + conservative_rate/100)**year - 1)
        moderate_appreciation = purchase_price * ((1 + moderate_rate/100)**year - 1)
        optimistic_appreciation = purchase_price * ((1 + optimistic_rate/100)**year - 1)
        
        conservative_equity.append(base_equity + conservative_appreciation)
        moderate_equity.append(base_equity + moderate_appreciation)
        optimistic_equity.append(base_equity + optimistic_appreciation)

    # Calculate ROI for each scenario
    initial_investment = down_payment_amount + closing_costs['total']  # Include closing costs in initial investment
    
    conservative_roi = calculate_irr(
        initial_investment,
        annual_cash_flows,
        conservative_equity[-1]
    )
    
    moderate_roi = calculate_irr(
        initial_investment,
        annual_cash_flows,
        moderate_equity[-1]
    )
    
    optimistic_roi = calculate_irr(
        initial_investment,
        annual_cash_flows,
        optimistic_equity[-1]
    )

    # Display IRR metrics
    irr_col1, irr_col2, irr_col3 = st.columns(3)
    
    with irr_col1:
        st.metric(
            translate_text("Conservative IRR", current_lang),
            f"{conservative_roi:.1f}%",
            help=translate_text("Internal Rate of Return assuming conservative appreciation", current_lang)
        )
    
    with irr_col2:
        st.metric(
            translate_text("Moderate IRR", current_lang),
            f"{moderate_roi:.1f}%",
            help=translate_text("Internal Rate of Return assuming moderate appreciation", current_lang)
        )
    
    with irr_col3:
        st.metric(
            translate_text("Optimistic IRR", current_lang),
            f"{optimistic_roi:.1f}%",
            help=translate_text("Internal Rate of Return assuming optimistic appreciation", current_lang)
        )

    # Create visualization
    st.subheader(translate_text("Property Value and Cash Flow Projections", current_lang))
    
    # Property Value Chart
    fig = go.Figure()
    
    # Add traces for equity values
    fig.add_trace(go.Scatter(
        x=years,
        y=conservative_equity,
        name=translate_text('Conservative Equity', current_lang),
        line=dict(color="blue", dash="dot")
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=moderate_equity,
        name=translate_text('Moderate Equity', current_lang),
        line=dict(color="green")
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=optimistic_equity,
        name=translate_text('Optimistic Equity', current_lang),
        line=dict(color="red", dash="dash")
    ))
    
    # Add trace for cash flows
    fig.add_trace(go.Bar(
        x=list(range(1, holding_period + 1)),
        y=annual_cash_flows,
        name=translate_text('Annual Cash Flow', current_lang),
        yaxis="y2",
        marker_color="rgba(0,150,0,0.5)"
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title=translate_text('Property Value and Cash Flow Over Time', current_lang),
        xaxis_title=translate_text('Years', current_lang),
        yaxis_title=translate_text('Equity Value ($)', current_lang),
        yaxis2=dict(
            title=translate_text('Annual Cash Flow ($)', current_lang),
            overlaying="y",
            side="right",
            tickformat="$,.0f"
        ),
        yaxis=dict(tickformat="$,.0f"),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Calculate loan schedule
    loan_schedule = []
    remaining_balance = loan_amount
    for _ in range(loan_years * 12):
        interest_payment = remaining_balance * (interest_rate / (12 * 100))
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        loan_schedule.append({
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Balance': remaining_balance
        })
    
    # Create a DataFrame for the loan schedule
    df_loan = pd.DataFrame(loan_schedule)

    # Income Tax Analysis
    st.subheader(translate_text("Income Tax Analysis", current_lang))
    
    # Calculate employment income tax
    employment_tax_deductions = calculate_tax_brackets(annual_salary)
    employment_total_tax = sum(employment_tax_deductions.values())
    employment_after_tax = annual_salary - employment_total_tax
    employment_tax_rate = (employment_total_tax / annual_salary * 100) if annual_salary > 0 else 0
    
    # Calculate combined income tax
    total_taxable_income = annual_salary + (monthly_rent * 12 * (1 - vacancy_rate/100) + other_income * 12 - (monthly_payment * 12 + monthly_operating_expenses * 12))
    combined_tax_deductions = calculate_tax_brackets(total_taxable_income)
    combined_total_tax = sum(combined_tax_deductions.values())
    combined_after_tax = total_taxable_income - combined_total_tax
    combined_tax_rate = (combined_total_tax / total_taxable_income * 100) if total_taxable_income > 0 else 0
    
    # Display employment income analysis
    st.markdown("#### Employment Income Only")
    emp_col1, emp_col2, emp_col3, emp_col4 = st.columns(4)
    
    with emp_col1:
        st.metric(
            translate_text("Income", current_lang),
            f"${annual_salary:,.2f}",
            help=translate_text("Your annual salary before tax", current_lang)
        )
    with emp_col2:
        st.metric(
            translate_text("Tax Paid", current_lang),
            f"${employment_total_tax:,.2f}",
            help=translate_text("Total income tax on employment income", current_lang)
        )
    with emp_col3:
        st.metric(
            translate_text("After-Tax Income", current_lang),
            f"${employment_after_tax:,.2f}",
            help=translate_text("Your employment income after tax", current_lang)
        )
    with emp_col4:
        st.metric(
            translate_text("Effective Tax Rate", current_lang),
            f"{employment_tax_rate:.2f}%",
            help=translate_text("Your effective tax rate on employment income", current_lang)
        )
        
    # Display employment income tax brackets
    with st.expander(translate_text("View Employment Income Tax Breakdown", current_lang)):
        for bracket, amount in employment_tax_deductions.items():
            if amount > 0:
                st.write(f"{bracket}: **${amount:,.2f}**")
    
    # Display combined income analysis
    st.markdown("#### With Rental Property Income")
    combined_col1, combined_col2, combined_col3, combined_col4 = st.columns(4)
    
    with combined_col1:
        st.metric(
            translate_text("Total Income", current_lang),
            f"${total_taxable_income:,.2f}",
            help=translate_text("Combined income from employment and rental property", current_lang)
        )
        st.caption(f"Employment: ${annual_salary:,.2f}")
        st.caption(f"Rental: ${(monthly_rent * 12 * (1 - vacancy_rate/100) + other_income * 12 - (monthly_payment * 12 + monthly_operating_expenses * 12)):,.2f}")
    with combined_col2:
        st.metric(
            translate_text("Tax Paid", current_lang),
            f"${combined_total_tax:,.2f}",
            help=translate_text("Total income tax on combined income", current_lang)
        )
        tax_difference = combined_total_tax - employment_total_tax
        st.caption(f"Additional Tax: ${tax_difference:,.2f}")
    with combined_col3:
        st.metric(
            translate_text("After-Tax Income", current_lang),
            f"${combined_after_tax:,.2f}",
            help=translate_text("Your total income after tax", current_lang)
        )
        income_difference = combined_after_tax - employment_after_tax
        st.caption(f"Additional Income: ${income_difference:,.2f}")
    with combined_col4:
        st.metric(
            translate_text("Effective Tax Rate", current_lang),
            f"{combined_tax_rate:.2f}%",
            help=translate_text("Your effective tax rate on total income", current_lang)
        )
        rate_difference = combined_tax_rate - employment_tax_rate
        st.caption(f"Rate Change: {rate_difference:+.2f}%")
    
    # Display combined income tax brackets
    with st.expander(translate_text("View Combined Income Tax Breakdown", current_lang)):
        for bracket, amount in combined_tax_deductions.items():
            if amount > 0:
                st.write(f"{bracket}: **${amount:,.2f}**")

    # Yearly Income Tax Analysis
    st.markdown("___")
    st.subheader(translate_text("Yearly Income Tax Analysis", current_lang))
    
    with st.expander(translate_text("View Detailed Yearly Tax Breakdown", current_lang)):
        yearly_tax_data = []
        
        # Calculate yearly values
        for year in range(holding_period):
            # Calculate rental income for this year with annual increases
            year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
            year_monthly_income = year_monthly_rent + other_income
            year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
            year_rental_income = (year_monthly_income - year_monthly_vacancy_loss) * 12
            
            # Calculate expenses for this year
            year_property_tax = property_tax * (1 + property_tax_inflation/100)**year
            year_insurance = insurance * (1 + insurance_inflation/100)**year
            year_utilities = utilities * (1 + utilities_inflation/100)**year * 12
            year_mgmt_fee = mgmt_fee * (1 + mgmt_fee_inflation/100)**year * 12
            year_maintenance = monthly_maintenance * 12 * (1 + conservative_rate/100)**year
            year_hoa = hoa_fees * (1 + hoa_inflation/100)**year * 12
            
            # Calculate mortgage components for this year
            if year < loan_years and year * 12 < len(df_loan):
                start_idx = year * 12
                end_idx = min(start_idx + 12, len(df_loan))
                year_interest = df_loan['Interest'][start_idx:end_idx].sum()
                # If we have partial year data, annualize the mortgage payment
                months_in_year = end_idx - start_idx
                year_mortgage = monthly_payment * months_in_year
            else:
                year_interest = 0
                year_mortgage = 0
            
            # Calculate operating expenses
            year_operating_expenses = (
                year_property_tax +
                year_insurance +
                year_utilities +
                year_mgmt_fee +
                year_maintenance +
                year_hoa
            )
            
            # Calculate net rental income
            year_net_rental = year_rental_income - year_operating_expenses - year_mortgage
            
            # Assume salary increases with inflation (use salary_inflation instead of conservative_rate)
            year_salary = annual_salary * (1 + salary_inflation/100)**year
            
            # Calculate taxes for employment income only
            year_employment_tax = calculate_tax_brackets(year_salary)
            year_employment_total_tax = sum(year_employment_tax.values())
            year_employment_after_tax = year_salary - year_employment_total_tax
            year_employment_tax_rate = (year_employment_total_tax / year_salary * 100) if year_salary > 0 else 0
            
            # Calculate taxes for combined income
            year_total_income = year_salary + year_net_rental
            year_combined_tax = calculate_tax_brackets(year_total_income)
            year_combined_total_tax = sum(year_combined_tax.values())
            year_combined_after_tax = year_total_income - year_combined_total_tax
            year_combined_tax_rate = (year_combined_total_tax / year_total_income * 100) if year_total_income > 0 else 0
            
            # Calculate differences
            year_additional_tax = year_combined_total_tax - year_employment_total_tax
            year_additional_after_tax = year_combined_after_tax - year_employment_after_tax
            year_tax_rate_change = year_combined_tax_rate - year_employment_tax_rate
            
            yearly_tax_data.append({
                "Year": year + 1,
                "Employment Income": f"${year_salary:,.2f}",
                "Employment Tax": f"${year_employment_total_tax:,.2f}",
                "Employment After-Tax": f"${year_employment_after_tax:,.2f}",
                "Employment Tax Rate": f"{year_employment_tax_rate:.2f}%",
                "Net Rental Income": f"${year_net_rental:,.2f}",
                "Total Income": f"${year_total_income:,.2f}",
                "Total Tax": f"${year_combined_total_tax:,.2f}",
                "Total After-Tax": f"${year_combined_after_tax:,.2f}",
                "Total Tax Rate": f"{year_combined_tax_rate:.2f}%",
                "Additional Tax": f"${year_additional_tax:,.2f}",
                "Additional After-Tax": f"${year_additional_after_tax:,.2f}",
                "Tax Rate Change": f"{year_tax_rate_change:+.2f}%"
            })
        
        df_tax = pd.DataFrame(yearly_tax_data)
        st.dataframe(df_tax, use_container_width=True)
        
        # Create a line chart showing the progression of after-tax income
        fig = go.Figure()
        
        # Extract numeric values from formatted strings
        employment_after_tax = [float(row['Employment After-Tax'].replace('$', '').replace(',', '')) 
                              for row in yearly_tax_data]
        total_after_tax = [float(row['Total After-Tax'].replace('$', '').replace(',', '')) 
                          for row in yearly_tax_data]
        years = [row['Year'] for row in yearly_tax_data]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=employment_after_tax,
            name='Employment Only',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=total_after_tax,
            name='With Rental Income',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title='After-Tax Income Over Time',
            xaxis_title='Year',
            yaxis_title='After-Tax Income ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Cash Flow Analysis
    st.subheader(translate_text("Cash Flow Analysis", current_lang))
    
    # Calculate yearly equity from loan paydown
    yearly_equity = []
    for year in range(loan_years):
        start_idx = year * 12
        end_idx = start_idx + 12
        yearly_principal = df_loan['Principal'][start_idx:end_idx].sum()
        yearly_equity.append(yearly_principal)

    # Summary metrics for the holding period
    total_equity_buildup = sum(yearly_equity[:holding_period])
    total_cash_flow = sum(annual_cash_flows)
    average_annual_cash_flow = total_cash_flow / holding_period
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric(
            translate_text("Total Equity Buildup", current_lang),
            f"${total_equity_buildup:,.2f}",
            help=translate_text("Total equity built through loan paydown during holding period", current_lang)
        )
    
    with summary_col2:
        st.metric(
            translate_text("Total Cash Flow", current_lang),
            f"${total_cash_flow:,.2f}",
            help=translate_text("Total cash flow during holding period", current_lang)
        )
    
    with summary_col3:
        st.metric(
            translate_text("Average Annual Cash Flow", current_lang),
            f"${average_annual_cash_flow:,.2f}",
            help=translate_text("Average yearly cash flow during holding period", current_lang)
        )

    # Yearly Breakdown Section
    st.markdown("___")
    st.subheader(translate_text("Yearly Cost and Revenue Breakdown", current_lang))
    
    with st.expander(translate_text("View Detailed Yearly Breakdown", current_lang)):
        yearly_data = []
        for year in range(holding_period):
            # Calculate values for this year
            year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
            year_monthly_income = year_monthly_rent + other_income
            year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
            
            year_property_tax = property_tax * (1 + property_tax_inflation/100)**year
            year_insurance = insurance * (1 + insurance_inflation/100)**year
            year_utilities = utilities * (1 + utilities_inflation/100)**year * 12
            year_mgmt_fee = mgmt_fee * (1 + mgmt_fee_inflation/100)**year * 12
            year_maintenance = monthly_maintenance * 12 * (1 + conservative_rate/100)**year  # Maintenance increases with property value
            year_hoa = hoa_fees * (1 + hoa_inflation/100)**year * 12
            
            # Calculate property values for each scenario
            conservative_value = purchase_price * (1 + conservative_rate/100)**year
            moderate_value = purchase_price * (1 + moderate_rate/100)**year
            optimistic_value = purchase_price * (1 + optimistic_rate/100)**year
            
            # Calculate mortgage components for this year
            if year < loan_years:
                start_idx = year * 12
                end_idx = start_idx + 12
                year_principal = df_loan['Principal'][start_idx:end_idx].sum()
                year_interest = df_loan['Interest'][start_idx:end_idx].sum()
                year_mortgage = monthly_payment * 12
            else:
                year_principal = 0
                year_interest = 0
                year_mortgage = 0
            
            yearly_data.append({
                "Year": year + 1,
                "Rental Income": f"${year_monthly_income * 12:,.2f}",
                "Vacancy Loss": f"${year_monthly_vacancy_loss * 12:,.2f}",
                "Property Tax": f"${year_property_tax:,.2f}",
                "Insurance": f"${year_insurance:,.2f}",
                "Utilities": f"${year_utilities:,.2f}",
                "Management Fee": f"${year_mgmt_fee:,.2f}",
                "Maintenance": f"${year_maintenance:,.2f}",
                "HOA Fees": f"${year_hoa:,.2f}",
                "Mortgage Payment": f"${year_mortgage:,.2f}",
                "Principal Paid": f"${year_principal:,.2f}",
                "Interest Paid": f"${year_interest:,.2f}",
                "Cash Flow": f"${annual_cash_flows[year]:,.2f}",
                "Conservative Value": f"${conservative_value:,.2f}",
                "Moderate Value": f"${moderate_value:,.2f}",
                "Optimistic Value": f"${optimistic_value:,.2f}",
                "Equity": f"${conservative_equity[year]:,.2f}"
            })
        
        df = pd.DataFrame(yearly_data)
        st.dataframe(df, use_container_width=True)

def main():
    show()

if __name__ == "__main__":
    main()