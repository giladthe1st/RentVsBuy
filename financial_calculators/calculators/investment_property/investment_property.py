import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
import streamlit as st
from functools import lru_cache
import numpy_financial as npf

# Use relative imports
from utils.financial_calculator import FinancialCalculator
from calculators.investment_property.loan_calculations import calculate_monthly_payment, calculate_remaining_balance
from calculators.investment_property.investment_metrics import calculate_loan_details, calculate_noi, calculate_cap_rate, calculate_coc_return, calculate_irr, calculate_tax_brackets, calculate_investment_metrics

@lru_cache(maxsize=128)
def get_rate_for_month(interest_rates: Tuple[Tuple[float, int], ...], month: int) -> float:
    """Get the interest rate applicable for a given month using cached lookup."""
    months_passed = 0
    for rate, years in interest_rates:
        period_months = years * 12
        if month < months_passed + period_months:
            return rate
        months_passed += period_months
    return interest_rates[-1][0] if interest_rates else 0.0

def show():
    """Main function to display the investment property calculator."""
    
    # Check if we're in deployment environment
    is_deployed = False  # Set to False for testing
    
    st.title("Investment Property Calculator")
    st.write("Evaluate potential real estate investments and analyze their financial performance")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")
        
        # Property type selection
        property_type = st.selectbox(
            "Property Type",
            ["Single Family", "Multi-Family", "Condo"],
            help="Select the type of property you're analyzing"
        )
        
        # Purchase details
        purchase_price = float(st.number_input(
            "Purchase Price ($)",
            min_value=0,
            value=300000,
            step=1000,
            help="Enter the total purchase price of the property"
        ))
        
        # Calculate and display closing costs
        closing_costs = FinancialCalculator.calculate_closing_costs(purchase_price)
        with st.expander("View Closing Costs Breakdown"):
            st.markdown(f"""
            #### One-Time Closing Costs
            - Legal Fees: ${closing_costs['legal_fees']:,.2f}
            - Bank Appraisal Fee: ${closing_costs['bank_appraisal_fee']:,.2f}
            - Interest Adjustment: ${closing_costs['interest_adjustment']:,.2f}
            - Title Insurance: ${closing_costs['title_insurance']:,.2f}
            - Land Transfer Tax: ${closing_costs['land_transfer_tax']:,.2f}
            
            **Total Closing Costs: ${closing_costs['total']:,.2f}**
            
            [Learn more about closing costs](https://www.example.com/closing-costs-info)
            """)
        
        down_payment_pct = float(st.number_input(
            "Down Payment (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            help="Percentage of purchase price as down payment"
        ))
        down_payment_amount = purchase_price * (down_payment_pct / 100)
        st.markdown(f"Down Payment Amount: **${down_payment_amount:,.2f}**")
        
        interest_rates = []
        num_rate_periods = int(st.number_input(
            "Number of Interest Rate Periods",
            min_value=1,
            max_value=10,
            value=1,
            help="Number of interest rate periods for the mortgage"
        ))
        
        for i in range(num_rate_periods):
            rate_col1, rate_col2 = st.columns([2, 1])
            with rate_col1:
                rate = float(st.number_input(
                    f"Interest Rate {i+1} (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=4.0,
                    step=0.1,
                    help=f"Annual interest rate for period {i+1}"
                ))
            with rate_col2:
                years = int(st.number_input(
                    f"Years for Rate {i+1}",
                    min_value=1,
                    max_value=40,
                    value=30,
                    help=f"Number of years for interest rate {i+1}"
                ))
            interest_rates.append({'rate': rate, 'years': years})
        
        # Option to use calculated or custom holding period
        use_calculated_period = st.checkbox(
            "Use calculated holding period based on interest rate periods",
            value=True
        )

        if use_calculated_period:
            # Calculate total holding period from interest rate periods
            total_holding_period = sum(rate['years'] for rate in interest_rates)
            # Display calculated holding period
            st.markdown(f"Expected Holding Period (Years): **{total_holding_period}**")
        else:
            # Allow manual input for holding period
            total_holding_period = int(st.number_input(
                "Expected Holding Period (Years)",
                min_value=1,
                max_value=100,
                value=30,
                help="Enter your desired holding period"
            ))

    with col2:
        st.subheader("Income Analysis")
        
        # Create columns for salary and its increase rate
        salary_col1, salary_col2 = st.columns([2, 1])
        
        with salary_col1:
            # Annual salary input
            annual_salary = float(st.number_input(
                "Annual Salary ($)",
                min_value=0,
                value=80000,
                step=1000,
                help="Enter your annual salary for tax calculation"
            ))
        
        with salary_col2:
            salary_inflation = float(st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.1,
                help="Expected annual percentage increase in salary"
            ))
        
        # Create columns for rent and its increase rate
        rent_col1, rent_col2 = st.columns([2, 1])
        
        with rent_col1:
            monthly_rent = float(st.number_input(
                "Expected Monthly Rent ($)",
                min_value=0,
                value=2000,
                step=100,
                help="Enter the expected monthly rental income"
            ))
        
        with rent_col2:
            annual_rent_increase = float(st.number_input(
                "Annual Increase (%)",
                min_value=0,
                max_value=10,
                value=3,
                help="Expected annual percentage increase in rental income"
            ))
        
        other_income = float(st.number_input(
            "Other Monthly Income ($)",
            min_value=0,
            value=0,
            step=50,
            help="Additional income from parking, laundry, storage, etc."
        ))
        
        vacancy_rate = float(st.number_input(
            "Vacancy Rate (%)",
            min_value=0,
            max_value=20,
            value=5,
            help="Expected percentage of time the property will be vacant"
        ))

    # Calculate initial mortgage details
    metrics = calculate_investment_metrics(
        purchase_price, down_payment_pct, interest_rates, total_holding_period,
        monthly_rent, annual_rent_increase, {'property_tax': 3000, 'insurance': 1200, 'utilities': 0, 'mgmt_fee': 200, 'hoa_fees': 0}, vacancy_rate
    )
    monthly_payments = metrics['monthly_payments']
    loan_amount = purchase_price * (1 - down_payment_pct / 100)

    # Display initial mortgage details
    st.subheader("Initial Mortgage Details")
    mort_col1, mort_col2, mort_col3, mort_col4, mort_col5 = st.columns(5)
    
    with mort_col1:
        st.metric(
            "Loan Amount",
            f"${loan_amount:,.2f}",
            help="Total amount borrowed for the mortgage"
        )
    with mort_col2:
        st.metric(
            "Monthly Payment",
            f"${monthly_payments[0]:,.2f}",
            help="Monthly mortgage payment"
        )
    with mort_col3:
        st.metric(
            "Annual Payment",
            f"${monthly_payments[0] * 12:,.2f}",
            help="Total yearly mortgage payment"
        )
    with mort_col4:
        st.metric(
            "Down Payment",
            f"${down_payment_amount:,.2f}",
            help="Initial down payment amount"
        )
    with mort_col5:
        st.metric(
            "Closing Costs",
            f"${closing_costs['total']:,.2f}",
            help="One-time closing costs for property purchase"
        )

    # Operating Expenses Section
    st.subheader("Operating Expenses")
    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        property_tax = float(st.number_input(
            "Annual Property Tax ($)",
            min_value=0,
            value=3000,
            step=100,
            help="Annual property tax amount"
        ))
        
        insurance = float(st.number_input(
            "Annual Insurance ($)",
            min_value=0,
            value=1200,
            step=100,
            help="Annual property insurance cost"
        ))
        
        utilities = float(st.number_input(
            "Monthly Utilities ($)",
            min_value=0,
            value=0,
            step=50,
            help="Monthly utilities cost (if paid by owner)"
        ))
        
        mgmt_fee = float(st.number_input(
            "Monthly Property Management Fee ($)",
            min_value=0,
            value=200,
            step=50,
            help="Monthly property management fee"
        ))

    with exp_col2:
        maintenance_pct = float(st.number_input(
            "Maintenance & Repairs (% of property value)",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Expected annual maintenance costs as percentage of property value"
        ))
        
        hoa_fees = float(st.number_input(
            "Monthly HOA Fees ($)",
            min_value=0,
            value=0,
            step=50,
            help="Monthly HOA or condo fees if applicable"
        ))

    with exp_col3:
        property_tax_inflation = float(st.number_input(
            "Property Tax Annual Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Expected annual increase in property tax"
        ))
        
        insurance_inflation = float(st.number_input(
            "Insurance Annual Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help="Expected annual increase in insurance cost"
        ))
        
        utilities_inflation = float(st.number_input(
            "Utilities Annual Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help="Expected annual increase in utilities cost"
        ))
        
        mgmt_fee_inflation = float(st.number_input(
            "Management Fee Annual Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Expected annual increase in property management fee"
        ))
        
        hoa_inflation = float(st.number_input(
            "HOA Fees Annual Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help="Expected annual increase in HOA fees"
        ))

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
        "Total Monthly Operating Expenses",
        f"${monthly_operating_expenses:,.2f}",
        help="Sum of all monthly operating expenses"
    )

    # Financial Analysis Section
    st.subheader("Financial Analysis")

    # Calculate key metrics
    monthly_gross_income = monthly_rent + other_income
    monthly_vacancy_loss = monthly_gross_income * (vacancy_rate / 100)
    monthly_effective_income = monthly_gross_income - monthly_vacancy_loss
    
    monthly_cash_flow = (
        monthly_effective_income -
        monthly_payments[0] -
        monthly_operating_expenses
    )
    
    annual_noi = (monthly_effective_income - monthly_operating_expenses) * 12
    cap_rate = calculate_cap_rate(annual_noi, purchase_price)
    cash_on_cash = calculate_coc_return(monthly_cash_flow * 12, down_payment_amount)

    # Display key metrics in columns
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            "Monthly Cash Flow",
            f"${monthly_cash_flow:,.2f}",
            help="Net monthly income after all expenses and mortgage payment"
        )
        st.metric(
            "Annual Cash Flow",
            f"${monthly_cash_flow * 12:,.2f}",
            help="Total yearly cash flow (monthly cash flow × 12)"
        )
    
    with metrics_col2:
        st.metric(
            "Net Operating Income (NOI)",
            f"${annual_noi:,.2f}",
            help="Annual income after operating expenses but before mortgage payments"
        )
        st.metric(
            "Cap Rate",
            f"{cap_rate:.2f}%",
            help="Net Operating Income divided by property value"
        )
    
    with metrics_col3:
        st.metric(
            "Cash on Cash Return",
            f"{cash_on_cash:.2f}%",
            help="Annual cash flow divided by down payment"
        )
        st.metric(
            "Down Payment",
            f"${down_payment_amount:,.2f}",
            help="Initial cash investment required"
        )

    # Appreciation Scenarios
    st.subheader("Property Value Appreciation Scenarios")
    
    appreciation_col1, appreciation_col2, appreciation_col3 = st.columns(3)
    
    with appreciation_col1:
        conservative_rate = float(st.number_input(
            "Conservative Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Annual property value appreciation rate - conservative estimate"
        ))
    
    with appreciation_col2:
        moderate_rate = float(st.number_input(
            "Moderate Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help="Annual property value appreciation rate - moderate estimate"
        ))
    
    with appreciation_col3:
        optimistic_rate = float(st.number_input(
            "Optimistic Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Annual property value appreciation rate - optimistic estimate"
        ))

    # Calculate future values and IRR for each scenario
    years = list(range(total_holding_period + 1))
    
    # Calculate loan amortization to track principal paid
    loan_schedule = []
    remaining_balance = loan_amount
    for month in range(len(monthly_payments)):
        current_rate = get_rate_for_month(tuple((rate['rate'], rate['years']) for rate in interest_rates), month)
        interest_payment = remaining_balance * (current_rate / (12 * 100))
        principal_payment = monthly_payments[month] - interest_payment
        remaining_balance -= principal_payment
        loan_schedule.append({
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Balance': remaining_balance
        })
    
    # Calculate annual cash flows with rent increase and expense inflation
    annual_cash_flows = []
    for year in range(total_holding_period):
        # Calculate rent for this year with annual increase
        year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
        year_monthly_income = year_monthly_rent + other_income
        year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
        year_effective_income = year_monthly_income - year_monthly_vacancy_loss
        year_effective_income = year_effective_income * 12
        
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
        annual_mortgage = monthly_payments[year * 12] * 12 if year < len(monthly_payments) // 12 else 0
        
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
    
    for year in range(total_holding_period + 1):
        # Base equity is down payment + principal paid - closing costs
        base_equity = down_payment_amount + sum([loan['Principal'] for loan in loan_schedule[:year*12]]) - closing_costs['total']
        
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
            "Conservative IRR",
            f"{conservative_roi:.1f}%",
            help="Internal Rate of Return assuming conservative appreciation"
        )
    
    with irr_col2:
        st.metric(
            "Moderate IRR",
            f"{moderate_roi:.1f}%",
            help="Internal Rate of Return assuming moderate appreciation"
        )
    
    with irr_col3:
        st.metric(
            "Optimistic IRR",
            f"{optimistic_roi:.1f}%",
            help="Internal Rate of Return assuming optimistic appreciation"
        )

    # Create visualization
    st.subheader("Property Value and Cash Flow Projections")
    
    # Property Value Chart
    import plotly.graph_objects as go
    fig = go.Figure()
    
    # Add traces for equity values
    fig.add_trace(go.Scatter(
        x=years,
        y=conservative_equity,
        name='Conservative Equity',
        line=dict(color="blue", dash="dot")
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=moderate_equity,
        name='Moderate Equity',
        line=dict(color="green")
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=optimistic_equity,
        name='Optimistic Equity',
        line=dict(color="red", dash="dash")
    ))
    
    # Add trace for cash flows
    fig.add_trace(go.Bar(
        x=list(range(1, total_holding_period + 1)),
        y=annual_cash_flows,
        name='Annual Cash Flow',
        yaxis="y2",
        marker_color="rgba(0,150,0,0.5)"
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title='Property Value and Cash Flow Over Time',
        xaxis_title='Years',
        yaxis_title='Equity Value ($)',
        yaxis2=dict(
            title='Annual Cash Flow ($)',
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
    for month in range(len(monthly_payments)):
        current_rate = get_rate_for_month(tuple((rate['rate'], rate['years']) for rate in interest_rates), month)
        interest_payment = remaining_balance * (current_rate / (12 * 100))
        principal_payment = monthly_payments[month] - interest_payment
        remaining_balance -= principal_payment
        loan_schedule.append({
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Balance': remaining_balance
        })
    
    # Create a DataFrame for the loan schedule
    import pandas as pd
    df_loan = pd.DataFrame(loan_schedule)

    # Income Tax Analysis
    st.subheader("Income Tax Analysis")
    
    # Calculate employment income tax
    employment_tax_deductions = calculate_tax_brackets(annual_salary)
    employment_total_tax = sum(employment_tax_deductions.values())
    employment_after_tax = annual_salary - employment_total_tax
    employment_tax_rate = (employment_total_tax / annual_salary * 100) if annual_salary > 0 else 0
    
    # Calculate combined income tax
    total_taxable_income = annual_salary + (monthly_rent * 12 * (1 - vacancy_rate/100) + other_income * 12 - (monthly_payments[0] * 12 + monthly_operating_expenses * 12))
    combined_tax_deductions = calculate_tax_brackets(total_taxable_income)
    combined_total_tax = sum(combined_tax_deductions.values())
    combined_after_tax = total_taxable_income - combined_total_tax
    combined_tax_rate = (combined_total_tax / total_taxable_income * 100) if total_taxable_income > 0 else 0
    
    # Display employment income analysis
    st.markdown("#### Employment Income Only")
    emp_col1, emp_col2, emp_col3, emp_col4 = st.columns(4)
    
    with emp_col1:
        st.metric(
            "Income",
            f"${annual_salary:,.2f}",
            help="Your annual salary before tax"
        )
    with emp_col2:
        st.metric(
            "Tax Paid",
            f"${employment_total_tax:,.2f}",
            help="Total income tax on employment income"
        )
    with emp_col3:
        st.metric(
            "After-Tax Income",
            f"${employment_after_tax:,.2f}",
            help="Your employment income after tax"
        )
    with emp_col4:
        st.metric(
            "Effective Tax Rate",
            f"{employment_tax_rate:.2f}%",
            help="Your effective tax rate on employment income"
        )
        
    # Display employment income tax brackets
    with st.expander("View Employment Income Tax Breakdown"):
        for bracket, amount in employment_tax_deductions.items():
            if amount > 0:
                st.write(f"{bracket}: **${amount:,.2f}**")
    
    # Display combined income analysis
    st.markdown("#### With Rental Property Income")
    combined_col1, combined_col2, combined_col3, combined_col4 = st.columns(4)
    
    with combined_col1:
        st.metric(
            "Total Income",
            f"${total_taxable_income:,.2f}",
            help="Combined income from employment and rental property"
        )
        st.caption(f"Employment: ${annual_salary:,.2f}")
        st.caption(f"Rental: ${(monthly_rent * 12 * (1 - vacancy_rate/100) + other_income * 12 - (monthly_payments[0] * 12 + monthly_operating_expenses * 12)):,.2f}")
    with combined_col2:
        st.metric(
            "Tax Paid",
            f"${combined_total_tax:,.2f}",
            help="Total income tax on combined income"
        )
        tax_difference = combined_total_tax - employment_total_tax
        st.caption(f"Additional Tax: ${tax_difference:,.2f}")
    with combined_col3:
        st.metric(
            "After-Tax Income",
            f"${combined_after_tax:,.2f}",
            help="Your total income after tax"
        )
        income_difference = combined_after_tax - employment_after_tax
        st.caption(f"Additional Income: ${income_difference:,.2f}")
    with combined_col4:
        st.metric(
            "Effective Tax Rate",
            f"{combined_tax_rate:.2f}%",
            help="Your effective tax rate on total income"
        )
        rate_difference = combined_tax_rate - employment_tax_rate
        st.caption(f"Rate Change: {rate_difference:+.2f}%")
    
    # Display combined income tax brackets
    with st.expander("View Combined Income Tax Breakdown"):
        for bracket, amount in combined_tax_deductions.items():
            if amount > 0:
                st.write(f"{bracket}: **${amount:,.2f}**")

    # Yearly Income Tax Analysis
    st.markdown("___")
    st.subheader("Yearly Income Tax Analysis")
    
    with st.expander("View Detailed Yearly Tax Breakdown"):
        yearly_tax_data = []
        
        # Calculate yearly values
        for year in range(total_holding_period):
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
            if year < len(monthly_payments) // 12 and year * 12 < len(df_loan):
                start_idx = year * 12
                end_idx = min(start_idx + 12, len(df_loan))
                year_interest = df_loan['Interest'][start_idx:end_idx].sum()
                # If we have partial year data, annualize the mortgage payment
                months_in_year = end_idx - start_idx
                year_mortgage = monthly_payments[start_idx] * months_in_year
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
    st.subheader("Cash Flow Analysis")
    
    # Calculate yearly equity from loan paydown
    yearly_equity = []
    for year in range(len(monthly_payments) // 12):
        start_idx = year * 12
        end_idx = start_idx + 12
        yearly_principal = df_loan['Principal'][start_idx:end_idx].sum()
        yearly_equity.append(yearly_principal)

    # Summary metrics for the holding period
    total_equity_buildup = sum(yearly_equity[:total_holding_period])
    total_cash_flow = sum(metrics['annual_cash_flows'])
    average_annual_cash_flow = total_cash_flow / total_holding_period
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric(
            "Total Equity Buildup",
            f"${total_equity_buildup:,.2f}",
            help="Total equity built through loan paydown during holding period"
        )
    
    with summary_col2:
        st.metric(
            "Total Cash Flow",
            f"${total_cash_flow:,.2f}",
            help="Total cash flow during holding period"
        )
    
    with summary_col3:
        st.metric(
            "Average Annual Cash Flow",
            f"${average_annual_cash_flow:,.2f}",
            help="Average yearly cash flow during holding period"
        )

    # Yearly Breakdown Section
    st.markdown("___")
    st.subheader("Yearly Cost and Revenue Breakdown")
    
    with st.expander("View Detailed Yearly Breakdown"):
        yearly_data = []
        for year in range(total_holding_period):
            # Calculate values for this year
            year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
            year_monthly_income = year_monthly_rent + other_income
            year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
            
            year_property_tax = property_tax * (1 + property_tax_inflation/100)**year
            year_insurance = insurance * (1 + insurance_inflation/100)**year
            year_utilities = utilities * (1 + utilities_inflation/100)**year * 12
            year_mgmt_fee = mgmt_fee * (1 + mgmt_fee_inflation/100)**year * 12
            year_maintenance = monthly_maintenance * 12 * (1 + conservative_rate/100)**year
            year_hoa = hoa_fees * (1 + hoa_inflation/100)**year * 12
            
            # Calculate property values for each scenario
            conservative_value = purchase_price * (1 + conservative_rate/100)**year
            moderate_value = purchase_price * (1 + moderate_rate/100)**year
            optimistic_value = purchase_price * (1 + optimistic_rate/100)**year
            
            # Calculate mortgage components for this year
            if year < len(monthly_payments) // 12:
                start_idx = year * 12
                end_idx = start_idx + 12
                year_principal = df_loan['Principal'][start_idx:end_idx].sum()
                year_interest = df_loan['Interest'][start_idx:end_idx].sum()
                year_mortgage = sum(monthly_payments[start_idx:end_idx])
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
                "Cash Flow": f"${metrics['annual_cash_flows'][year]:,.2f}",
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