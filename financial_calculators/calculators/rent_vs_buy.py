from dataclasses import dataclass
from typing import Tuple, Dict, Any

import streamlit as st
from ui.input_handler import InputHandler
from ui.results_visualizer import ResultsVisualizer
from utils.financial_calculator import FinancialCalculator
from utils.constants import DEFAULT_VALUES


@dataclass
class MortgageCalculation:
    monthly_payment: float
    first_principal: float
    first_interest: float


def calculate_mortgage_details(house_price: float, down_payment_pct: float, interest_rate: float, years: int) -> MortgageCalculation:
    """Calculate initial mortgage details."""
    loan_amount = house_price * (1 - down_payment_pct/100)
    monthly_rate = interest_rate / (100 * 12)
    num_payments = years * 12

    if interest_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    first_interest = loan_amount * monthly_rate
    first_principal = monthly_payment - first_interest

    return MortgageCalculation(monthly_payment, first_principal, first_interest)


def display_header() -> int:
    """Display the calculator header and get simulation years."""
    st.title("Rent vs. Buy Calculator")
    st.write("Compare the financial implications of renting versus buying a home")
    
    years = st.number_input(
        'Simulation Years:',
        min_value=1,
        max_value=50,
        value=DEFAULT_VALUES['years'],
        help="Number of years to simulate the comparison"
    )
    st.session_state['simulation_years'] = years
    
    return years


def get_income() -> float:
    """Get the annual household income input."""
    return st.number_input(
        "Annual Household Income ($)",
        min_value=0,
        max_value=1000000,
        value=100000,
        step=1000,
        help="Total yearly household income before taxes"
    )


def handle_purchase_inputs() -> Tuple[Any, MortgageCalculation]:
    """Handle purchase-related inputs and calculations."""
    purchase_params = InputHandler.create_purchase_inputs()
    mortgage_details = calculate_mortgage_details(
        purchase_params.house_price,
        purchase_params.down_payment_pct,
        purchase_params.interest_rate,
        purchase_params.years
    )
    
    ResultsVisualizer.create_monthly_payment_chart(
        mortgage_details.monthly_payment,
        mortgage_details.first_principal,
        mortgage_details.first_interest
    )
    
    return purchase_params, mortgage_details


def handle_rental_inputs(down_payment: float) -> Any:
    """Handle rental-related inputs."""
    st.session_state['initial_investment'] = down_payment
    return InputHandler.create_rental_inputs()


def calculate_and_display_results(
    calculator: FinancialCalculator,
    purchase_params: Any,
    rental_params: Any,
    years: int
) -> None:
    """Calculate and display comparison results."""
    property_values, equity_values, purchase_details = calculator.calculate_purchase_scenario(purchase_params)
    rental_wealth, rental_details = calculator.calculate_rental_scenario(rental_params)

    ResultsVisualizer.create_comparison_chart(purchase_details, rental_details, years)
    
    params = {
        'down_payment_pct': purchase_params.down_payment_pct,
        'utilities': {
            'electricity': {'base': purchase_params.utilities.electricity.base},
            'water': {'base': purchase_params.utilities.water.base},
            'other': {'base': purchase_params.utilities.other.base}
        }
    }
    
    ResultsVisualizer.display_summary_statistics(
        purchase_details,
        rental_details,
        years,
        rental_params.initial_investment,
        params=params
    )

    save_results(purchase_details, rental_details, years, purchase_params, rental_params)


def save_results(
    purchase_details: Dict,
    rental_details: Dict,
    years: int,
    purchase_params: Any,
    rental_params: Any
) -> None:
    """Save calculation results to CSV."""
    purchase_params_dict = {
        'House_Price': purchase_params.house_price,
        'Down_Payment_Percent': purchase_params.down_payment_pct,
        'Interest_Rate': purchase_params.interest_rate,
        'Property_Tax_Rate': purchase_params.property_tax_rate,
        'Maintenance_Rate': purchase_params.maintenance_rate,
        'Insurance': purchase_params.insurance,
        'Property_Growth_Rate': purchase_params.appreciation_rate,
        'Monthly_Investment': purchase_params.monthly_investment,
        'Investment_Return': purchase_params.investment_return
    }

    rental_params_dict = {
        'Monthly_Rent': rental_params.monthly_rent,
        'Initial_Investment': rental_params.initial_investment,
        'Monthly_Investment': rental_params.monthly_investment,
        'Investment_Return': rental_params.investment_return,
        'Rent_Insurance': rental_params.rent_insurance,
        'Rent_Increase_Rate': rental_params.rent_inflation
    }

    ResultsVisualizer.save_results_to_csv(
        purchase_details,
        rental_details,
        years,
        purchase_params_dict,
        rental_params_dict
    )


def show() -> None:
    """Main function to display the rent vs buy calculator interface."""
    years = display_header()
    annual_income = get_income()

    col1, col2 = st.columns(2)

    with col1:
        purchase_params, mortgage_details = handle_purchase_inputs()

    with col2:
        rental_params = handle_rental_inputs(
            purchase_params.house_price * (purchase_params.down_payment_pct/100)
        )

    if st.button("Calculate Comparison", type="primary"):
        calculator = FinancialCalculator()
        calculate_and_display_results(calculator, purchase_params, rental_params, years)


if __name__ == "__main__":
    show()