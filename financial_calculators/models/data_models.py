from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class UtilityData:
    base: float
    inflation: float

@dataclass
class Utilities:
    electricity: UtilityData
    water: UtilityData
    other: UtilityData

@dataclass
class PurchaseScenarioParams:
    house_price: float
    down_payment_pct: float
    interest_rate: float
    years: int
    property_tax_rate: float
    maintenance_rate: float
    insurance: float
    insurance_inflation: float
    appreciation_rate: float
    monthly_investment: float
    investment_return: float
    investment_increase_rate: float
    utilities: Utilities

@dataclass
class RentalScenarioParams:
    monthly_rent: float
    rent_inflation: float
    monthly_investment: float
    investment_increase_rate: float
    years: int
    investment_return: float
    rent_insurance: float
    rent_insurance_inflation: float
    utilities: Utilities
    initial_investment: float = 0