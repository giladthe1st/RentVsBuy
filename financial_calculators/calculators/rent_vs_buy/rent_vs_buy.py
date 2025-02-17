import os
import streamlit as st
from ui.ui_handlers.rent_vs_buy_ui_handler import RentVsBuyUIHandler
from ui.results_visualizer import ResultsVisualizer
from utils.financial_calculator import FinancialCalculator
from utils.constants import DEFAULT_VALUES

def show():
    """Main function to display the rent vs buy calculator interface."""
    
    # Check if we're in deployment environment
    is_deployed = os.getenv('DEPLOYMENT_ENV') == 'production'
    
    st.title("Rent vs. Buy Calculator")
    st.write("Compare the financial implications of renting versus buying a home")

    # Get simulation years input
    years = st.number_input(
        'Simulation Years:',
        min_value=1,
        max_value=50,
        value=DEFAULT_VALUES['years'],
        help="Number of years to simulate the comparison"
    )
    st.session_state['simulation_years'] = years

    # Get annual income input
    annual_income = st.number_input(
        "Annual Household Income ($)",
        min_value=0,
        max_value=1000000,
        value=100000,
        step=1000,
        help="Total yearly household income before taxes"
    )

    # Create two columns for the layout
    col1, col2 = st.columns(2)

    # Purchase inputs in left column
    with col1:
        purchase_params = RentVsBuyUIHandler.create_purchase_inputs()

        # Calculate and display initial mortgage details
        loan_amount = purchase_params.house_price * (1 - purchase_params.down_payment_pct/100)
        monthly_rate = purchase_params.interest_rate / (100 * 12)
        num_payments = purchase_params.years * 12

        if purchase_params.interest_rate == 0:
            monthly_payment = loan_amount / num_payments
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

        # Calculate first month's interest and principal
        first_interest = loan_amount * monthly_rate
        first_principal = monthly_payment - first_interest

        # Display monthly payment breakdown visualization
        ResultsVisualizer.create_monthly_payment_chart(
            monthly_payment,
            first_principal,
            first_interest
        )

    # Rental inputs in middle column
    with col2:
        # Set initial investment based on purchase down payment
        st.session_state['initial_investment'] = purchase_params.house_price * (purchase_params.down_payment_pct/100)
        rental_params = InputHandler.create_rental_inputs()

    # Calculate comparison when button is clicked
    if st.button("Calculate Comparison", type="primary"):
        # Initialize calculator
        calculator = FinancialCalculator()
        
        # Calculate scenarios
        property_values, equity_values, purchase_details = calculator.calculate_purchase_scenario(
            purchase_params
        )
        
        rental_wealth, rental_details = calculator.calculate_rental_scenario(
            rental_params
        )

        # Display results
        ResultsVisualizer.create_comparison_chart(
            purchase_details,
            rental_details,
            years
        )
        
        ResultsVisualizer.display_summary_statistics(
            purchase_details,
            rental_details,
            years,
            rental_params.initial_investment,
            params={
                'down_payment_pct': purchase_params.down_payment_pct,
                'utilities': {
                    'electricity': {'base': purchase_params.utilities.electricity.base},
                    'water': {'base': purchase_params.utilities.water.base},
                    'other': {'base': purchase_params.utilities.other.base}
                }
            }
        )

        # Save results to CSV
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

if __name__ == "__main__":
    show()