# ui/input_handler.py

import streamlit as st
from typing import Tuple
from models.data_models import PurchaseScenarioParams, RentalScenarioParams, Utilities, UtilityData
from utils.constants import DEFAULT_VALUES
from translation_utils import translate_text, translate_number_input

class InputHandler:
    @staticmethod
    def create_purchase_inputs(current_lang: str = 'en') -> PurchaseScenarioParams:
        st.header(translate_text("Purchase Options", current_lang))
        
        house_price = translate_number_input(
            translate_text("House Price ($)", current_lang),
            current_lang,
            min_value=0,
            max_value=10000000,
            value=DEFAULT_VALUES['house_price'],
            step=1000,
            help=translate_text("Enter the total price of the house you're considering", current_lang),
            key="purchase_house_price"
        )

        interest_rate = translate_number_input(
            translate_text("Mortgage Interest Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=15.0,
            value=DEFAULT_VALUES['interest_rate'],
            step=0.1,
            help=translate_text("Annual mortgage interest rate", current_lang),
            key="purchase_interest_rate"
        )

        down_payment = translate_number_input(
            translate_text("Down Payment (%)", current_lang),
            current_lang,
            min_value=0,
            max_value=100,
            value=DEFAULT_VALUES['down_payment'],
            help=translate_text("Percentage of house price as down payment", current_lang),
            key="purchase_down_payment"
        )

        property_tax = translate_number_input(
            translate_text("Property Tax Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=5.0,
            value=DEFAULT_VALUES['property_tax'],
            step=0.1,
            help=translate_text("Annual property tax as percentage of house value", current_lang),
            key="purchase_property_tax"
        )

        maintenance_rate = translate_number_input(
            translate_text("Annual Maintenance (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=5.0,
            value=DEFAULT_VALUES['maintenance_rate'],
            step=0.1,
            help=translate_text("Annual maintenance and repairs as percentage of house value", current_lang),
            key="purchase_maintenance_rate"
        )

        long_term_growth = translate_number_input(
            translate_text("Property Appreciation Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=10.0,
            value=DEFAULT_VALUES['long_term_growth'],
            step=0.1,
            help=translate_text("Expected annual property value appreciation", current_lang),
            key="purchase_appreciation_rate"
        )

        col_homeins1, col_homeins_inflation = st.columns(2)
        with col_homeins1:
            insurance = translate_number_input(
                translate_text("Annual Insurance ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=DEFAULT_VALUES['insurance'],
                step=100,
                key="purchase_insurance"
            )
        with col_homeins_inflation:
            insurance_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['insurance_inflation'],
                step=0.1,
                key="purchase_insurance_inflation"
            )

        col_inv_purchase1, col_inv_purchase_inflation = st.columns(2)
        with col_inv_purchase1:
            monthly_investment = translate_number_input(
                translate_text("Monthly Investment ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                key="purchase_monthly_investment"
            )
        with col_inv_purchase_inflation:
            investment_increase_rate = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="purchase_investment_increase"
            )

        investment_return = translate_number_input(
            translate_text("Investment Return Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=20.0,
            value=DEFAULT_VALUES['investment_return'],
            step=0.1,
            help=translate_text("Expected annual return on investments", current_lang),
            key="purchase_investment_return"
        )

        utilities_data = InputHandler._create_utilities_inputs("Purchase", current_lang)

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
    def create_rental_inputs(current_lang: str = 'en') -> RentalScenarioParams:
        st.header(translate_text("Rental Options", current_lang))

        # Display Initial Investment (from down payment)
        initial_investment = st.session_state.get('initial_investment', 0)
        st.markdown(translate_text("**Initial Investment**", current_lang))
        st.markdown(f"${initial_investment:,.2f}")
        st.markdown(translate_text("*(Equal to down payment amount)*", current_lang))
        st.markdown("---")

        col_rent1, col_rent_inflation = st.columns(2)
        with col_rent1:
            monthly_rent = translate_number_input(
                translate_text("Monthly Rent ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=DEFAULT_VALUES['monthly_rent'],
                step=100,
                key="rental_monthly_rent"
            )
        with col_rent_inflation:
            rent_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['rent_inflation'],
                step=0.1,
                key="rental_rent_inflation"
            )

        col_rent_ins1, col_rent_ins_inflation = st.columns(2)
        with col_rent_ins1:
            rent_insurance = translate_number_input(
                translate_text("Renter's Insurance ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=10000,
                value=DEFAULT_VALUES['rent_insurance'],
                step=50,
                key="rental_insurance"
            )
        with col_rent_ins_inflation:
            rent_insurance_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['rent_insurance_inflation'],
                step=0.1,
                key="rental_insurance_inflation"
            )

        col_inv_rental1, col_inv_rental_inflation = st.columns(2)
        with col_inv_rental1:
            monthly_investment = translate_number_input(
                translate_text("Monthly Investment ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                key="rental_monthly_investment"
            )
        with col_inv_rental_inflation:
            investment_increase_rate = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                key="rental_investment_increase"
            )

        investment_return = translate_number_input(
            translate_text("Investment Return Rate (%)", current_lang),
            current_lang,
            min_value=0.0,
            max_value=20.0,
            value=DEFAULT_VALUES['investment_return'],
            step=0.1,
            help=translate_text("Expected annual return on investments", current_lang),
            key="rental_investment_return"
        )

        utilities_data = InputHandler._create_utilities_inputs("Rental", current_lang)

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
    def _create_utilities_inputs(scenario_type: str, current_lang: str = 'en') -> Utilities:
        st.markdown(translate_text(f"### Monthly Utilities", current_lang))
        
        # Electricity
        col_utility1, col_inflation1 = st.columns(2)
        with col_utility1:
            electricity_base = translate_number_input(
                translate_text("Electricity ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=1000,
                value=DEFAULT_VALUES['utilities']['electricity']['base'],
                step=10,
                key=f"{scenario_type.lower()}_electricity"
            )
        with col_inflation1:
            electricity_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['utilities']['electricity']['inflation'],
                step=0.1,
                key=f"{scenario_type.lower()}_electricity_inflation"
            )

        # Water
        col_utility2, col_inflation2 = st.columns(2)
        with col_utility2:
            water_base = translate_number_input(
                translate_text("Water ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=500,
                value=DEFAULT_VALUES['utilities']['water']['base'],
                step=10,
                key=f"{scenario_type.lower()}_water"
            )
        with col_inflation2:
            water_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
                min_value=0.0,
                max_value=10.0,
                value=DEFAULT_VALUES['utilities']['water']['inflation'],
                step=0.1,
                key=f"{scenario_type.lower()}_water_inflation"
            )

        # Other expenses
        col_utility3, col_inflation3 = st.columns(2)
        with col_utility3:
            other_base = translate_number_input(
                translate_text("Other Monthly Expenses ($)", current_lang),
                current_lang,
                min_value=0,
                max_value=1000,
                value=DEFAULT_VALUES['utilities']['other']['base'],
                step=10,
                key=f"{scenario_type.lower()}_other"
            )
        with col_inflation3:
            other_inflation = translate_number_input(
                translate_text("Annual Increase (%)", current_lang),
                current_lang,
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