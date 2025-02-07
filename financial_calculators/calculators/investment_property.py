import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import streamlit as st
from functools import lru_cache
import numpy_financial as npf

# Use relative imports
from utils.financial_calculator import FinancialCalculator

try:
    from utils.translation_utils import create_language_selector, translate_text, translate_number_input
except ImportError:
    # Mock translation functions for testing
    def translate_text(text, _=None):
        return text

    def translate_number_input(label, lang=None, **kwargs):
        """Mock translation function that handles streamlit parameters"""
        return st.number_input(label, **kwargs)

    def create_language_selector():
        return None

@dataclass
class LoanPeriod:
    """Data class for loan period details."""
    rate: float
    years: int
    months: int
    payment: float

def calculate_monthly_payment(principal: float, annual_rate: float, total_months: int) -> float:
    """Calculate monthly mortgage payment using the standard formula."""
    if principal < 0:
        raise ValueError("Principal amount cannot be negative")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if total_months <= 0:
        raise ValueError("Loan term must be positive")

    if annual_rate == 0:
        return principal / total_months
    monthly_rate = annual_rate / (12 * 100)
    return principal * (monthly_rate * (1 + monthly_rate)**total_months) / ((1 + monthly_rate)**total_months - 1)

def calculate_remaining_balance(principal: float, payment: float, annual_rate: float, months: int) -> float:
    """Calculate remaining loan balance after a number of payments."""
    if principal < 0:
        raise ValueError("Principal amount cannot be negative")
    if payment < 0:
        raise ValueError("Payment amount cannot be negative")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if months <= 0:
        raise ValueError("Number of payments must be positive")

    if annual_rate == 0:
        return principal - (payment * months)
    monthly_rate = annual_rate / (12 * 100)
    return principal * (1 + monthly_rate)**months - payment * ((1 + monthly_rate)**months - 1) / monthly_rate
    
@lru_cache(maxsize=128)
def calculate_loan_details(price: float, down_payment_pct: float, interest_rates: Tuple[Tuple[float, int], ...], loan_years: int) -> Tuple[List[float], float]:
    """
    Calculate monthly mortgage payments and loan amount with variable interest rates.
    Uses vectorized operations and caching for improved performance.
    
    Args:
        price: Property purchase price
        down_payment_pct: Down payment percentage
        interest_rates: Tuple of tuples containing (rate, years) for immutability in caching
        loan_years: Total loan term in years
    
    Returns:
        Tuple of (list of monthly payments, loan amount)
    """
    if price < 0:
        raise ValueError("Property price cannot be negative")
    if down_payment_pct < 0 or down_payment_pct > 100:
        raise ValueError("Down payment percentage must be between 0 and 100")
    if loan_years <= 0:
        raise ValueError("Loan term must be positive")
    for rate, years in interest_rates:
        if rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if years <= 0:
            raise ValueError("Rate period must be positive")

    loan_amount = price * (1 - down_payment_pct / 100)
    if not interest_rates:
        return [0] * (loan_years * 12), loan_amount
        
    total_months = loan_years * 12
    monthly_payments = []
    remaining_principal = loan_amount
    current_month = 0
    
    for rate, years in interest_rates:
        if current_month >= total_months or remaining_principal <= 0:
            break
            
        # Calculate months for this period
        period_months = min(years * 12, total_months - current_month)
        monthly_rate = rate / (12 * 100)
        
        # Calculate payment based on remaining principal and remaining term
        # This ensures the loan will be fully amortized by the end
        remaining_term = total_months - current_month
        payment = calculate_monthly_payment(remaining_principal, rate, remaining_term)
        
        # Calculate amortization for this period
        for _ in range(period_months):
            if remaining_principal <= 0:
                monthly_payments.append(0)
                continue
                
            interest = remaining_principal * monthly_rate
            principal = min(payment - interest, remaining_principal)
            remaining_principal = max(0, remaining_principal - principal)
            monthly_payments.append(payment)
            
        current_month += period_months
    
    # Fill any remaining months with zero payments
    while len(monthly_payments) < total_months:
        monthly_payments.append(0)
    
    return monthly_payments, loan_amount

