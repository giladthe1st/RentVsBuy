# ui/input_handler.py

import streamlit as st
from typing import Tuple
from financial_calculators.models.data_models import PurchaseScenarioParams, RentalScenarioParams, Utilities, UtilityData
from financial_calculators.utils.constants import DEFAULT_VALUES, CLOSING_COSTS, CLOSING_COSTS_INFO_URL
from financial_calculators.utils.financial_calculator import FinancialCalculator

class InputHandler:
    @staticmethod
    def create_purchase_inputs() -> PurchaseScenarioParams:
        """Create and handle purchase scenario inputs"""
        st.header("Purchase Options")
        
        st.subheader("Purchase Details")

        house_price = st.number_input(
            "House Price ($)",
            min_value=0,
            max_value=10000000,
            value=DEFAULT_VALUES['house_price'],
            step=1000,
            help="Total purchase price of the home",
            key="purchase_house_price"
        )

        # Calculate and display closing costs
        closing_costs = FinancialCalculator.calculate_closing_costs(house_price)
        with st.expander("View Closing Costs Breakdown"):
            st.markdown(f"""
            #### One-Time Closing Costs
            - Legal Fees: ${closing_costs['legal_fees']:,.2f}
            - Bank Appraisal Fee: ${closing_costs['bank_appraisal_fee']:,.2f}
            - Interest Adjustment: ${closing_costs['interest_adjustment']:,.2f}
            - Title Insurance: ${closing_costs['title_insurance']:,.2f}
            - Land Transfer Tax: ${closing_costs['land_transfer_tax']:,.2f}
            
            **Total Closing Costs: ${closing_costs['total']:,.2f}**
            
            [Learn more about closing costs]({CLOSING_COSTS_INFO_URL})
            """)

        down_payment = st.number_input(
            "Down Payment (%)",
            min_value=0,
            max_value=100,
            value=DEFAULT_VALUES['down_payment'],
            help="Percentage of house price as down payment",
            key="purchase_down_payment"
        )

        interest_rate = st.number_input(
            "Mortgage Interest Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=DEFAULT_VALUES['interest_rate'],
            step=0.1,
            help="Annual mortgage interest rate",
            key="purchase_interest_rate"
        )

        property_tax = st.number_input(
            "Property Tax Rate (%)",
            min_value=0.0,
            max_value=5.0,
            value=DEFAULT_VALUES['property_tax'],
            step=0.1,
            help="Annual property tax as percentage of house value",
            key="purchase_property_tax"
        )

        maintenance_rate = st.number_input(
            "Annual Maintenance (%)",
            min_value=0.0,
            max_value=5.0,
            value=DEFAULT_VALUES['maintenance_rate'],
            step=0.1,
            help="Annual maintenance and repairs as percentage of house value",
            key="purchase_maintenance_rate"
        )

        long_term_growth = st.number_input(
            "Property Appreciation Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=DEFAULT_VALUES['long_term_growth'],
            step=0.1,
            help="Expected annual property value appreciation",
            key="purchase_appreciation_rate"
        )

        col_homeins1, col_homeins_inflation = st.columns(2)
        with col_homeins1:
            insurance = st.number_input(
                "Annual Insurance ($)",
                min_value=0,
                max_value=50000,
                value=DEFAULT_VALUES['insurance'],
                step=100,
                key="purchase_insurance"
            )
        with col_homeins_inflation:
            insurance_inflation = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['insurance_inflation'],
                step=0.1,
                key="purchase_insurance_inflation"
            )

        col_inv_purchase1, col_inv_purchase_inflation = st.columns(2)
        with col_inv_purchase1:
            monthly_investment = st.number_input(
                "Monthly Investment ($)",
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                key="purchase_monthly_investment"
            )
        with col_inv_purchase_inflation:
            investment_increase_rate = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="purchase_investment_increase"
            )

        investment_return = st.number_input(
            "Investment Return Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=DEFAULT_VALUES['investment_return'],
            step=0.1,
            help="Expected annual return on investments",
            key="purchase_investment_return"
        )

        utilities_data = InputHandler._create_utilities_inputs("Purchase")

        # Calculate total monthly expenses
        loan_amount = house_price * (1 - down_payment/100)
        monthly_payment = FinancialCalculator.calculate_monthly_mortgage_payment(
            loan_amount, interest_rate, st.session_state.get('simulation_years', DEFAULT_VALUES['years'])
        )
        monthly_property_tax = (house_price * property_tax / 100) / 12
        monthly_maintenance = (house_price * maintenance_rate / 100) / 12
        monthly_insurance = insurance / 12
        monthly_utilities = (utilities_data.electricity.base + utilities_data.water.base + utilities_data.other.base)
        
        total_monthly_expenses = monthly_payment + monthly_property_tax + monthly_maintenance + monthly_insurance + monthly_utilities
        total_monthly_with_investment = total_monthly_expenses + monthly_investment

        # Display monthly breakdown
        st.subheader("Monthly Payment Breakdown")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            #### Required Monthly Expenses
            - Mortgage Payment: **${monthly_payment:,.2f}**
            - Property Tax: **${monthly_property_tax:,.2f}**
            - Maintenance: **${monthly_maintenance:,.2f}**
            - Insurance: **${monthly_insurance:,.2f}**
            - Utilities: **${monthly_utilities:,.2f}**
            
            #### Optional Investment
            - Monthly Investment: **${monthly_investment:,.2f}**
            """)
        
        with col2:
            st.markdown(f"""
            ### Required Monthly
            ## ${total_monthly_expenses:,.2f}
            
            ### With Investment
            ## ${total_monthly_with_investment:,.2f}
            """)

        return PurchaseScenarioParams(
            house_price=house_price,
            down_payment_pct=down_payment,
            interest_rate=interest_rate,
            years=st.session_state.get('simulation_years', DEFAULT_VALUES['years']),
            property_tax_rate=property_tax,
            maintenance_rate=maintenance_rate,
            insurance=insurance,
            insurance_inflation=insurance_inflation,
            appreciation_rate=long_term_growth,
            monthly_investment=monthly_investment,
            investment_return=investment_return,
            investment_increase_rate=investment_increase_rate,
            utilities=utilities_data
        )

    @staticmethod
    def create_rental_inputs() -> RentalScenarioParams:
        st.header("Rental Options")

        # Display Initial Investment (from down payment)
        initial_investment = st.session_state.get('initial_investment', 0)
        st.markdown("**Initial Investment**")
        st.markdown(f"${initial_investment:,.2f}")
        st.markdown("*(Equal to down payment amount)*")
        st.markdown("---")

        col_rent1, col_rent_inflation = st.columns(2)
        with col_rent1:
            monthly_rent = st.number_input(
                "Monthly Rent ($)",
                min_value=0,
                max_value=50000,
                value=DEFAULT_VALUES['monthly_rent'],
                step=100,
                key="rental_monthly_rent"
            )
        with col_rent_inflation:
            rent_inflation = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['rent_inflation'],
                step=0.1,
                key="rental_rent_inflation"
            )

        col_rent_ins1, col_rent_ins_inflation = st.columns(2)
        with col_rent_ins1:
            rent_insurance = st.number_input(
                "Renter's Insurance ($)",
                min_value=0,
                max_value=10000,
                value=DEFAULT_VALUES['rent_insurance'],
                step=50,
                key="rental_insurance"
            )
        with col_rent_ins_inflation:
            rent_insurance_inflation = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['rent_insurance_inflation'],
                step=0.1,
                key="rental_insurance_inflation"
            )

        col_inv_rental1, col_inv_rental_inflation = st.columns(2)
        with col_inv_rental1:
            monthly_investment = st.number_input(
                "Monthly Investment ($)",
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                key="rental_monthly_investment"
            )
        with col_inv_rental_inflation:
            investment_increase_rate = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="rental_investment_increase"
            )

        investment_return = st.number_input(
            "Investment Return Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=DEFAULT_VALUES['investment_return'],
            step=0.1,
            help="Expected annual return on investments",
            key="rental_investment_return"
        )

        utilities_data = InputHandler._create_utilities_inputs("Rental")

        # Calculate total monthly expenses
        monthly_utilities = (utilities_data.electricity.base + utilities_data.water.base + utilities_data.other.base)
        monthly_insurance = rent_insurance / 12
        total_monthly_expenses = monthly_rent + monthly_utilities + monthly_insurance
        total_monthly_with_investment = total_monthly_expenses + monthly_investment

        # Display monthly breakdown
        st.subheader("Monthly Payment Breakdown")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            #### Required Monthly Expenses
            - Rent: **${monthly_rent:,.2f}**
            - Insurance: **${monthly_insurance:,.2f}**
            - Utilities: **${monthly_utilities:,.2f}**
            
            #### Optional Investment
            - Monthly Investment: **${monthly_investment:,.2f}**
            """)
        
        with col2:
            st.markdown(f"""
            ### Required Monthly
            ## ${total_monthly_expenses:,.2f}
            
            ### With Investment
            ## ${total_monthly_with_investment:,.2f}
            """)

        return RentalScenarioParams(
            monthly_rent=monthly_rent,
            rent_inflation=rent_inflation,
            monthly_investment=monthly_investment,
            investment_increase_rate=investment_increase_rate,
            years=st.session_state.get('simulation_years', DEFAULT_VALUES['years']),
            investment_return=investment_return,
            rent_insurance=rent_insurance,
            rent_insurance_inflation=rent_insurance_inflation,
            utilities=utilities_data,
            initial_investment=st.session_state.get('initial_investment', 0)
        )

    @staticmethod
    def _create_utilities_inputs(scenario_type: str) -> Utilities:
        st.markdown(f"### Monthly Utilities")
        
        # Electricity
        col_utility1, col_inflation1 = st.columns(2)
        with col_utility1:
            electricity_base = st.number_input(
                "Electricity ($)",
                min_value=0,
                max_value=1000,
                value=DEFAULT_VALUES['utilities']['electricity']['base'],
                step=10,
                key=f"{scenario_type.lower()}_electricity"
            )
        with col_inflation1:
            electricity_inflation = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['utilities']['electricity']['inflation'],
                step=0.1,
                key=f"{scenario_type.lower()}_electricity_inflation"
            )

        # Water
        col_utility2, col_inflation2 = st.columns(2)
        with col_utility2:
            water_base = st.number_input(
                "Water ($)",
                min_value=0,
                max_value=500,
                value=DEFAULT_VALUES['utilities']['water']['base'],
                step=10,
                key=f"{scenario_type.lower()}_water"
            )
        with col_inflation2:
            water_inflation = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['utilities']['water']['inflation'],
                step=0.1,
                key=f"{scenario_type.lower()}_water_inflation"
            )

        # Other expenses
        col_utility3, col_inflation3 = st.columns(2)
        with col_utility3:
            other_base = st.number_input(
                "Other Monthly Expenses ($)",
                min_value=0,
                max_value=1000,
                value=DEFAULT_VALUES['utilities']['other']['base'],
                step=10,
                key=f"{scenario_type.lower()}_other"
            )
        with col_inflation3:
            other_inflation = st.number_input(
                "Annual Increase (%)",
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['utilities']['other']['inflation'],
                step=0.1,
                key=f"{scenario_type.lower()}_other_inflation"
            )

        return Utilities(
            electricity=UtilityData(base=electricity_base, inflation=electricity_inflation),
            water=UtilityData(base=water_base, inflation=water_inflation),
            other=UtilityData(base=other_base, inflation=other_inflation)
        )