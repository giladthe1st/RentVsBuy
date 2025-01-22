import streamlit as st
from calculators.rent_vs_buy import show as show_rent_vs_buy
from calculators.investment_property import show as show_investment_property
from ui.navigation import Navigation, NavigationManager, CalculatorType

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
    else:
        show_investment_property()

if __name__ == "__main__":
    main()