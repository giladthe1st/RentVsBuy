"""
Data models for property investment calculations.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class LoanPeriod:
    """Data class for loan period details."""
    rate: float
    years: int
    months: int
    payment: float

@dataclass
class PropertyMetrics:
    """Data class for property investment metrics."""
    monthly_payments: List[float]
    monthly_cash_flows: List[float]
    noi: float
    cap_rate: float
    coc_return: float
    irr: float
    total_profit: float
    roi: float
    tax_savings: float

@dataclass
class PropertyExpenses:
    """Data class for property operating expenses."""
    property_tax: float
    insurance: float
    maintenance: float
    utilities: float
    hoa: float
    property_management: float

@dataclass
class PropertyInvestment:
    """Data class for property investment parameters."""
    purchase_price: float
    down_payment_pct: float
    interest_rates: List[Dict[str, float]]
    holding_period: int
    monthly_rent: float
    annual_rent_increase: float
    operating_expenses: PropertyExpenses
    vacancy_rate: float
