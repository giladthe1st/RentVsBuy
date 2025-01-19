import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple
from numpy_financial import irr

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

def show():
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
        purchase_price = st.number_input(
            "Purchase Price ($)",
            min_value=0,
            value=300000,
            step=1000,
            help="Enter the total purchase price of the property"
        )
        
        down_payment_pct = st.slider(
            "Down Payment (%)",
            min_value=0,
            max_value=100,
            value=20,
            help="Enter the down payment percentage"
        )
        
        down_payment_amount = purchase_price * (down_payment_pct / 100)
        st.write(f"Down Payment Amount: ${down_payment_amount:,.2f}")
        
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=6.5,
            step=0.1,
            help="Enter the annual interest rate for the mortgage"
        )
        
        loan_years = st.number_input(
            "Loan Term (Years)",
            min_value=1,
            max_value=40,
            value=30,
            help="Enter the length of the mortgage in years"
        )
        
        holding_period = st.number_input(
            "Expected Holding Period (Years)",
            min_value=1,
            max_value=50,
            value=10,
            help="How long do you plan to hold this investment?"
        )

    with col2:
        st.subheader("Income Analysis")
        
        monthly_rent = st.number_input(
            "Expected Monthly Rent ($)",
            min_value=0,
            value=2000,
            step=100,
            help="Enter the expected monthly rental income"
        )
        
        other_income = st.number_input(
            "Other Monthly Income ($)",
            min_value=0,
            value=0,
            step=50,
            help="Additional income from parking, laundry, storage, etc."
        )
        
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0,
            max_value=20,
            value=5,
            help="Expected percentage of time the property will be vacant"
        )
        
        annual_rent_increase = st.slider(
            "Annual Rent Increase (%)",
            min_value=0,
            max_value=10,
            value=3,
            help="Expected annual percentage increase in rental income"
        )

    # Calculate initial mortgage details
    monthly_payment, loan_amount = calculate_loan_details(
        purchase_price,
        down_payment_pct,
        interest_rate,
        loan_years
    )

    # Display initial mortgage details
    st.subheader("Initial Mortgage Details")
    mort_col1, mort_col2, mort_col3 = st.columns(3)
    
    with mort_col1:
        st.metric("Loan Amount", f"${loan_amount:,.2f}")
    with mort_col2:
        st.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    with mort_col3:
        st.metric("Annual Payment", f"${monthly_payment * 12:,.2f}")

    # Operating Expenses Section
    st.subheader("Operating Expenses")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        property_tax = st.number_input(
            "Annual Property Tax ($)",
            min_value=0,
            value=3000,
            step=100,
            help="Annual property tax amount"
        )
        
        insurance = st.number_input(
            "Annual Insurance ($)",
            min_value=0,
            value=1200,
            step=100,
            help="Annual property insurance cost"
        )
        
        utilities = st.number_input(
            "Monthly Utilities ($)",
            min_value=0,
            value=0,
            step=50,
            help="Monthly utilities cost (if paid by owner)"
        )
        
        mgmt_fee = st.number_input(
            "Monthly Property Management Fee ($)",
            min_value=0,
            value=200,
            step=50,
            help="Monthly property management fee"
        )

    with exp_col2:
        maintenance_pct = st.slider(
            "Maintenance & Repairs (% of property value)",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Expected annual maintenance costs as percentage of property value"
        )
        
        hoa_fees = st.number_input(
            "Monthly HOA Fees ($)",
            min_value=0,
            value=0,
            step=50,
            help="Monthly HOA or condo fees if applicable"
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
            help="Net Operating Income divided by property value. This metric shows the property's return regardless of financing. Higher is better, but typical ranges are 4-10% depending on the market."
        )
    
    with metrics_col3:
        st.metric(
            "Cash on Cash Return",
            f"{cash_on_cash:.2f}%",
            help="Annual cash flow divided by down payment. This shows your actual cash return on the money you invested."
        )
        st.metric(
            "Down Payment",
            f"${down_payment_amount:,.2f}",
            help="Initial cash investment required to purchase the property"
        )

    # Appreciation Scenarios
    st.subheader("Property Value Appreciation Scenarios")
    
    appreciation_col1, appreciation_col2, appreciation_col3 = st.columns(3)
    
    with appreciation_col1:
        conservative_rate = st.number_input(
            "Conservative Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Annual property value appreciation rate - conservative estimate"
        )
    
    with appreciation_col2:
        moderate_rate = st.number_input(
            "Moderate Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help="Annual property value appreciation rate - moderate estimate"
        )
    
    with appreciation_col3:
        optimistic_rate = st.number_input(
            "Optimistic Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Annual property value appreciation rate - optimistic estimate"
        )

    # Calculate future values and IRR for each scenario
    years = list(range(holding_period + 1))
    
    # Calculate annual cash flows with rent increase
    annual_cash_flows = []
    debug_info = []  # Store calculation details for debugging
    
    for year in range(holding_period):
        # Calculate rent for this year with annual increase
        year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
        year_monthly_income = year_monthly_rent + other_income
        year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
        year_effective_monthly_income = year_monthly_income - year_monthly_vacancy_loss
        year_effective_income = year_effective_monthly_income * 12
        
        # Only include mortgage payment if still within loan term
        annual_mortgage = monthly_payment * 12 if year < loan_years else 0
        annual_expenses = monthly_operating_expenses * 12
        
        year_cash_flow = (
            year_effective_income -
            annual_mortgage -
            annual_expenses
        )
        annual_cash_flows.append(year_cash_flow)
        
        # Store debug info for first 5 years
        if year < 5:
            debug_info.append({
                'Year': year + 1,
                'Monthly Rent': f"${year_monthly_rent:,.2f}",
                'Monthly Income with Other': f"${year_monthly_income:,.2f}",
                'Monthly After Vacancy': f"${year_effective_monthly_income:,.2f}",
                'Annual Income': f"${year_effective_income:,.2f}",
                'Annual Mortgage': f"${annual_mortgage:,.2f}",
                'Annual Expenses': f"${annual_expenses:,.2f}",
                'Annual Cash Flow': f"${year_cash_flow:,.2f}"
            })

    # Display debug information in an expander
    with st.expander("Show Detailed Calculations (First 5 Years)"):
        st.write("### Cash Flow Calculation Breakdown")
        for year_info in debug_info:
            st.write(f"\n**Year {year_info['Year']}**")
            st.write(f"Monthly Rent: {year_info['Monthly Rent']}")
            st.write(f"Monthly Income (with other): {year_info['Monthly Income with Other']}")
            st.write(f"Monthly Income (after vacancy): {year_info['Monthly After Vacancy']}")
            st.write(f"Annual Income: {year_info['Annual Income']}")
            st.write(f"Annual Mortgage: {year_info['Annual Mortgage']}")
            st.write(f"Annual Expenses: {year_info['Annual Expenses']}")
            st.write(f"Annual Cash Flow: {year_info['Annual Cash Flow']}")
            st.write("---")
    
    # Initialize arrays for each scenario
    conservative_values = [purchase_price * (1 + conservative_rate/100)**year for year in years]
    moderate_values = [purchase_price * (1 + moderate_rate/100)**year for year in years]
    optimistic_values = [purchase_price * (1 + optimistic_rate/100)**year for year in years]
    
    # Calculate IRR for each scenario using the adjusted cash flows
    conservative_irr = calculate_irr(
        down_payment_amount,
        annual_cash_flows,
        conservative_values[-1] - purchase_price
    )
    
    moderate_irr = calculate_irr(
        down_payment_amount,
        annual_cash_flows,
        moderate_values[-1] - purchase_price
    )
    
    optimistic_irr = calculate_irr(
        down_payment_amount,
        annual_cash_flows,
        optimistic_values[-1] - purchase_price
    )

    # Display IRR metrics
    irr_col1, irr_col2, irr_col3 = st.columns(3)
    
    with irr_col1:
        st.metric(
            "Conservative IRR",
            f"{conservative_irr:.1f}%",
            help="Internal Rate of Return assuming conservative appreciation and increasing rents"
        )
    
    with irr_col2:
        st.metric(
            "Moderate IRR",
            f"{moderate_irr:.1f}%",
            help="Internal Rate of Return assuming moderate appreciation and increasing rents"
        )
    
    with irr_col3:
        st.metric(
            "Optimistic IRR",
            f"{optimistic_irr:.1f}%",
            help="Internal Rate of Return assuming optimistic appreciation and increasing rents"
        )

    # Create visualization
    st.subheader("Property Value and Cash Flow Projections")
    
    # Property Value Chart
    fig = go.Figure()
    
    # Add traces for property values
    fig.add_trace(go.Scatter(
        x=years,
        y=conservative_values,
        name="Conservative Value",
        line=dict(color="blue", dash="dot")
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=moderate_values,
        name="Moderate Value",
        line=dict(color="green")
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=optimistic_values,
        name="Optimistic Value",
        line=dict(color="red", dash="dash")
    ))
    
    # Add trace for cash flows
    fig.add_trace(go.Bar(
        x=list(range(1, holding_period + 1)),
        y=annual_cash_flows,
        name="Annual Cash Flow",
        yaxis="y2",
        marker_color="rgba(0,150,0,0.5)"
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title="Property Value and Cash Flow Over Time",
        xaxis_title="Years",
        yaxis_title="Property Value ($)",
        yaxis2=dict(
            title="Annual Cash Flow ($)",
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

    # Cash Flow Analysis
    st.subheader("Cash Flow Analysis")
    
    # Calculate monthly principal and interest for each payment
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
    
    # Calculate yearly equity from loan paydown
    yearly_equity = []
    for year in range(loan_years):
        start_idx = year * 12
        end_idx = start_idx + 12
        yearly_principal = df_loan['Principal'][start_idx:end_idx].sum()
        yearly_equity.append(yearly_principal)
    
    # Create equity buildup visualization
    fig_equity = go.Figure()
    
    fig_equity.add_trace(go.Bar(
        x=list(range(1, loan_years + 1)),
        y=yearly_equity,
        name="Annual Equity Buildup",
        marker_color='green'
    ))
    
    fig_equity.update_layout(
        title="Annual Equity Buildup from Loan Paydown",
        xaxis_title="Year",
        yaxis_title="Equity Added ($)",
        showlegend=False,
        yaxis=dict(tickformat="$,.0f")
    )
    
    st.plotly_chart(fig_equity, use_container_width=True)

    # Summary metrics for the holding period
    total_equity_buildup = sum(yearly_equity[:holding_period])
    total_cash_flow = sum(annual_cash_flows)
    average_annual_cash_flow = total_cash_flow / holding_period
    
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
            help="Total cash flow during holding period, including rent increases"
        )
    
    with summary_col3:
        st.metric(
            "Average Annual Cash Flow",
            f"${average_annual_cash_flow:,.2f}",
            help="Average yearly cash flow during holding period"
        )