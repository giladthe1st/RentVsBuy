import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict
import pandas as pd
import os
from models.rent_vs_buy_models import YearlyPurchaseDetails, YearlyRentalDetails
from translation_utils import translate_text

class ResultsVisualizer:
    @staticmethod
    def create_comparison_chart(
        purchase_details: List[YearlyPurchaseDetails],
        rental_details: List[YearlyRentalDetails],
        years: int,
        current_lang: str = 'en'
    ):
        """Creates and displays the comparison chart using Plotly"""
        
        # Calculate cumulative costs for each year
        cumulative_purchase_costs = []
        cumulative_rental_costs = []
        running_purchase_cost = 0
        running_rental_cost = 0

        for year in range(years):
            # Purchase costs for this year
            yearly_purchase_cost = (
                purchase_details[year].yearly_mortgage +
                purchase_details[year].property_tax +
                purchase_details[year].maintenance +
                purchase_details[year].insurance +
                purchase_details[year].yearly_utilities
            )
            running_purchase_cost += yearly_purchase_cost
            cumulative_purchase_costs.append(running_purchase_cost)

            # Rental costs for this year
            yearly_rental_cost = (
                rental_details[year].yearly_rent +
                rental_details[year].rent_insurance +
                rental_details[year].yearly_utilities
            )
            running_rental_cost += yearly_rental_cost
            cumulative_rental_costs.append(running_rental_cost)

        # Calculate net worth for each scenario
        property_values = [detail.property_value for detail in purchase_details]
        purchase_net_worth = [
            property_values[i] - cumulative_purchase_costs[i] + purchase_details[i].investment_portfolio
            for i in range(years)
        ]

        rental_net_worth = [
            rental_details[i].investment_portfolio - cumulative_rental_costs[i]
            for i in range(years)
        ]

        # Create the figure
        fig = go.Figure()

        # Add purchase scenario net worth
        fig.add_trace(go.Scatter(
            x=list(range(1, years + 1)),
            y=purchase_net_worth,
            name=translate_text('Purchase Net Worth', current_lang),
            line=dict(color='blue')
        ))

        # Add rental scenario net worth
        fig.add_trace(go.Scatter(
            x=list(range(1, years + 1)),
            y=rental_net_worth,
            name=translate_text('Rental Net Worth', current_lang),
            line=dict(color='red')
        ))

        fig.update_layout(
            title=translate_text(f'Net Worth Comparison Over {years} Years', current_lang),
            xaxis_title=translate_text('Years', current_lang),
            yaxis_title=translate_text('Value ($)', current_lang),
            height=600,
            showlegend=True,
            hovermode='x unified'
        )

        # Display the graph
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_summary_statistics(
        purchase_details: List[YearlyPurchaseDetails],
        rental_details: List[YearlyRentalDetails],
        years: int,
        initial_investment: float,
        current_lang: str = 'en'
    ):
        """Displays summary statistics for both scenarios"""
        
        st.header(translate_text(f"Total Payments Over {years} Years", current_lang))
        
        # Calculate purchase scenario totals
        total_interest_paid = sum(year.interest_paid for year in purchase_details)
        total_principal_paid = sum(year.principal_paid for year in purchase_details)
        total_property_tax = sum(year.property_tax for year in purchase_details)
        total_maintenance = sum(year.maintenance for year in purchase_details)
        total_home_insurance = sum(year.insurance for year in purchase_details)
        total_utilities_purchase = sum(year.yearly_utilities for year in purchase_details)
        
        total_purchase_costs = (total_interest_paid + total_principal_paid +
                              total_property_tax + total_maintenance +
                              total_home_insurance + total_utilities_purchase)

        # Calculate rental scenario totals
        total_rent_paid = sum(year.yearly_rent for year in rental_details)
        total_rent_insurance = sum(year.rent_insurance for year in rental_details)
        total_utilities_rental = sum(year.yearly_utilities for year in rental_details)
        total_rental_costs = total_rent_paid + total_rent_insurance + total_utilities_rental

        # Investment calculations
        final_investment_value_rental = rental_details[-1].investment_portfolio
        total_investment_returns_rental = sum(year.investment_returns for year in rental_details)
        total_new_investments_rental = sum(year.new_investments for year in rental_details)

        final_investment_value_purchase = purchase_details[-1].investment_portfolio
        total_investment_returns_purchase = sum(year.investment_returns for year in purchase_details)
        total_new_investments_purchase = sum(year.new_investments for year in purchase_details)

        # Display summaries in two columns
        col_totals1, col_totals2 = st.columns(2)

        with col_totals1:
            st.markdown(translate_text("### Purchase Scenario", current_lang))
            st.markdown(translate_text(f"**Total Interest Paid:** ${total_interest_paid:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Principal Paid:** ${total_principal_paid:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Property Tax:** ${total_property_tax:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Maintenance:** ${total_maintenance:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Home Insurance:** ${total_home_insurance:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Utilities:** ${total_utilities_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Cost:** ${total_purchase_costs:,.2f}", current_lang))
            st.markdown(translate_text("#### Investment Portfolio", current_lang))
            st.markdown(translate_text(f"**Total New Investments:** ${total_new_investments_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Investment Returns:** ${total_investment_returns_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Final Portfolio Value:** ${final_investment_value_purchase:,.2f}", current_lang))
            st.markdown(translate_text(f"**Final Property Value:** ${purchase_details[-1].property_value:,.2f}", current_lang))
            st.markdown(translate_text(f"**Final Home Equity:** ${purchase_details[-1].equity:,.2f}", current_lang))

        with col_totals2:
            st.markdown(translate_text("### Rental Scenario", current_lang))
            st.markdown(translate_text(f"**Total Rent Paid:** ${total_rent_paid:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Rent Insurance:** ${total_rent_insurance:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Utilities:** ${total_utilities_rental:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Cost:** ${total_rental_costs:,.2f}", current_lang))
            st.markdown(translate_text("#### Investment Portfolio", current_lang))
            st.markdown(translate_text(f"**Initial Investment:** ${initial_investment:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total New Investments:** ${total_new_investments_rental:,.2f}", current_lang))
            st.markdown(translate_text(f"**Total Investment Returns:** ${total_investment_returns_rental:,.2f}", current_lang))
            st.markdown(translate_text(f"**Final Portfolio Value:** ${final_investment_value_rental:,.2f}", current_lang))

    @staticmethod
    def save_results_to_csv(
        purchase_details: List[YearlyPurchaseDetails],
        rental_details: List[YearlyRentalDetails],
        years: int,
        purchase_params: Dict,
        rental_params: Dict
    ):
        """Saves the calculation results to CSV files"""
        
        # Create output folder if it doesn't exist
        output_folder = 'output_data'
        os.makedirs(output_folder, exist_ok=True)

        # Create DataFrames for each component
        results_df = pd.DataFrame({
            'Year': range(1, years + 1),
            'Property_Value': [pd.property_value for pd in purchase_details],
            'Home_Equity': [pd.equity for pd in purchase_details],
            'Rental_Wealth': [rd.net_wealth for rd in rental_details]
        })

        params_df = pd.DataFrame({
            'Parameter': ['Years'] + list(purchase_params.keys()) + list(rental_params.keys()),
            'Value': [years] + list(purchase_params.values()) + list(rental_params.values())
        })

        purchase_df = pd.DataFrame([vars(pd) for pd in purchase_details])
        rental_df = pd.DataFrame([vars(rd) for rd in rental_details])

        # Save all data to CSV files
        params_df.to_csv(os.path.join(output_folder, 'input_parameters.csv'), index=False)
        results_df.to_csv(os.path.join(output_folder, 'comparison_results.csv'), index=False)
        rental_df.to_csv(os.path.join(output_folder, 'rental_detailed_analysis.csv'), index=False)
        purchase_df.to_csv(os.path.join(output_folder, 'purchase_detailed_analysis.csv'), index=False)

    @staticmethod
    def create_monthly_payment_chart(
        monthly_payment: float,
        first_principal: float,
        first_interest: float,
        current_lang: str = 'en'
    ):

        # Display the numerical breakdown
        st.markdown(translate_text("### Monthly Payment Breakdown", current_lang))
        st.markdown(translate_text(f"**Total Monthly Payment:** ${monthly_payment:,.2f}", current_lang))
        st.markdown(translate_text(f"**First Payment Breakdown:**", current_lang))
        st.markdown(translate_text(f"- Principal: ${first_principal:,.2f}", current_lang))
        st.markdown(translate_text(f"- Interest: ${first_interest:,.2f}", current_lang))