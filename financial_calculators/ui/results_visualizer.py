import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict
import os
from financial_calculators.models.rent_vs_buy_models import YearlyPurchaseDetails, YearlyRentalDetails

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
            detail.equity - cumulative_purchase_costs[i] + purchase_details[i].investment_portfolio
            for i, detail in enumerate(purchase_details[:years])
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
            name="Purchase Net Worth",
            line=dict(color='blue')
        ))

        # Add rental scenario net worth
        fig.add_trace(go.Scatter(
            x=list(range(1, years + 1)),
            y=rental_net_worth,
            name="Rental Net Worth",
            line=dict(color='red')
        ))

        fig.update_layout(
            title=f'Net Worth Comparison Over {years} Years',
            xaxis_title='Years',
            yaxis_title='Value ($)',
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
        current_lang: str = 'en',
        params: Dict = {}
    ):
        """Displays summary statistics for both scenarios"""

        # Calculate totals for purchase scenario
        total_interest_paid = sum(year.interest_paid for year in purchase_details)
        total_principal_paid = sum(year.principal_paid for year in purchase_details)
        total_property_tax = sum(year.property_tax for year in purchase_details)
        total_maintenance = sum(year.maintenance for year in purchase_details)
        total_home_insurance = sum(year.insurance for year in purchase_details)
        total_utilities_purchase = sum(year.yearly_utilities for year in purchase_details)
        total_closing_costs = purchase_details[0].closing_costs
        total_purchase_costs = (total_interest_paid + total_principal_paid +
                              total_property_tax + total_maintenance +
                              total_home_insurance + total_utilities_purchase +
                              total_closing_costs)

        # Calculate totals for rental scenario
        total_rent_paid = sum(year.yearly_rent for year in rental_details)
        total_rent_insurance = sum(year.rent_insurance for year in rental_details)
        total_utilities_rental = sum(year.yearly_utilities for year in rental_details)
        total_rental_costs = total_rent_paid + total_rent_insurance + total_utilities_rental

        # Calculate final positions
        purchase_final_position = (
            purchase_details[-1].equity +  # Home equity
            purchase_details[-1].investment_portfolio -  # Investment portfolio
            total_purchase_costs  # Total costs
        )

        rental_final_position = (
            rental_details[-1].investment_portfolio -  # Investment portfolio
            total_rental_costs  # Total costs
        )

        # Display the net positions with color coding
        st.header("Final Net Position")

        # Display calculation breakdown
        st.markdown("### Calculation Breakdown")

        col_calc1, col_calc2 = st.columns(2)

        with col_calc1:
            st.markdown("#### Purchase Scenario")
            st.markdown("**Assets:**")

            # Home Equity Section
            st.markdown(f"+ Home Equity: ${purchase_details[-1].equity:,.2f}")
            with st.expander("View Home Equity Details"):
                down_payment = purchase_details[0].property_value * (params['down_payment_pct'] / 100)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Down Payment: ${down_payment:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Principal Paid: ${total_principal_paid:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Property Appreciation: ${(purchase_details[-1].property_value - purchase_details[0].property_value):,.2f}")

            # Investment Portfolio Section
            st.markdown(f"+ Investment Portfolio: ${purchase_details[-1].investment_portfolio:,.2f}")
            with st.expander("View Investment Portfolio Details"):
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Initial Investment: $0.00")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Total New Investments: ${sum(year.new_investments for year in purchase_details):,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Total Investment Returns: ${sum(year.investment_returns for year in purchase_details):,.2f}")

            st.markdown("**Costs:**")
            st.markdown(f"- One-Time Closing Costs: ${total_closing_costs:,.2f}")
            st.markdown(f"- Total Interest: ${total_interest_paid:,.2f}")
            st.markdown(f"- Total Property Tax: ${total_property_tax:,.2f}")
            st.markdown(f"- Total Maintenance: ${total_maintenance:,.2f}")
            st.markdown(f"- Total Insurance: ${total_home_insurance:,.2f}")

            # Utilities Section
            st.markdown(f"- Total Utilities: ${total_utilities_purchase:,.2f}")
            with st.expander("View Utilities Breakdown"):
                # Get the utilities breakdown from yearly details
                total_electricity = sum(
                    year.yearly_utilities * (params['utilities']['electricity']['base'] / 
                    (params['utilities']['electricity']['base'] + params['utilities']['water']['base'] + params['utilities']['other']['base']))
                    for year in purchase_details
                )
                total_water = sum(
                    year.yearly_utilities * (params['utilities']['water']['base'] / 
                    (params['utilities']['electricity']['base'] + params['utilities']['water']['base'] + params['utilities']['other']['base']))
                    for year in purchase_details
                )
                total_other = sum(
                    year.yearly_utilities * (params['utilities']['other']['base'] / 
                    (params['utilities']['electricity']['base'] + params['utilities']['water']['base'] + params['utilities']['other']['base']))
                    for year in purchase_details
                )

                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Electricity: ${total_electricity:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Water: ${total_water:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Other: ${total_other:,.2f}")

            st.markdown("___")
            st.markdown(f"""
            Total Costs Calculation:
            ```
            {total_closing_costs:,.2f} (Closing Costs)
            + {total_interest_paid:,.2f} (Interest)
            + {total_property_tax:,.2f} (Property Tax)
            + {total_maintenance:,.2f} (Maintenance)
            + {total_home_insurance:,.2f} (Insurance)
            + {total_utilities_purchase:,.2f} (Utilities)
            = {total_purchase_costs:,.2f} (Total Costs)
            ```
            """)
            st.markdown("___")

            color = "green" if purchase_final_position > 0 else "red"
            st.markdown(f'<p style="color: {color}; font-size: 20px;"><strong>Net Position: ${purchase_final_position:,.2f}</strong></p>', unsafe_allow_html=True)
            st.markdown(f"""
            Final Position Calculation:
            ```
            {purchase_details[-1].equity:,.2f} (Equity)
            + {purchase_details[-1].investment_portfolio:,.2f} (Investments)
            - {total_purchase_costs:,.2f} (Total Costs)
            = {purchase_final_position:,.2f}
            ```
            """)

        with col_calc2:
            st.markdown("#### Rental Scenario")
            st.markdown("**Assets:**")

            # Investment Portfolio Section
            st.markdown(f"+ Investment Portfolio: ${rental_details[-1].investment_portfolio:,.2f}")
            with st.expander("View Investment Portfolio Details"):
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Initial Investment: ${initial_investment:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Total New Investments: ${sum(year.new_investments for year in rental_details):,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Total Investment Returns: ${sum(year.investment_returns for year in rental_details):,.2f}")

            st.markdown("**Costs:**")
            st.markdown(f"- Total Rent: ${total_rent_paid:,.2f}")
            st.markdown(f"- Total Insurance: ${total_rent_insurance:,.2f}")

            # Utilities Section
            st.markdown(f"- Total Utilities: ${total_utilities_rental:,.2f}")
            with st.expander("View Utilities Breakdown"):
                # Get the utilities breakdown from yearly details
                total_electricity = sum(
                    year.yearly_utilities * (params['utilities']['electricity']['base'] / 
                    (params['utilities']['electricity']['base'] + params['utilities']['water']['base'] + params['utilities']['other']['base']))
                    for year in rental_details
                )
                total_water = sum(
                    year.yearly_utilities * (params['utilities']['water']['base'] / 
                    (params['utilities']['electricity']['base'] + params['utilities']['water']['base'] + params['utilities']['other']['base']))
                    for year in rental_details
                )
                total_other = sum(
                    year.yearly_utilities * (params['utilities']['other']['base'] / 
                    (params['utilities']['electricity']['base'] + params['utilities']['water']['base'] + params['utilities']['other']['base']))
                    for year in rental_details
                )

                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Electricity: ${total_electricity:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Water: ${total_water:,.2f}")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• Other: ${total_other:,.2f}")

            st.markdown("___")
            st.markdown(f"""
            Total Costs Calculation:
            ```
            {total_rent_paid:,.2f} (Rent)
            + {total_rent_insurance:,.2f} (Insurance)
            + {total_utilities_rental:,.2f} (Utilities)
            = {total_rental_costs:,.2f} (Total Costs)
            ```
            """)
            st.markdown("___")

            color = "green" if rental_final_position > 0 else "red"
            st.markdown(f'<p style="color: {color}; font-size: 20px;"><strong>Net Position: ${rental_final_position:,.2f}</strong></p>', unsafe_allow_html=True)
            st.markdown(f"""
            Final Position Calculation:
            ```
            {rental_details[-1].investment_portfolio:,.2f} (Investments)
            - {total_rental_costs:,.2f} (Total Costs)
            = {rental_final_position:,.2f}
            ```
            """)

        # Compare the scenarios
        difference = purchase_final_position - rental_final_position
        better_option = "Buying" if difference > 0 else "Renting"
        color = "green" if difference > 0 else "red"

        st.markdown("---")
        st.markdown("### Comparison")
        st.markdown(f'<p style="font-size: 18px;">Better financial position by <span style="color: green; font-weight: bold;">${abs(difference):,.2f}</span> with <span style="color: green; font-weight: bold;">{better_option}</span></p>', unsafe_allow_html=True)

        # Add yearly breakdown section
        st.markdown("___")
        st.markdown("### Yearly Cost Breakdown")
        
        with st.expander("View Detailed Yearly Breakdown"):
            # Create tabs for Purchase and Rental scenarios
            purchase_tab, rental_tab = st.tabs(["Purchase Scenario", "Rental Scenario"])
            
            with purchase_tab:
                purchase_data = []
                for i, year in enumerate(purchase_details):
                    yearly_data = {
                        "Year": i + 1,
                        "Property Value": f"${year.property_value:,.2f}",
                        "Mortgage Payment": f"${year.yearly_mortgage:,.2f}",
                        "Principal Paid": f"${year.principal_paid:,.2f}",
                        "Interest Paid": f"${year.interest_paid:,.2f}",
                        "Property Tax": f"${year.property_tax:,.2f}",
                        "Maintenance": f"${year.maintenance:,.2f}",
                        "Insurance": f"${year.insurance:,.2f}",
                        "Utilities": f"${year.yearly_utilities:,.2f}",
                        "Investment Portfolio": f"${year.investment_portfolio:,.2f}",
                        "Home Equity": f"${year.equity:,.2f}"
                    }
                    if i == 0:
                        yearly_data["Closing Costs"] = f"${year.closing_costs:,.2f}"
                    else:
                        yearly_data["Closing Costs"] = "$0.00"
                    purchase_data.append(yearly_data)
                
                df_purchase = pd.DataFrame(purchase_data)
                st.dataframe(df_purchase, use_container_width=True)
            
            with rental_tab:
                rental_data = []
                for i, year in enumerate(rental_details):
                    yearly_data = {
                        "Year": i + 1,
                        "Yearly Rent": f"${year.yearly_rent:,.2f}",
                        "Insurance": f"${year.rent_insurance:,.2f}",
                        "Utilities": f"${year.yearly_utilities:,.2f}",
                        "Investment Portfolio": f"${year.investment_portfolio:,.2f}",
                        "New Investments": f"${year.new_investments:,.2f}",
                        "Investment Returns": f"${year.investment_returns:,.2f}"
                    }
                    rental_data.append(yearly_data)
                
                df_rental = pd.DataFrame(rental_data)
                st.dataframe(df_rental, use_container_width=True)

    @staticmethod
    def save_results_to_csv(
        purchase_details: List[YearlyPurchaseDetails],
        rental_details: List[YearlyRentalDetails],
        years: int,
        purchase_params: Dict,
        rental_params: Dict,
        save_output: bool = False
    ):
        """Saves the calculation results to CSV files if save_output is True"""
        if not save_output:
            return

        # Create output folder if it doesn't exist
        output_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output_data')
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
        st.markdown("### Monthly Payment Breakdown")
        st.markdown(f"**Total Monthly Payment:** ${monthly_payment:,.2f}")
        st.markdown(f"**First Payment Breakdown:**")
        st.markdown(f"- Principal: ${first_principal:,.2f}")
        st.markdown(f"- Interest: ${first_interest:,.2f}")