@lru_cache(maxsize=256)
def get_rate_for_month(interest_rates: Tuple[Tuple[float, int], ...], month: int) -> float:
    """Get the interest rate applicable for a given month using cached lookup."""
    months_passed = 0
    for rate, years in interest_rates:
        period_months = years * 12
        if month < months_passed + period_months:
            return rate
        months_passed += period_months
    return interest_rates[-1][0] if interest_rates else 0.0

@lru_cache(maxsize=128)
def calculate_noi(annual_income: float, operating_expenses: float) -> float:
    """Calculate Net Operating Income with caching."""
    if annual_income < 0:
        raise ValueError("Annual income cannot be negative")
    if operating_expenses < 0:
        raise ValueError("Operating expenses cannot be negative")
    return annual_income - operating_expenses

@lru_cache(maxsize=128)
def calculate_cap_rate(noi: float, property_value: float) -> float:
    """Calculate Capitalization Rate with caching."""
    if property_value <= 0:
        return 0.0  # Return 0 for invalid property values
    return (noi / property_value) * 100

@lru_cache(maxsize=128)
def calculate_coc_return(annual_cash_flow: float, total_investment: float) -> float:
    """Calculate Cash on Cash Return with caching."""
    if total_investment <= 0:
        return 0.0  # Return 0 for invalid investment values
    return (annual_cash_flow / total_investment) * 100

def calculate_irr(initial_investment: float, cash_flows: List[float], final_value: float) -> float:
    """Calculate Internal Rate of Return using vectorized operations."""
    if initial_investment < 0:
        raise ValueError("Initial investment cannot be negative")
    if final_value < 0:
        raise ValueError("Final value cannot be negative")
    flows = np.array([-initial_investment] + cash_flows + [final_value])
    try:
        result = npf.irr(flows)
        return 0.0 if np.isnan(result) else result * 100
    except:
        return 0.0

@lru_cache(maxsize=128)
def calculate_tax_brackets(annual_salary: float) -> Dict[str, float]:
    """Calculate tax deductions based on 2025 tax brackets with caching."""
    if annual_salary < 0:
        raise ValueError("Annual salary cannot be negative")
        
    # Define brackets with thresholds and rates
    brackets = (
        (47564, 0.2580, "0 to 47,564"),
        (57375, 0.2775, "47,564 to 57,375"),
        (101200, 0.3325, "57,375 to 101,200"),
        (114750, 0.3790, "101,200 to 114,750"),
        (177882, 0.4340, "114,750 to 177,882"),
        (200000, 0.4672, "177,882 to 200,000"),
        (253414, 0.4758, "200,000 to 253,414"),
        (400000, 0.5126, "253,414 to 400,000"),
        (float('inf'), 0.5040, "400,000+")
    )
    
    tax_paid = {}
    remaining_income = annual_salary
    prev_threshold = 0
    
    for threshold, rate, range_text in brackets:
        if remaining_income <= 0:
            break
            
        taxable_amount = min(remaining_income, threshold - prev_threshold)
        if taxable_amount > 0:
            tax_paid[f"{rate*100:.2f}% ({range_text})"] = taxable_amount * rate
        remaining_income -= taxable_amount
        prev_threshold = threshold
    
    return tax_paid

