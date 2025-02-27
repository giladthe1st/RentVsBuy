import streamlit as st

class InvestmentPropertyUIHandler:
    def __init__(self):
        pass

    def get_property_type(self) -> str:
        """
        Get the property type from the user.
        
        Returns:
            str: Selected property type
        """
        return st.selectbox(
            "Property Type",
            ["Single Family", "Multi-Family", "Condo"],
            help="Select the type of property you're analyzing"
        )

    def get_purchase_price(self) -> float:
        """
        Get the purchase price from the user.
        
        Returns:
            float: Purchase price of the property
        """
        purchase_price = float(st.number_input(
            "Purchase Price ($)",
            min_value=0,
            value=227000,
            step=1000,
            help="Enter the total purchase price of the property"
        ))
        # Store in session state for use in other methods
        st.session_state['purchase_price'] = purchase_price
        return purchase_price

    def get_down_payment_pct(self) -> float:
        """
        Get the down payment percentage from the user.
        
        Returns:
            float: Down payment percentage
        """
        down_payment_pct = float(st.number_input(
            "Down Payment (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            help="Percentage of purchase price as down payment"
        ))
        # Store in session state for use in other methods
        st.session_state['down_payment_pct'] = down_payment_pct
        return down_payment_pct

    def get_interest_rates(self) -> list:
        """
        Get the interest rates for different periods from the user.
        
        Returns:
            list[dict]: List of dicts with 'rate', 'years', and 'one_time_payment' keys
        """
        interest_rates = []
        
        st.markdown("### Mortgage Rate Details")
        
        num_rate_periods = int(st.number_input(
            "Number of Interest Rate Periods",
            min_value=1,
            max_value=10,
            value=1,
            help="Number of interest rate periods for the mortgage"
        ))
        
        # Get purchase price and down payment to calculate remaining principal
        purchase_price = st.session_state.get('purchase_price', 0)
        down_payment_pct = st.session_state.get('down_payment_pct', 0)
        loan_amount = purchase_price * (1 - down_payment_pct / 100)
        remaining_principal = loan_amount
        
        for i in range(num_rate_periods):
            rate_col1, rate_col2, rate_col3 = st.columns([2, 1, 2])
            with rate_col1:
                rate = float(st.number_input(
                    f"Interest Rate {i+1} (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=4.0,
                    step=0.1,
                    help=f"Interest rate for period {i+1}"
                ))
            with rate_col2:
                years = int(st.number_input(
                    f"Years for Rate {i+1}",
                    min_value=1,
                    max_value=30,
                    value=25,
                    step=1,
                    help=f"Number of years for interest rate {i+1}"
                ))
            with rate_col3:
                # Calculate max one-time payment based on remaining principal
                max_payment = remaining_principal
                one_time_payment = float(st.number_input(
                    f"One-Time Payment {i+1} ($)",
                    min_value=0.0,
                    max_value=float(max_payment),
                    value=0.0,
                    step=1000.0,
                    help=f"Optional one-time payment at the start of period {i+1}. Cannot exceed remaining loan amount: ${max_payment:.2f}"
                ))
                # Update remaining principal for next period
                remaining_principal = max(0, remaining_principal - one_time_payment)
            
            interest_rates.append({'rate': rate, 'years': years, 'one_time_payment': one_time_payment})
        
        return interest_rates

    def use_calculated_holding_period(self) -> bool:
        """
        Get the user's choice to use calculated or custom holding period.
        
        Returns:
            bool: True if user chooses calculated period, False otherwise
        """
        return st.checkbox("Option to use calculated or custom holding period", value=True)

    def get_custom_holding_period(self) -> int:
        """
        Get the custom holding period from the user.
        
        Returns:
            int: Custom holding period in years
        """
        return int(st.number_input(
            "Expected Holding Period (Years)",
            min_value=1,
            max_value=100,
            value=30,
            help="Enter your desired holding period"
        ))

    def get_monthly_rent(self) -> float:
        """
        Get the monthly rent from the user.
        
        Returns:
            float: Monthly rental income
        """
        return float(st.number_input(
            "Monthly Rent ($)",
            min_value=0,
            value=1650,
            step=100,
            help="Enter the expected monthly rental income"
        ))

    def get_annual_rent_increase(self) -> float:
        """
        Get the annual rent increase percentage from the user.
        
        Returns:
            float: Annual rent increase percentage
        """
        return float(st.number_input(
            "Annual Rent Increase (%)",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            help="Enter the expected annual rent increase percentage"
        ))

    def get_annual_inflation(self) -> float:
        """
        Get the annual inflation percentage from the user.
        
        Returns:
            float: Annual inflation percentage that will be applied to all expenses
        """
        return float(st.number_input(
            "Annual Inflation (%)",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            help="Enter the expected annual inflation percentage that will be applied to all expenses"
        ))

    def get_other_income(self) -> float:
        """
        Get the other monthly income from the user.
        
        Returns:
            float: Other monthly income
        """
        return float(st.number_input(
            "Other Monthly Income ($)",
            min_value=0,
            value=0,
            step=50,
            help="Additional income from parking, laundry, storage, etc."
        ))

    def get_vacancy_rate(self) -> float:
        """
        Get the vacancy rate from the user.
        
        Returns:
            float: Vacancy rate
        """
        return float(st.number_input(
            "Vacancy Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=8.0,
            step=0.1,
            help="Percentage of time the property is vacant"
        ))

    def get_property_tax(self, purchase_price: float) -> float:
        """
        Get the property tax from the user.
        
        Returns:
            float: Property tax
        """
        return float(st.number_input(
            "Annual Property Tax ($)",
            min_value=0.0,
            value=purchase_price * 0.01,
            step=100.0,
            help="Annual property tax amount",
            key="property_tax"
        ))

    def get_annual_insurance(self, purchase_price: float) -> float:
        """
        Get the annual insurance from the user.
        
        Returns:
            float: Annual insurance
        """
        return float(st.number_input(
            "Annual Insurance ($)",
            min_value=0.0,
            value=purchase_price * 0.0045,
            step=100.0,
            help="Annual property insurance cost",
            key="annual_insurance"
        ))

    def get_monthly_utilities(self) -> int:
        """
        Get the monthly utilities from the user.
        
        Returns:
            int: Monthly utilities
        """
        return int(st.number_input(
            "Monthly Utilities ($)",
            min_value=0,
            value=0,
            step=50,
            help="Monthly utilities cost (if paid by owner)",
            key="monthly_utilities"
        ))

    def get_monthly_hoa_fees(self) -> int:
        """
        Get the monthly HOA fees from the user.
        
        Returns:
            int: Monthly HOA fees
        """
        return int(st.number_input(
            "Monthly HOA Fees ($)",
            min_value=0,
            value=0,
            step=50,
            help="Monthly HOA fees",
            key="monthly_hoa_fees"
        ))
    
    def get_monthly_mgmt_fee(self) -> int:
        """
        Get the monthly management fee from the user.
        
        Returns:
            int: Monthly management fee
        """
        return int(st.number_input(
            "Monthly Property Management Fee ($)",
            min_value=0,
            value=150,
            step=50,
            help="Monthly property management fee",
            key="monthly_mgmt_fee"
        ))

    def get_maintenance_pct(self, purchase_price: int) -> float:
        """
        Get the maintenance percentage from the user.
        
        Returns:
            float: Maintenance percentage
        """
        return float(st.number_input(
            "Maintenance & Repairs (% of property value)",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Expected annual maintenance costs as percentage of property value",
            key="maintenance_pct"
        ))

    def get_annual_salary(self) -> float:
        """
        Get the annual salary from the user.
        
        Returns:
            float: Annual salary
        """
        return float(st.number_input(
            "Annual Salary ($)",
            min_value=0,
            value=80000,
            step=1000,
            help="Enter your annual salary for tax calculation",
            key="annual_salary"
        ))

    def get_salary_inflation(self) -> float:
        """
        Get the salary inflation from the user.
        
        Returns:
            float: Salary inflation
        """
        return float(st.number_input(
            "Salary Annual Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Expected annual increase in salary",
            key="salary_inflation"
        ))

    def get_conservative_rate(self) -> float:
        """
        Get the conservative rate from the user.
        
        Returns:
            float: Conservative rate
        """
        return float(st.number_input(
            "Conservative Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            help="Expected annual increase in salary",
            key="conservative_rate"
        ))

    def get_moderate_rate(self) -> float:
        """
        Get the moderate rate from the user.
        
        Returns:
            float: Moderate rate
        """
        return float(st.number_input(
            "Moderate Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help="Annual property value appreciation rate - moderate estimate",
            key="moderate_rate"
        ))
    
    def get_optimistic_rate(self) -> float:
        """
        Get the optimistic rate from the user.
        
        Returns:
            float: Optimistic rate
        """
        return float(st.number_input(
            "Optimistic Growth Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Annual property value appreciation rate - optimistic estimate",
            key="optimistic_rate"
        ))