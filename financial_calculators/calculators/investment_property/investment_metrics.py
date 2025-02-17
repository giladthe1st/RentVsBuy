"""
Module for investment-related calculations.
"""

from typing import List, Tuple, Dict
from functools import lru_cache
import numpy_financial as npf
import numpy as np
import streamlit as st

# Function to calculate loan details

@lru_cache(maxsize=128)
def calculate_loan_details(price: float, down_payment_pct: float, interest_rates: Tuple[Tuple[float, int, float], ...], loan_years: int) -> Tuple[List[float], float]:
    """
    Calculate monthly mortgage payments and loan amount with variable interest rates.
    Uses vectorized operations and caching for improved performance.
    
    Args:
        price: Property purchase price
        down_payment_pct: Down payment percentage
        interest_rates: Tuple of tuples containing (rate, years, one_time_payment) for immutability in caching
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
    for rate, years, one_time_payment in interest_rates:
        if rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if years <= 0:
            raise ValueError("Rate period must be positive")
        if one_time_payment < 0:
            raise ValueError("One-time payment cannot be negative")

    loan_amount = price * (1 - down_payment_pct / 100)
    if not interest_rates:
        return [0] * (loan_years * 12), loan_amount
        
    # Calculate total years from interest rate periods
    total_rate_years = sum(years for _, years, _ in interest_rates)

    # Adjust loan_years to match total_rate_years
    loan_years = total_rate_years
    
    total_months = loan_years * 12
    monthly_payments = []
    remaining_principal = loan_amount
    current_month = 0
    
    for rate, years, one_time_payment in interest_rates:
        if current_month >= total_months or remaining_principal <= 0:
            break
            
        # Apply one-time payment at the start of the period
        remaining_principal = max(0, remaining_principal - one_time_payment)
        if remaining_principal <= 0:
            monthly_payments.extend([0] * (years * 12))
            current_month += years * 12
            continue
            
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

def calculate_monthly_payment(principal, annual_rate, term):
    monthly_rate = annual_rate / (12 * 100)
    return principal * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)

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

def get_rate_for_month(rates, month):
    total_months = 0
    for rate, years, _ in rates:
        total_months += years * 12
        if month < total_months:
            return rate
    return 0

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
    rates_tuple = tuple((rate['rate'], rate['years'], rate.get('one_time_payment', 0)) for rate in interest_rates)
    
    # Calculate total years from interest rate periods
    total_rate_years = sum(years for _, years, _ in rates_tuple)

    # Adjust holding_period to match total_rate_years
    holding_period = total_rate_years

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
    
    # Calculate equity buildup from principal payments
    remaining_balance = loan_amount
    for i, payment in enumerate(monthly_payments):
        if payment == 0:  # Handle case where there's no loan
            break
        rate = get_rate_for_month(rates_tuple, i) / (12 * 100)  # Convert annual rate to monthly
        interest = remaining_balance * rate
        principal = payment - interest
        remaining_balance -= principal
    
    equity_from_principal = loan_amount - remaining_balance
    equity_from_appreciation = property_value - purchase_price
    total_equity = equity_from_principal + equity_from_appreciation
    
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
        'final_property_value': property_value,
        'equity_from_principal': equity_from_principal,
        'equity_from_appreciation': equity_from_appreciation,
        'total_equity': total_equity
    }
