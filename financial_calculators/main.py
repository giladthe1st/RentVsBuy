import streamlit as st
from financial_calculators.calculators.rent_vs_buy import show as show_rent_vs_buy
from financial_calculators.calculators.investment_property import show as show_investment_property
from financial_calculators.calculators.etf_comparison import show as show_etf_comparison
from financial_calculators.ui.navigation import NavigationManager, CalculatorType

def main():
    """Main entry point for the application."""
    # Configure the page
    st.set_page_config(
        layout="wide",
        page_title="Real Estate Financial Calculator",
        page_icon="🏠",
        initial_sidebar_state="collapsed"
    )

    # Initialize navigation
    nav_manager = NavigationManager()
    
    # Render navigation
    nav_manager.render()
    
    # Show the selected calculator
    current_calculator = st.session_state.current_calculator
    
    if current_calculator == CalculatorType.RENT_VS_BUY:
        show_rent_vs_buy()
    elif current_calculator == CalculatorType.INVESTMENT_PROPERTY:
        show_investment_property()
    elif current_calculator == CalculatorType.ETF_COMPARISON:
        show_etf_comparison()

if __name__ == "__main__":
    main()