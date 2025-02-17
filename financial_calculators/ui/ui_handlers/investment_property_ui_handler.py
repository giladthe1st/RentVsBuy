import streamlit as st
from utils.financial_calculator import FinancialCalculator

class InvestmentPropertyUIHandler:
    def handle_property_details(self):
        def create_property_type_input(self) -> str:
            property_type = st.selectbox(
                "Property Type",
                ["Single Family", "Multi-Family", "Condo"],
                help="Select the type of property you're analyzing"
            )
            return property_type

        def create_purchase_inputs(self) -> dict:
            purchase_price = float(st.number_input(
                "Purchase Price ($)",
                min_value=0,
                value=300000,
                step=1000,
                help="Enter the total purchase price of the property"
            ))
            
            # Calculate and display closing costs
            closing_costs = FinancialCalculator.calculate_closing_costs(purchase_price)
            with st.expander("View Closing Costs Breakdown"):
                st.markdown(f"""
                #### One-Time Closing Costs
                - Legal Fees: ${closing_costs['legal_fees']:,.2f}
                - Bank Appraisal Fee: ${closing_costs['bank_appraisal_fee']:,.2f}
                - Interest Adjustment: ${closing_costs['interest_adjustment']:,.2f}
                - Title Insurance: ${closing_costs['title_insurance']:,.2f}
                - Land Transfer Tax: ${closing_costs['land_transfer_tax']:,.2f}
                
                **Total Closing Costs: ${closing_costs['total']:,.2f}**
                """)
            
            return {
                "purchase_price": purchase_price,
                "closing_costs": closing_costs
            }

        def create_down_payment_input(self) -> tuple:
            down_payment_pct = float(st.number_input(
                "Down Payment (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
                help="Percentage of purchase price as down payment"
            ))
            purchase_price = float(st.number_input(
                "Purchase Price ($)",
                min_value=0,
                value=300000,
                step=1000,
                help="Enter the total purchase price of the property"
            ))
            down_payment_amount = purchase_price * (down_payment_pct / 100)
            st.markdown(f"Down Payment Amount: **${down_payment_amount:,.2f}**")
            
            return down_payment_pct, down_payment_amount

        def create_interest_rate_inputs(self) -> list:
            interest_rates = []
            num_rate_periods = int(st.number_input(
                "Number of Interest Rate Periods",
                min_value=1,
                max_value=10,
                value=1,
                help="Number of interest rate periods for the mortgage"
            ))
            
            for i in range(num_rate_periods):
                rate_col1, rate_col2 = st.columns([2, 1])
                with rate_col1:
                    rate = float(st.number_input(
                        f"Interest Rate {i+1} (%)",
                        min_value=0.0,
                        max_value=20.0,
                        value=4.0,
                        step=0.1,
                        help=f"Annual interest rate for period {i+1}"
                    ))
                with rate_col2:
                    years = int(st.number_input(
                        f"Years for Rate {i+1}",
                        min_value=1,
                        max_value=40,
                        value=30,
                        help=f"Number of years for interest rate {i+1}"
                    ))
                interest_rates.append({'rate': rate, 'years': years})
            
            return interest_rates

        def create_holding_period_input(self, interest_rates: list) -> int:
            use_calculated_period = st.checkbox(
                "Use calculated holding period based on interest rate periods",
                value=True
            )

            if use_calculated_period:
                total_holding_period = sum(rate['years'] for rate in interest_rates)
                st.markdown(f"Expected Holding Period (Years): **{total_holding_period}**")
            else:
                total_holding_period = int(st.number_input(
                    "Expected Holding Period (Years)",
                    min_value=1,
                    max_value=100,
                    value=30,
                    help="Enter your desired holding period"
                ))
            
            return total_holding_period
            
        # Execute all property detail inputs
        property_type = create_property_type_input(self)
        purchase_details = create_purchase_inputs(self)
        down_payment = create_down_payment_input(self)
        interest_rates = create_interest_rate_inputs(self)
        holding_period = create_holding_period_input(self, interest_rates)
        
        return {
            "property_type": property_type,
            "purchase_details": purchase_details,
            "down_payment": down_payment,
            "interest_rates": interest_rates,
            "holding_period": holding_period
        }
        
    def handle_income_inputs(self):
        def create_salary_inputs(self) -> tuple:
            salary_col1, salary_col2 = st.columns([2, 1])
            
            with salary_col1:
                annual_salary = float(st.number_input(
                    "Annual Salary ($)",
                    min_value=0,
                    value=80000,
                    step=1000,
                    help="Enter your annual salary for tax calculation"
                ))
            
            with salary_col2:
                salary_inflation = float(st.number_input(
                    "Annual Increase (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=3.0,
                    step=0.1,
                    help="Expected annual percentage increase in salary"
                ))
            
            return annual_salary, salary_inflation

        def create_rental_income_inputs(self) -> tuple:
            rent_col1, rent_col2 = st.columns([2, 1])
            
            with rent_col1:
                monthly_rent = float(st.number_input(
                    "Expected Monthly Rent ($)",
                    min_value=0,
                    value=2000,
                    step=100,
                    help="Enter the expected monthly rental income"
                ))
            
            with rent_col2:
                annual_rent_increase = float(st.number_input(
                    "Annual Increase (%)",
                    min_value=0,
                    max_value=10,
                    value=3,
                    help="Expected annual percentage increase in rental income"
                ))
            
            return monthly_rent, annual_rent_increase

        def create_additional_income_inputs(self) -> tuple:
            other_income = float(st.number_input(
                "Other Monthly Income ($)",
                min_value=0,
                value=0,
                step=50,
                help="Additional income from parking, laundry, storage, etc."
            ))
            
            vacancy_rate = float(st.number_input(
                "Vacancy Rate (%)",
                min_value=0,
                max_value=20,
                value=5,
                help="Expected percentage of time the property will be vacant"
            ))
            
            return other_income, vacancy_rate
            
        # Execute all income inputs
        salary_details = create_salary_inputs(self)
        rental_income = create_rental_income_inputs(self)
        additional_income = create_additional_income_inputs(self)
        
        return {
            "salary_details": salary_details,
            "rental_income": rental_income,
            "additional_income": additional_income
        }
        
    def handle_expense_inputs(self):
        def create_primary_expense_inputs(self) -> dict:
            property_tax = float(st.number_input(
                "Annual Property Tax ($)",
                min_value=0,
                value=3000,
                step=100,
                help="Annual property tax amount"
            ))
            
            insurance = float(st.number_input(
                "Annual Insurance ($)",
                min_value=0,
                value=1200,
                step=100,
                help="Annual property insurance cost"
            ))
            
            utilities = float(st.number_input(
                "Monthly Utilities ($)",
                min_value=0,
                value=200,
                step=50,
                help="Monthly utilities cost (if not paid by tenant)"
            ))
            
            management_fee = float(st.number_input(
                "Property Management Fee (%)",
                min_value=0.0,
                max_value=20.0,
                value=8.0,
                step=0.5,
                help="Property management fee as percentage of rental income"
            ))
            
            return {
                "property_tax": property_tax,
                "insurance": insurance,
                "utilities": utilities,
                "management_fee": management_fee
            }

        def create_secondary_expense_inputs(self) -> dict:
            maintenance_pct = float(st.number_input(
                "Maintenance (%)",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="Annual maintenance cost as percentage of property value"
            ))
            
            hoa_fees = float(st.number_input(
                "Monthly HOA Fees ($)",
                min_value=0,
                value=0,
                step=50,
                help="Monthly Homeowner Association fees (if applicable)"
            ))
            
            return {
                "maintenance_pct": maintenance_pct,
                "hoa_fees": hoa_fees
            }

        def create_expense_inflation_inputs(self) -> dict:
            property_tax_inflation = float(st.number_input(
                "Property Tax Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                help="Annual increase in property tax"
            ))
            
            insurance_inflation = float(st.number_input(
                "Insurance Cost Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.1,
                help="Annual increase in insurance costs"
            ))
            
            utilities_inflation = float(st.number_input(
                "Utilities Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=2.5,
                step=0.1,
                help="Annual increase in utility costs"
            ))
            
            maintenance_inflation = float(st.number_input(
                "Maintenance Cost Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.1,
                help="Annual increase in maintenance costs"
            ))
            
            hoa_inflation = float(st.number_input(
                "HOA Fee Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.1,
                help="Annual increase in HOA fees"
            ))
            
            return {
                "property_tax_inflation": property_tax_inflation,
                "insurance_inflation": insurance_inflation,
                "utilities_inflation": utilities_inflation,
                "maintenance_inflation": maintenance_inflation,
                "hoa_inflation": hoa_inflation
            }
            
        # Execute all expense inputs
        primary_expenses = create_primary_expense_inputs(self)
        secondary_expenses = create_secondary_expense_inputs(self)
        expense_inflation = create_expense_inflation_inputs(self)
        
        return {
            "primary_expenses": primary_expenses,
            "secondary_expenses": secondary_expenses,
            "expense_inflation": expense_inflation
        }
        
    def handle_all_inputs(self):
        # Main method to collect all inputs
        st.subheader("Property Details")
        property_details = self.handle_property_details()
        
        st.subheader("Income Analysis")
        income_details = self.handle_income_inputs()
        
        st.subheader("Expense Analysis")
        expense_details = self.handle_expense_inputs()
        
        return property_details, income_details, expense_details