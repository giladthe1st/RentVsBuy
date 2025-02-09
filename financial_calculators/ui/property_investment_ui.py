"""
Streamlit UI for property investment calculator.
"""
import streamlit as st
from ..models.property_investment import PropertyInvestment, PropertyExpenses
from ..calculators.property_calculator import calculate_metrics

def show_property_investment_calculator():
    """Display the property investment calculator UI."""
    st.title("Investment Property Calculator")
    
    with st.form("property_investment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Property Details")
            purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, value=300000.0)
            down_payment_pct = st.number_input("Down Payment (%)", min_value=0.0, max_value=100.0, value=20.0)
            holding_period = st.number_input("Holding Period (years)", min_value=1, value=30)
            
            st.subheader("Rental Income")
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0.0, value=2000.0)
            annual_rent_increase = st.number_input("Annual Rent Increase (%)", min_value=0.0, value=2.0)
            vacancy_rate = st.number_input("Vacancy Rate (%)", min_value=0.0, max_value=100.0, value=5.0)
        
        with col2:
            st.subheader("Operating Expenses (Annual)")
            property_tax = st.number_input("Property Tax ($)", min_value=0.0, value=3000.0)
            insurance = st.number_input("Insurance ($)", min_value=0.0, value=1200.0)
            maintenance = st.number_input("Maintenance ($)", min_value=0.0, value=3000.0)
            utilities = st.number_input("Utilities ($)", min_value=0.0, value=0.0)
            hoa = st.number_input("HOA ($)", min_value=0.0, value=0.0)
            property_management = st.number_input("Property Management ($)", min_value=0.0, value=0.0)
        
        st.subheader("Loan Details")
        num_rates = st.number_input("Number of Interest Rate Periods", min_value=1, max_value=5, value=1)
        interest_rates = []
        
        for i in range(num_rates):
            col1, col2 = st.columns(2)
            with col1:
                rate = st.number_input(f"Interest Rate {i+1} (%)", min_value=0.0, value=6.0, key=f"rate_{i}")
            with col2:
                years = st.number_input(f"Years for Rate {i+1}", min_value=1, value=30, key=f"years_{i}")
            interest_rates.append({"rate": rate, "years": years})
        
        calculate_button = st.form_submit_button("Calculate Investment Metrics")
        
        if calculate_button:
            # Create investment object
            expenses = PropertyExpenses(
                property_tax=property_tax,
                insurance=insurance,
                maintenance=maintenance,
                utilities=utilities,
                hoa=hoa,
                property_management=property_management
            )
            
            investment = PropertyInvestment(
                purchase_price=purchase_price,
                down_payment_pct=down_payment_pct,
                interest_rates=interest_rates,
                holding_period=holding_period,
                monthly_rent=monthly_rent,
                annual_rent_increase=annual_rent_increase,
                operating_expenses=expenses,
                vacancy_rate=vacancy_rate
            )
            
            # Calculate metrics
            metrics = calculate_metrics(investment)
            
            # Display results
            st.header("Investment Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Monthly Averages")
                st.metric("Monthly Payment", f"${metrics.monthly_payments[0]:.2f}")
                st.metric("Monthly Cash Flow", f"${metrics.monthly_cash_flows[0]:.2f}")
                st.metric("Net Operating Income (Monthly)", f"${metrics.noi/12:.2f}")
            
            with col2:
                st.subheader("Investment Returns")
                st.metric("Cap Rate", f"{metrics.cap_rate*100:.2f}%")
                st.metric("Cash on Cash Return", f"{metrics.coc_return*100:.2f}%")
                st.metric("IRR", f"{metrics.irr*100:.2f}%")
            
            st.subheader("Long-term Projections")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Profit", f"${metrics.total_profit:.2f}")
                st.metric("Return on Investment", f"{metrics.roi*100:.2f}%")
            with col2:
                st.metric("Annual Tax Savings", f"${metrics.tax_savings:.2f}")

def main():
    show_property_investment_calculator()

if __name__ == "__main__":
    main()
