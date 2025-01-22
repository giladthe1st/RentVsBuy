from dataclasses import dataclass
from typing import Dict, List
from .data_models import PurchaseScenarioParams, RentalScenarioParams

@dataclass
class YearlyPurchaseDetails:
    year: int
    property_value: float
    yearly_mortgage: float
    property_tax: float
    maintenance: float
    insurance: float
    interest_paid: float
    principal_paid: float
    remaining_loan: float
    equity: float
    yearly_costs: float
    total_interest_to_date: float
    total_principal_to_date: float
    investment_portfolio: float
    investment_returns: float
    new_investments: float
    yearly_utilities: float

@dataclass
class YearlyRentalDetails:
    year: int
    yearly_rent: float
    rent_insurance: float
    investment_portfolio: float
    investment_returns: float
    new_investments: float
    net_wealth: float
    yearly_costs: float
    yearly_utilities: float