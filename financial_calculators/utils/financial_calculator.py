from typing import List, Tuple, Dict, Any
from models.data_models import PurchaseScenarioParams, RentalScenarioParams, Utilities
from models.rent_vs_buy_models import YearlyPurchaseDetails, YearlyRentalDetails
from utils.constants import CLOSING_COSTS

class FinancialCalculator:
    @staticmethod
    def calculate_purchase_scenario(params: PurchaseScenarioParams) -> Tuple[List[float], List[float], List[YearlyPurchaseDetails]]:
        down_payment = params.house_price * (params.down_payment_pct / 100)
        loan_amount = params.house_price - down_payment
        monthly_rate = params.interest_rate / (100 * 12)
        num_payments = params.years * 12

        # Calculate closing costs
        closing_costs = FinancialCalculator.calculate_closing_costs(params.house_price)
        initial_costs = closing_costs['total']

        investment_portfolio = 0
        current_monthly_investment = params.monthly_investment

        monthly_payment = FinancialCalculator.calculate_monthly_mortgage_payment(loan_amount, params.interest_rate, params.years)

        property_values = []
        equity_values = []
        remaining_loan = loan_amount
        yearly_details = []
        
        total_interest_to_date = 0
        total_principal_to_date = 0
        current_insurance = params.insurance

        for year in range(params.years):
            # Update insurance with inflation
            current_insurance *= (1 + params.insurance_inflation/100)
            
            # Calculate utilities with inflation for this year
            current_utilities = {
                'electricity': params.utilities.electricity.base * 
                             (1 + params.utilities.electricity.inflation/100)**year,
                'water': params.utilities.water.base * 
                        (1 + params.utilities.water.inflation/100)**year,
                'other': params.utilities.other.base * 
                        (1 + params.utilities.other.inflation/100)**year
            }
            yearly_utilities = sum(current_utilities.values()) * 12

            current_home_value = params.house_price * (1 + params.appreciation_rate/100)**year
            yearly_tax = current_home_value * (params.property_tax_rate/100)
            yearly_maintenance = current_home_value * (params.maintenance_rate/100)
            yearly_mortgage = monthly_payment * 12

            yearly_interest_paid = 0
            yearly_principal_paid = 0
            for _ in range(12):
                interest_payment = remaining_loan * monthly_rate
                principal_payment = monthly_payment - interest_payment
                remaining_loan = max(0, remaining_loan - principal_payment)
                yearly_interest_paid += interest_payment
                yearly_principal_paid += principal_payment

            equity = current_home_value - remaining_loan
            
            # Update monthly investment amount with inflation
            current_monthly_investment *= (1 + params.investment_increase_rate/100)
            yearly_investment = current_monthly_investment * 12
            
            investment_returns = investment_portfolio * (params.investment_return/100)
            investment_portfolio = investment_portfolio * (1 + params.investment_return/100) + yearly_investment

            # Add closing costs to first year's total costs
            total_yearly_costs = (yearly_mortgage + yearly_tax + yearly_maintenance + 
                                current_insurance + yearly_utilities)
            if year == 0:
                total_yearly_costs += initial_costs

            total_interest_to_date += yearly_interest_paid
            total_principal_to_date += yearly_principal_paid

            yearly_details.append(YearlyPurchaseDetails(
                year=year + 1,
                property_value=current_home_value,
                yearly_mortgage=yearly_mortgage,
                property_tax=yearly_tax,
                maintenance=yearly_maintenance,
                insurance=current_insurance,
                interest_paid=yearly_interest_paid,
                principal_paid=yearly_principal_paid,
                remaining_loan=remaining_loan,
                equity=equity,
                yearly_costs=total_yearly_costs,
                total_interest_to_date=total_interest_to_date,
                total_principal_to_date=total_principal_to_date,
                investment_portfolio=investment_portfolio,
                investment_returns=investment_returns,
                new_investments=yearly_investment,
                yearly_utilities=yearly_utilities,
                closing_costs=initial_costs if year == 0 else 0
            ))

            property_values.append(current_home_value)
            equity_values.append(equity)

        return property_values, equity_values, yearly_details

    @staticmethod
    def calculate_monthly_mortgage_payment(loan_amount: float, interest_rate: float, years: int) -> float:
        """Calculate the monthly mortgage payment.
        
        Args:
            loan_amount: The total amount of the loan
            interest_rate: Annual interest rate as a percentage (e.g., 5.5 for 5.5%)
            years: The term of the loan in years
            
        Returns:
            Monthly payment amount
        """
        monthly_rate = interest_rate / (100 * 12)
        num_payments = years * 12

        if interest_rate == 0:
            return loan_amount / num_payments
        else:
            return loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    @staticmethod
    def calculate_closing_costs(house_price: float) -> Dict[str, float]:
        """Calculate closing costs for a home purchase."""
        # Fixed costs
        costs = {
            'legal_fees': CLOSING_COSTS['legal_fees'],
            'bank_appraisal_fee': CLOSING_COSTS['bank_appraisal_fee'],
            'interest_adjustment': CLOSING_COSTS['interest_adjustment'],
            'title_insurance': CLOSING_COSTS['title_insurance']
        }
        
        # Calculate land transfer tax
        if house_price <= CLOSING_COSTS['land_transfer_threshold']:
            land_transfer_tax = CLOSING_COSTS['land_transfer_base']
        else:
            excess_amount = house_price - CLOSING_COSTS['land_transfer_threshold']
            land_transfer_tax = (CLOSING_COSTS['land_transfer_base'] + 
                               excess_amount * CLOSING_COSTS['land_transfer_rate'])
        
        costs['land_transfer_tax'] = land_transfer_tax
        costs['total'] = sum(costs.values())
        
        return costs

    @staticmethod
    def calculate_rental_scenario(params: RentalScenarioParams) -> Tuple[List[float], List[YearlyRentalDetails]]:
        wealth_values = []
        investment_portfolio = params.initial_investment
        yearly_details = []
        
        current_monthly_investment = params.monthly_investment
        current_rent = params.monthly_rent
        current_insurance = params.rent_insurance

        for year in range(params.years):
            # Update rent insurance with inflation
            current_insurance *= (1 + params.rent_insurance_inflation/100)
            
            # Calculate utilities with inflation for this year
            current_utilities = {
                'electricity': params.utilities.electricity.base * 
                             (1 + params.utilities.electricity.inflation/100)**year,
                'water': params.utilities.water.base * 
                        (1 + params.utilities.water.inflation/100)**year,
                'other': params.utilities.other.base * 
                        (1 + params.utilities.other.inflation/100)**year
            }
            yearly_utilities = sum(current_utilities.values()) * 12

            # Update rent with inflation
            current_rent *= (1 + params.rent_inflation/100)
            yearly_rent = current_rent * 12
            
            # Update investment amount with inflation
            current_monthly_investment *= (1 + params.investment_increase_rate/100)
            yearly_investment = current_monthly_investment * 12

            yearly_costs = yearly_rent + current_insurance + yearly_utilities

            investment_returns = investment_portfolio * (params.investment_return/100)
            investment_portfolio = investment_portfolio * (1 + params.investment_return/100) + yearly_investment

            current_wealth = investment_portfolio

            wealth_values.append(current_wealth)

            yearly_details.append(YearlyRentalDetails(
                year=year + 1,
                yearly_rent=yearly_rent,
                rent_insurance=current_insurance,
                investment_portfolio=investment_portfolio,
                investment_returns=investment_returns,
                new_investments=yearly_investment,
                net_wealth=current_wealth,
                yearly_costs=yearly_costs,
                yearly_utilities=yearly_utilities
            ))

        return wealth_values, yearly_details