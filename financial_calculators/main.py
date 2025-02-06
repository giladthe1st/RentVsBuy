import streamlit as st
from .calculators.rent_vs_buy import show as show_rent_vs_buy
from .calculators.investment_property import show as show_investment_property
from .calculators.etf_comparison import show as show_etf_comparison
from .ui.navigation import Navigation, NavigationManager, CalculatorType

def main():
    """Main application entry point."""
    # Configure the page
    NavigationManager.setup_page_config()
    
    # Create navigation (pass current_lang if in production)
    nav = Navigation()
    current_calculator = nav.create_navigation()
    
    # Display the selected calculator
    if current_calculator == CalculatorType.RENT_VS_BUY:
        show_rent_vs_buy()
    elif current_calculator == CalculatorType.INVESTMENT_PROPERTY:
        property_metrics = show_investment_property()
        if property_metrics and st.session_state.get('show_etf_comparison', False):
            show_etf_comparison(property_metrics)
    elif current_calculator == CalculatorType.ETF_COMPARISON:
        show_etf_comparison()

if __name__ == "__main__":
    main()