@st.cache_data(ttl=3600)
def calculate_investment_metrics(purchase_price: float, down_payment_pct: float, 
                              interest_rates: List[Dict[str, float]], holding_period: int,
                              monthly_rent: float, annual_rent_increase: float,
                              operating_expenses: Dict[str, float], vacancy_rate: float) -> Dict:
    """Calculate and cache investment metrics."""
    if purchase_price < 0:
        raise ValueError("Purchase price cannot be negative")
    if down_payment_pct < 0 or down_payment_pct > 100:
        raise ValueError("Down payment percentage must be between 0 and 100")
    if holding_period <= 0:
        raise ValueError("Holding period must be positive")
    if monthly_rent < 0:
        raise ValueError("Monthly rent cannot be negative")
    if annual_rent_increase < 0:
        raise ValueError("Annual rent increase cannot be negative")
    if vacancy_rate < 0 or vacancy_rate > 100:
        raise ValueError("Vacancy rate must be between 0 and 100")
    for expense, value in operating_expenses.items():
        if value < 0:
            raise ValueError(f"{expense} cannot be negative")
    for rate in interest_rates:
        if rate['rate'] < 0:
            raise ValueError("Interest rate cannot be negative")
        if rate['years'] <= 0:
            raise ValueError("Rate period must be positive")

    # Convert interest rates to tuple for caching
    rates_tuple = tuple((rate['rate'], rate['years']) for rate in interest_rates)
    
    # Get mortgage details
    monthly_payments, loan_amount = calculate_loan_details(
        purchase_price, down_payment_pct, rates_tuple, holding_period
    )
    
    # Calculate monthly cash flows using vectorized operations
    months = holding_period * 12
    month_array = np.arange(months)
    
    # Calculate rent with annual increases
    annual_rent_increase_factor = 1 + annual_rent_increase/100
    monthly_rent_array = monthly_rent * np.power(annual_rent_increase_factor, month_array // 12)
    effective_rent = monthly_rent_array * (1 - vacancy_rate/100)
    
    # Calculate operating expenses with annual increases
    # Assume expenses also increase with inflation
    annual_expenses = sum(operating_expenses.values())
    monthly_expenses = (annual_expenses / 12) * np.power(annual_rent_increase_factor, month_array // 12)
    
    # Calculate monthly cash flows
    monthly_cash_flows = effective_rent - monthly_expenses - monthly_payments
    
    # Calculate key metrics
    total_investment = purchase_price * (down_payment_pct/100)
    annual_cash_flows = np.sum(monthly_cash_flows.reshape(-1, 12), axis=1)
    
    # Calculate NOI using first year's numbers for cap rate
    first_year_rent = monthly_rent * 12 * (1 - vacancy_rate/100)
    first_year_expenses = annual_expenses
    noi = calculate_noi(first_year_rent, first_year_expenses)
    
    # Calculate other metrics
    cap_rate = calculate_cap_rate(noi, purchase_price)
    coc_return = calculate_coc_return(annual_cash_flows[0], total_investment)
    
    # Calculate appreciation using the same rate as rent increases
    property_value = purchase_price * np.power(annual_rent_increase_factor, holding_period)
    
    # Calculate IRR
    irr_value = calculate_irr(total_investment, annual_cash_flows.tolist(), property_value)
    
    return {
        'monthly_payments': monthly_payments,
        'monthly_cash_flows': monthly_cash_flows.tolist(),
        'annual_cash_flows': annual_cash_flows.tolist(),
        'noi': noi,
        'cap_rate': cap_rate,
        'coc_return': coc_return,
        'irr': irr_value,
        'final_property_value': property_value
    }

def show():
    """Main function to display the investment property calculator."""
    
    # Check if we're in deployment environment
    is_deployed = False  # Set to False for testing
    
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
        purchase_price = float(translate_number_input(
            translate_text("Purchase Price ($)", current_lang),
            current_lang,
            min_value=0,
            value=300000,
            step=1000,
            help=translate_text("Enter the total purchase price of the property", current_lang)
        ))
        
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
            
            [Learn more about closing costs](https://www.example.com/closing-costs-info)
            """)
        
        down_payment_pct = float(translate_number_input(
            translate_text("Down Payment (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            help=translate_text("Percentage of purchase price as down payment", current_lang)
        ))
        down_payment_amount = purchase_price * (down_payment_pct / 100)
        st.markdown(f"Down Payment Amount: **${down_payment_amount:,.2f}**")
        
        interest_rates = []
        num_rate_periods = int(translate_number_input(
            translate_text("Number of Interest Rate Periods", current_lang),
            current_lang,
            min_value=1,
            max_value=10,
            value=1,
            help=translate_text("Number of interest rate periods for the mortgage", current_lang)
        ))
        
        for i in range(num_rate_periods):
            rate_col1, rate_col2 = st.columns([2, 1])
            with rate_col1:
                rate = float(translate_number_input(
                    translate_text(f"Interest Rate {i+1} (%)", current_lang),
                    current_lang,
                    min_value=0.0,
                    max_value=20.0,
                    value=4.0,
                    step=0.1,
                    help=translate_text(f"Annual interest rate for period {i+1}", current_lang)
                ))
            with rate_col2:
                years = int(translate_number_input(
                    translate_text(f"Years for Rate {i+1}", current_lang),
                    current_lang,
                    min_value=1,
                    max_value=40,
                    value=30,
                    help=translate_text(f"Number of years for interest rate {i+1}", current_lang)
                ))
            interest_rates.append({'rate': rate, 'years': years})
        
        holding_period = int(translate_number_input(
            translate_text("Expected Holding Period (Years)", current_lang),
            current_lang,
            min_value=1,
            max_value=50,
            value=30,
            help=translate_text("How long do you plan to hold this investment?", current_lang)
        ))

    with col2:
        st.subheader(translate_text("Income Analysis", current_lang))
        
        # Create columns for salary and its increase rate
        salary_col1, salary_col2 = st.columns([2, 1])
        
        with salary_col1:
            # Annual salary input
            annual_salary = float(translate_number_input(
                translate_text("Annual Salary ($)", current_lang),
                current_lang,
                min_value=0,
                value=80000,
                step=1000,
                help=translate_text("Enter your annual salary for tax calculation", current_lang)
            ))
        
        with salary_col2:
            salary_inflation = float(translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.1,
                help=translate_text("Expected annual percentage increase in salary", current_lang)
            ))
        
        # Create columns for rent and its increase rate
        rent_col1, rent_col2 = st.columns([2, 1])
        
        with rent_col1:
            monthly_rent = float(translate_number_input(
                translate_text("Expected Monthly Rent ($)", current_lang),
                current_lang,
                min_value=0,
                value=2000,
                step=100,
                help=translate_text("Enter the expected monthly rental income", current_lang)
            ))
        
        with rent_col2:
            annual_rent_increase = float(translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0,
                max_value=10,
                value=3,
                help=translate_text("Expected annual percentage increase in rental income", current_lang)
            ))
        
        other_income = float(translate_number_input(
            translate_text("Other Monthly Income ($)", current_lang),
            current_lang,
            min_value=0,
            value=0,
            step=50,
            help=translate_text("Additional income from parking, laundry, storage, etc.", current_lang)
        ))
        
        vacancy_rate = float(translate_number_input(
            translate_text("Vacancy Rate (%)", current_lang),
            current_lang,
            min_value=0,
            max_value=20,
            value=5,
            help=translate_text("Expected percentage of time the property will be vacant", current_lang)
        ))

    # Calculate initial mortgage details
    metrics = calculate_investment_metrics(
        purchase_price, down_payment_pct, interest_rates, holding_period,
        monthly_rent, annual_rent_increase, {'property_tax': 3000, 'insurance': 1200, 'utilities': 0, 'mgmt_fee': 200, 'hoa_fees': 0}, vacancy_rate
    )
    monthly_payments = metrics['monthly_payments']
    loan_amount = purchase_price * (1 - down_payment_pct / 100)

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
            f"${monthly_payments[0]:,.2f}",
            help=translate_text("Monthly mortgage payment", current_lang)
        )
    with mort_col3:
        st.metric(
            translate_text("Annual Payment", current_lang),
            f"${monthly_payments[0] * 12:,.2f}",
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
        property_tax = float(translate_number_input(
            translate_text("Annual Property Tax ($)", current_lang),
            current_lang,
            min_value=0,
            value=3000,
            step=100,
            help=translate_text("Annual property tax amount", current_lang)
        ))
        
        insurance = float(translate_number_input(
            translate_text("Annual Insurance ($)", current_lang),
            current_lang,
            min_value=0,
            value=1200,
            step=100,
            help=translate_text("Annual property insurance cost", current_lang)
        ))
        
        utilities = float(translate_number_input(
            translate_text("Monthly Utilities ($)", current_lang),
            current_lang,
            min_value=0,
            value=0,
            step=50,
            help=translate_text("Monthly utilities cost (if paid by owner)", current_lang)
        ))
        
        mgmt_fee = float(translate_number_input(
            translate_text("Monthly Property Management Fee ($)", current_lang),
            current_lang,
            min_value=0,
            value=200,
            step=50,
            help=translate_text("Monthly property management fee", current_lang)
        ))

    with exp_col2:
        maintenance_pct = float(translate_number_input(
            translate_text("Maintenance & Repairs (% of property value)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help=translate_text("Expected annual maintenance costs as percentage of property value", current_lang)
        ))
        
        hoa_fees = float(translate_number_input(
            translate_text("Monthly HOA Fees ($)", current_lang),
            current_lang,
            min_value=0,
            value=0,
            step=50,
            help=translate_text("Monthly HOA or condo fees if applicable", current_lang)
        ))

    with exp_col3:
        property_tax_inflation = float(translate_number_input(
            translate_text("Property Tax Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help=translate_text("Expected annual increase in property tax", current_lang)
        ))
        
        insurance_inflation = float(translate_number_input(
            translate_text("Insurance Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help=translate_text("Expected annual increase in insurance cost", current_lang)
        ))
        
        utilities_inflation = float(translate_number_input(
            translate_text("Utilities Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help=translate_text("Expected annual increase in utilities cost", current_lang)
        ))
        
        mgmt_fee_inflation = float(translate_number_input(
            translate_text("Management Fee Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help=translate_text("Expected annual increase in property management fee", current_lang)
        ))
        
        hoa_inflation = float(translate_number_input(
            translate_text("HOA Fees Annual Increase (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help=translate_text("Expected annual increase in HOA fees", current_lang)
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
        conservative_rate = float(translate_number_input(
            translate_text("Conservative Growth Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help=translate_text("Annual property value appreciation rate - conservative estimate", current_lang)
        ))
    
    with appreciation_col2:
        moderate_rate = float(translate_number_input(
            translate_text("Moderate Growth Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help=translate_text("Annual property value appreciation rate - moderate estimate", current_lang)
        ))
    
    with appreciation_col3:
        optimistic_rate = float(translate_number_input(
            translate_text("Optimistic Growth Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help=translate_text("Annual property value appreciation rate - optimistic estimate", current_lang)
        ))

    # Calculate future values and IRR for each scenario
    years = list(range(holding_period + 1))
    
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
    for year in range(holding_period):
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
    
    for year in range(holding_period + 1):
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
    import plotly.graph_objects as go
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
    st.subheader(translate_text("Income Tax Analysis", current_lang))
    
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
        st.caption(f"Rental: ${(monthly_rent * 12 * (1 - vacancy_rate/100) + other_income * 12 - (monthly_payments[0] * 12 + monthly_operating_expenses * 12)):,.2f}")
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
    st.subheader(translate_text("Cash Flow Analysis", current_lang))
    
    # Calculate yearly equity from loan paydown
    yearly_equity = []
    for year in range(len(monthly_payments) // 12):
        start_idx = year * 12
        end_idx = start_idx + 12
        yearly_principal = df_loan['Principal'][start_idx:end_idx].sum()
        yearly_equity.append(yearly_principal)

    # Summary metrics for the holding period
    total_equity_buildup = sum(yearly_equity[:holding_period])
    total_cash_flow = sum(metrics['annual_cash_flows'])
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