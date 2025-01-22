from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PropertyDetails:
    """Data model for basic property details."""
    property_type: str
    purchase_price: float
    down_payment_pct: float
    interest_rate: float
    loan_years: int
    holding_period: int

@dataclass
class IncomeDetails:
    """Data model for property income details."""
    monthly_rent: float
    other_income: float
    vacancy_rate: float
    annual_rent_increase: float

@dataclass
class ExpenseDetails:
    """Data model for property operating expenses."""
    property_tax: float
    insurance: float
    utilities: float
    management_fee: float
    maintenance_pct: float
    hoa_fees: float

@dataclass
class MortgageDetails:
    """Data model for mortgage calculation results."""
    loan_amount: float
    monthly_payment: float
    interest_payment: float
    principal_payment: float
    remaining_balance: float

@dataclass
class AppreciationScenario:
    """Data model for property appreciation scenarios."""
    conservative_rate: float
    moderate_rate: float
    optimistic_rate: float

@dataclass
class CashFlowProjection:
    """Data model for annual cash flow projections."""
    year: int
    monthly_rent: float
    monthly_income: float
    vacancy_loss: float
    effective_income: float
    mortgage_payment: float
    operating_expenses: float
    net_cash_flow: float

@dataclass
class InvestmentMetrics:
    """Data model for key investment metrics."""
    noi: float
    cap_rate: float
    cash_on_cash_return: float
    conservative_irr: float
    moderate_irr: float
    optimistic_irr: float

@dataclass
class EquityMetrics:
    """Data model for equity-related metrics."""
    down_payment: float
    total_equity_buildup: float
    yearly_equity: List[float]

@dataclass
class InvestmentAnalysis:
    """Complete investment property analysis results."""
    property_details: PropertyDetails
    income_details: IncomeDetails
    expense_details: ExpenseDetails
    mortgage_details: MortgageDetails
    appreciation_scenario: AppreciationScenario
    cash_flow_projections: List[CashFlowProjection]
    investment_metrics: InvestmentMetrics
    equity_metrics: EquityMetrics
    
    def calculate_total_cash_flow(self) -> float:
        """Calculate total cash flow over the holding period."""
        return sum(cf.net_cash_flow for cf in self.cash_flow_projections)
    
    def calculate_average_cash_flow(self) -> float:
        """Calculate average annual cash flow."""
        total = self.calculate_total_cash_flow()
        return total / len(self.cash_flow_projections) if self.cash_flow_projections else 0.0
    
    def get_conservative_value_projection(self) -> List[float]:
        """Calculate conservative property value projection."""
        return [
            self.property_details.purchase_price * 
            (1 + self.appreciation_scenario.conservative_rate/100) ** year
            for year in range(self.property_details.holding_period + 1)
        ]
    
    def get_moderate_value_projection(self) -> List[float]:
        """Calculate moderate property value projection."""
        return [
            self.property_details.purchase_price * 
            (1 + self.appreciation_scenario.moderate_rate/100) ** year
            for year in range(self.property_details.holding_period + 1)
        ]
    
    def get_optimistic_value_projection(self) -> List[float]:
        """Calculate optimistic property value projection."""
        return [
            self.property_details.purchase_price * 
            (1 + self.appreciation_scenario.optimistic_rate/100) ** year
            for year in range(self.property_details.holding_period + 1)
        ]