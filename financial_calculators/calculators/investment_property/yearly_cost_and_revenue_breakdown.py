"""
Module for calculating yearly cost and revenue breakdown for investment properties.
"""

import pandas as pd
import streamlit as st
from typing import List, Dict

class YearlyCostAndRevenueBreakdownCalculator:
    @staticmethod
    def calculate_yearly_breakdown(
        total_holding_period: int,
        purchase_price: float,
        monthly_rent: float,
        annual_rent_increase: float,
        other_income: float,
        vacancy_rate: float,
        property_tax: float,
        annual_inflation: float,
        insurance: float,
        utilities: float,
        mgmt_fee: float,
        monthly_maintenance: float,
        conservative_rate: float,
        hoa_fees: float,
        monthly_payments: List[float],
        df_loan: pd.DataFrame,
        conservative_equity: List[float],
    ) -> pd.DataFrame:
        """
        Calculate yearly breakdown of costs and revenues for an investment property.
        
        Args:
            total_holding_period: Total number of years to analyze
            purchase_price: Purchase price of the property
            monthly_rent: Monthly rental income
            annual_rent_increase: Annual percentage increase in rent
            other_income: Additional monthly income
            vacancy_rate: Expected vacancy rate percentage
            property_tax: Annual property tax
            annual_inflation: Annual increase in expenses
            insurance: Annual insurance cost
            utilities: Monthly utilities cost
            mgmt_fee: Monthly management fee
            monthly_maintenance: Monthly maintenance cost
            conservative_rate: Conservative growth rate
            hoa_fees: Monthly HOA fees
            monthly_payments: List of monthly mortgage payments
            df_loan: DataFrame containing loan amortization details
            metrics: Dictionary containing calculated metrics
            conservative_equity: List of yearly conservative equity values
            is_deployed: Whether the calculator is running in deployment mode
            
        Returns:
            DataFrame containing yearly breakdown
        """
        yearly_data = []
        for year in range(total_holding_period):
            # Calculate values for this year
            year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
            year_monthly_income = year_monthly_rent + other_income
            year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
            
            year_property_tax = property_tax * (1 + annual_inflation/100)**year
            year_insurance = insurance * (1 + annual_inflation/100)**year
            year_utilities = utilities * (1 + annual_inflation/100)**year * 12
            year_mgmt_fee = mgmt_fee * (1 + annual_inflation/100)**year * 12
            year_maintenance = monthly_maintenance * 12 * (1 + conservative_rate/100)**year
            year_hoa = hoa_fees * (1 + annual_inflation/100)**year * 12
            
            # Calculate property values for each scenario
            conservative_value = purchase_price * (1 + conservative_rate/100)**year
            
            # Calculate mortgage components for this year
            if year < len(monthly_payments) // 12:
                start_idx = year * 12
                end_idx = start_idx + 12
                year_principal = df_loan['Principal'][start_idx:end_idx].sum()
                year_interest = df_loan['Interest'][start_idx:end_idx].sum()
                year_mortgage = sum(monthly_payments[start_idx:end_idx])
            else:
                year_principal = 0
                year_interest = 0
                year_mortgage = 0
            
            # Calculate cash flow - if beyond loan term, use 0 for mortgage payment
            year_cash_flow = (year_monthly_income * 12) - (year_monthly_vacancy_loss * 12) - \
                           year_property_tax - year_insurance - year_utilities - \
                           year_mgmt_fee - year_maintenance - year_hoa - year_mortgage

            yearly_data.append({
                "Year": year + 1,
                "Rental Income": f"${year_monthly_income * 12:,.2f}",
                "Vacancy Loss": f"${year_monthly_vacancy_loss * 12:,.2f}",
                "Property Tax": f"${year_property_tax:,.2f}",
                "Insurance": f"${year_insurance:,.2f}",
                "Utilities": f"${year_utilities:,.2f}",
                "Management Fee": f"${year_mgmt_fee:,.2f}",
                "Maintenance": f"${year_maintenance:,.2f}",
                "HOA Fees": f"${year_hoa:,.2f}",
                "Mortgage Payment": f"${year_mortgage:,.2f}",
                "Principal Paid": f"${year_principal:,.2f}",
                "Interest Paid": f"${year_interest:,.2f}",
                "Cash Flow": f"${year_cash_flow:,.2f}",
                "Conservative Value": f"${conservative_value:,.2f}",
                "Equity": f"${conservative_equity[year]:,.2f}"
            })
        
        return pd.DataFrame(yearly_data)

    @staticmethod
    def display_detailed_summary(
        yearly_data: List[Dict],
        property_details: Dict,
        key_metrics: Dict,
        appreciation_scenarios: Dict,
        monthly_expenses: Dict,
        is_deployed: bool = False
    ) -> None:
        """
        Display a detailed summary of the investment property analysis.
        
        Args:
            yearly_data: List of dictionaries containing yearly breakdown data
            property_details: Dictionary containing property details
            key_metrics: Dictionary containing key metrics
            appreciation_scenarios: Dictionary containing appreciation scenarios
            monthly_expenses: Dictionary containing monthly expenses
            is_deployed: Whether the calculator is running in deployment mode
        """
        if not is_deployed:
            st.subheader("Detailed Data Summary")
            with st.expander("Click to view all inputs and calculated values"):
                st.markdown("### Property Details")
                st.table(pd.DataFrame(list(property_details.items()), columns=['Item', 'Value']))
                
                st.markdown("### Key Metrics")
                st.table(pd.DataFrame(list(key_metrics.items()), columns=['Metric', 'Value']))
                
                st.markdown("### Appreciation Scenarios")
                st.table(pd.DataFrame(list(appreciation_scenarios.items()), columns=['Scenario', 'Rate']))
                
                st.markdown("### Monthly Expense Breakdown")
                st.table(pd.DataFrame(list(monthly_expenses.items()), columns=['Expense', 'Amount']))

                # Income and Property Value Projections
                st.markdown("### Income and Property Value Projections")
                income_df = pd.DataFrame([{
                    'Year': data['Year'],
                    'Rental Income': data['Rental Income'],
                    'Cash Flow': data['Cash Flow'],
                    'Equity': data['Equity'],
                    'Conservative Value': data['Conservative Value']
                } for data in yearly_data])
                st.dataframe(income_df, use_container_width=True)

                # Yearly Expense Breakdown
                st.markdown("### Yearly Expense Breakdown")
                expenses_df = pd.DataFrame([{
                    'Year': data['Year'],
                    'Property Tax': data['Property Tax'],
                    'Insurance': data['Insurance'],
                    'Utilities': data['Utilities'],
                    'Management Fee': data['Management Fee'],
                    'Maintenance': data['Maintenance'],
                    'HOA Fees': data['HOA Fees'],
                    'Principal Paid': data['Principal Paid'],
                    'Interest Paid': data['Interest Paid']
                } for data in yearly_data])
                st.dataframe(expenses_df, use_container_width=True)
                
                # Add download button
                summary_text = YearlyCostAndRevenueBreakdownCalculator.format_summary_data(
                    property_details, 
                    key_metrics, 
                    appreciation_scenarios, 
                    monthly_expenses,
                    yearly_data
                )
                st.download_button(
                    label="Download Summary",
                    data=summary_text,
                    file_name="investment_property_analysis.txt",
                    mime="text/plain"
                )

    @staticmethod
    def format_summary_data(
        property_details: Dict,
        key_metrics: Dict,
        appreciation_scenarios: Dict,
        monthly_expenses: Dict,
        yearly_data: List[Dict]
    ) -> str:
        """
        Format all summary data into a nice text format for downloading.
        
        Args:
            property_details: Dictionary containing property details
            key_metrics: Dictionary containing key metrics
            appreciation_scenarios: Dictionary containing appreciation scenarios
            monthly_expenses: Dictionary containing monthly expenses
            yearly_data: List of dictionaries containing yearly breakdown data
            
        Returns:
            Formatted string containing the summary data
        """
        summary = []
        
        summary.append("INVESTMENT PROPERTY ANALYSIS SUMMARY")
        summary.append("=" * 40 + "\n")
        
        summary.append("PROPERTY DETAILS")
        summary.append("-" * 20)
        for item, value in property_details.items():
            summary.append(f"{item}: {value}")
        summary.append("")
        
        summary.append("KEY METRICS")
        summary.append("-" * 20)
        for metric, value in key_metrics.items():
            summary.append(f"{metric}: {value}")
        summary.append("")
        
        summary.append("APPRECIATION SCENARIOS")
        summary.append("-" * 20)
        for scenario, rate in appreciation_scenarios.items():
            summary.append(f"{scenario}: {rate}")
        summary.append("")
        
        summary.append("MONTHLY EXPENSE BREAKDOWN")
        summary.append("-" * 20)
        for expense, amount in monthly_expenses.items():
            summary.append(f"{expense}: {amount}")
        summary.append("")
        
        summary.append("YEARLY BREAKDOWN")
        summary.append("-" * 20)
        summary.append("\nYear  Rental Income    Cash Flow    Equity    Conservative")
        summary.append("-" * 85)
        
        for data in yearly_data:
            year = data['Year']
            rental = data['Rental Income']
            cash_flow = data['Cash Flow']
            equity = data['Equity']
            cons_value = data['Conservative Value']
            
            summary.append(f"{year:<6}{rental:<16}{cash_flow:<12}{equity:<10}{cons_value:<16}")
        
        summary.append("\nDETAILED YEARLY EXPENSES")
        summary.append("-" * 25)
        summary.append("\nYear  Property Tax  Insurance  Utilities  Management  Maintenance  HOA  Principal  Interest")
        summary.append("-" * 95)
        
        for data in yearly_data:
            year = data['Year']
            tax = data['Property Tax']
            insurance = data['Insurance']
            utilities = data['Utilities']
            mgmt = data['Management Fee']
            maint = data['Maintenance']
            hoa = data['HOA Fees']
            principal = data['Principal Paid']
            interest = data['Interest Paid']
            
            summary.append(f"{year:<6}{tax:<14}{insurance:<11}{utilities:<11}{mgmt:<13}{maint:<13}{hoa:<6}{principal:<11}{interest}")    
        return "\n".join(summary)