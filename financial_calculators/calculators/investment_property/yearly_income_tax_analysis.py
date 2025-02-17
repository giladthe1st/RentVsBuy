"""
Module for calculating yearly income tax analysis for investment properties.
"""

import pandas as pd
from typing import List, Dict
import streamlit as st
from calculators.investment_property.investment_metrics import calculate_tax_brackets

class YearlyTaxBreakdownCalculator:
    
    def calculate_yearly_tax_breakdown(
        total_holding_period: int,
        monthly_rent: float,
        annual_rent_increase: float,
        other_income: float,
        vacancy_rate: float,
        property_tax: float,
        property_tax_inflation: float,
        insurance: float,
        insurance_inflation: float,
        utilities: float,
        utilities_inflation: float,
        mgmt_fee: float,
        mgmt_fee_inflation: float,
        monthly_maintenance: float,
        conservative_rate: float,
        hoa_fees: float,
        hoa_inflation: float,
        monthly_payments: List[float],
        df_loan: pd.DataFrame,
        annual_salary: float,
        salary_inflation: float,
        one_time_payment: float = 0.0
    ) -> pd.DataFrame:
        """
        Calculate yearly tax breakdown for an investment property.
        
        Args:
            total_holding_period: Total number of years to analyze
            monthly_rent: Monthly rental income
            annual_rent_increase: Annual percentage increase in rent
            other_income: Additional monthly income
            vacancy_rate: Expected vacancy rate percentage
            property_tax: Annual property tax
            property_tax_inflation: Annual increase in property tax
            insurance: Annual insurance cost
            insurance_inflation: Annual increase in insurance
            utilities: Monthly utilities cost
            utilities_inflation: Annual increase in utilities
            mgmt_fee: Monthly management fee
            mgmt_fee_inflation: Annual increase in management fee
            monthly_maintenance: Monthly maintenance cost
            conservative_rate: Conservative growth rate for maintenance
            hoa_fees: Monthly HOA fees
            hoa_inflation: Annual increase in HOA fees
            monthly_payments: List of monthly mortgage payments
            df_loan: DataFrame containing loan amortization details
            annual_salary: Annual employment salary
            salary_inflation: Annual increase in salary
            one_time_payment: One-time payment to be added to the first year's net rental income
            
        Returns:
            DataFrame containing yearly tax analysis
        """
        yearly_tax_data = []
        
        # Calculate yearly values
        for year in range(total_holding_period):
            # Calculate rental income for this year with annual increases
            year_monthly_rent = monthly_rent * (1 + annual_rent_increase/100)**year
            year_monthly_income = year_monthly_rent + other_income
            year_monthly_vacancy_loss = year_monthly_income * (vacancy_rate / 100)
            year_rental_income = (year_monthly_income - year_monthly_vacancy_loss) * 12
            
            # Calculate expenses for this year
            year_property_tax = property_tax * (1 + property_tax_inflation/100)**year
            year_insurance = insurance * (1 + insurance_inflation/100)**year
            year_utilities = utilities * (1 + utilities_inflation/100)**year * 12
            year_mgmt_fee = mgmt_fee * (1 + mgmt_fee_inflation/100)**year * 12
            year_maintenance = monthly_maintenance * 12 * (1 + conservative_rate/100)**year
            year_hoa = hoa_fees * (1 + hoa_inflation/100)**year * 12
            
            # Calculate mortgage components for this year
            if year < len(monthly_payments) // 12 and year * 12 < len(df_loan):
                start_idx = year * 12
                end_idx = min(start_idx + 12, len(df_loan))
                year_interest = df_loan['Interest'][start_idx:end_idx].sum()
                # If we have partial year data, annualize the mortgage payment
                months_in_year = end_idx - start_idx
                year_mortgage = monthly_payments[start_idx] * months_in_year
            else:
                year_interest = 0
                year_mortgage = 0
            
            # Calculate operating expenses
            year_operating_expenses = (
                year_property_tax +
                year_insurance +
                year_utilities +
                year_mgmt_fee +
                year_maintenance +
                year_hoa
            )
            
            # Calculate net rental income
            year_net_rental = year_rental_income - year_operating_expenses - year_mortgage
            
            # Add one-time payment to first year's net rental income
            if year == 0:
                year_net_rental += one_time_payment
            
            # Assume salary increases with inflation
            year_salary = annual_salary * (1 + salary_inflation/100)**year
            
            # Calculate taxes for employment income only
            year_employment_tax = calculate_tax_brackets(year_salary)
            year_employment_total_tax = sum(year_employment_tax.values())
            year_employment_after_tax = year_salary - year_employment_total_tax
            year_employment_tax_rate = (year_employment_total_tax / year_salary * 100) if year_salary > 0 else 0
            
            # Calculate taxes for combined income
            year_total_income = year_salary + year_net_rental
            year_combined_tax = calculate_tax_brackets(year_total_income)
            year_combined_total_tax = sum(year_combined_tax.values())
            year_combined_after_tax = year_total_income - year_combined_total_tax
            year_combined_tax_rate = (year_combined_total_tax / year_total_income * 100) if year_total_income > 0 else 0
            
            # Calculate differences
            year_additional_tax = year_combined_total_tax - year_employment_total_tax
            year_additional_after_tax = year_combined_after_tax - year_employment_after_tax
            year_tax_rate_change = year_combined_tax_rate - year_employment_tax_rate
            
            yearly_tax_data.append({
                "Year": year + 1,
                "Employment Income": f"${year_salary:,.2f}",
                "Employment Tax": f"${year_employment_total_tax:,.2f}",
                "Employment After-Tax": f"${year_employment_after_tax:,.2f}",
                "Employment Tax Rate": f"{year_employment_tax_rate:.2f}%",
                "Net Rental Income": f"${year_net_rental:,.2f}",
                "Total Income": f"${year_total_income:,.2f}",
                "Total Tax": f"${year_combined_total_tax:,.2f}",
                "Total After-Tax": f"${year_combined_after_tax:,.2f}",
                "Total Tax Rate": f"{year_combined_tax_rate:.2f}%",
                "Additional Tax": f"${year_additional_tax:,.2f}",
                "Additional After-Tax": f"${year_additional_after_tax:,.2f}",
                "Tax Rate Change": f"{year_tax_rate_change:+.2f}%"
            })
        
        return pd.DataFrame(yearly_tax_data)