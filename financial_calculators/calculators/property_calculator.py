"""
Core calculations for property investment analysis.
"""
import numpy as np
import numpy_financial as npf
from functools import lru_cache
from typing import List, Dict, Tuple
from ..models.property_investment import PropertyMetrics, PropertyInvestment, PropertyExpenses

def calculate_monthly_payment(principal: float, annual_rate: float, total_months: int) -> float:
    """Calculate monthly mortgage payment using the standard formula."""
    if annual_rate == 0:
        return principal / total_months
    monthly_rate = annual_rate / (12 * 100)
    return principal * (monthly_rate * (1 + monthly_rate)**total_months) / ((1 + monthly_rate)**total_months - 1)

def calculate_remaining_balance(principal: float, payment: float, annual_rate: float, months: int) -> float:
    """Calculate remaining loan balance after a number of payments."""
    if annual_rate == 0:
        return principal - (payment * months)
    monthly_rate = annual_rate / (12 * 100)
    return principal * (1 + monthly_rate)**months - payment * ((1 + monthly_rate)**months - 1) / monthly_rate

@lru_cache(maxsize=128)
def calculate_loan_payments(price: float, down_payment_pct: float, interest_rates: Tuple[Tuple[float, int], ...], loan_years: int) -> List[float]:
    """Calculate monthly mortgage payments with variable interest rates."""
    loan_amount = price * (1 - down_payment_pct / 100)
    total_months = loan_years * 12
    monthly_payments = []
    remaining_principal = loan_amount
    current_month = 0
    
    for rate, years in interest_rates:
        if current_month >= total_months or remaining_principal <= 0:
            break
        
        period_months = min(years * 12, total_months - current_month)
        remaining_term = total_months - current_month
        payment = calculate_monthly_payment(remaining_principal, rate, remaining_term)
        
        monthly_payments.extend([payment] * period_months)
        for _ in range(period_months):
            interest = remaining_principal * (rate / (12 * 100))
            principal_payment = payment - interest
            remaining_principal = max(0, remaining_principal - principal_payment)
            current_month += 1
            
    return monthly_payments

def calculate_noi(annual_income: float, expenses: PropertyExpenses) -> float:
    """Calculate Net Operating Income."""
    total_expenses = (expenses.property_tax + expenses.insurance + expenses.maintenance +
                     expenses.utilities + expenses.hoa + expenses.property_management)
    return annual_income - total_expenses

def calculate_cap_rate(noi: float, property_value: float) -> float:
    """Calculate Capitalization Rate."""
    return noi / property_value if property_value > 0 else 0

def calculate_coc_return(annual_cash_flow: float, total_investment: float) -> float:
    """Calculate Cash on Cash Return."""
    return annual_cash_flow / total_investment if total_investment > 0 else 0

def calculate_irr(initial_investment: float, cash_flows: List[float], final_value: float) -> float:
    """Calculate Internal Rate of Return."""
    all_flows = [initial_investment] + cash_flows + [final_value]
    try:
        irr = float(npf.irr(all_flows))
        return irr if not np.isnan(irr) else 0.0
    except:
        return 0.0

def calculate_metrics(investment: PropertyInvestment) -> PropertyMetrics:
    """Calculate all investment metrics for a property."""
    # Convert interest rates to tuple format for caching
    rates_tuple = tuple((rate['rate'], rate['years']) for rate in investment.interest_rates)
    
    # Calculate monthly payments
    monthly_payments = calculate_loan_payments(
        investment.purchase_price,
        investment.down_payment_pct,
        rates_tuple,
        investment.holding_period
    )
    
    # Calculate monthly cash flows
    monthly_rent_values = [
        investment.monthly_rent * (1 + investment.annual_rent_increase/100)**(i//12)
        for i in range(investment.holding_period * 12)
    ]
    
    monthly_expenses = sum([
        investment.operating_expenses.property_tax,
        investment.operating_expenses.insurance,
        investment.operating_expenses.maintenance,
        investment.operating_expenses.utilities,
        investment.operating_expenses.hoa,
        investment.operating_expenses.property_management
    ]) / 12
    
    monthly_cash_flows = [
        rent * (1 - investment.vacancy_rate/100) - monthly_expenses - payment
        for rent, payment in zip(monthly_rent_values, monthly_payments)
    ]
    
    # Calculate other metrics
    annual_income = sum(monthly_rent_values[:12]) * (1 - investment.vacancy_rate/100)
    noi = calculate_noi(annual_income, investment.operating_expenses)
    cap_rate = calculate_cap_rate(noi, investment.purchase_price)
    
    down_payment = investment.purchase_price * (investment.down_payment_pct / 100)
    annual_cash_flow = sum(monthly_cash_flows[:12])
    coc_return = calculate_coc_return(annual_cash_flow, down_payment)
    
    # Assuming 3% annual appreciation for final value
    final_value = investment.purchase_price * (1.03 ** investment.holding_period)
    irr = calculate_irr(-down_payment, monthly_cash_flows, final_value - investment.purchase_price)
    
    total_profit = sum(monthly_cash_flows) + (final_value - investment.purchase_price)
    roi = (total_profit / down_payment) if down_payment > 0 else 0
    
    # Simple tax savings calculation (assuming 25% tax bracket)
    tax_savings = sum(monthly_payments[:12]) * 0.25
    
    return PropertyMetrics(
        monthly_payments=monthly_payments,
        monthly_cash_flows=monthly_cash_flows,
        noi=noi,
        cap_rate=cap_rate,
        coc_return=coc_return,
        irr=irr,
        total_profit=total_profit,
        roi=roi,
        tax_savings=tax_savings
    )
