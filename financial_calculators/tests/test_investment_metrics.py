import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import unittest
from financial_calculators.calculators.investment_metrics import (
    calculate_loan_details, calculate_noi, calculate_cap_rate,
    calculate_coc_return, calculate_irr, calculate_tax_brackets,
    calculate_investment_metrics
)

class TestInvestmentMetrics(unittest.TestCase):
    def test_calculate_loan_details(self):
        price = 300000
        down_payment_pct = 20
        interest_rates = [(3.5, 30)]
        loan_years = 30
        monthly_payments, loan_amount = calculate_loan_details(price, down_payment_pct, interest_rates, loan_years)
        self.assertAlmostEqual(loan_amount, 240000)
        self.assertEqual(len(monthly_payments), 360)

    def test_calculate_noi(self):
        annual_income = 50000
        operating_expenses = 15000
        noi = calculate_noi(annual_income, operating_expenses)
        self.assertEqual(noi, 35000)

    def test_calculate_cap_rate(self):
        noi = 35000
        property_value = 500000
        cap_rate = calculate_cap_rate(noi, property_value)
        self.assertAlmostEqual(cap_rate, 7.0)

    def test_calculate_coc_return(self):
        annual_cash_flow = 10000
        total_investment = 100000
        coc_return = calculate_coc_return(annual_cash_flow, total_investment)
        self.assertAlmostEqual(coc_return, 10.0)

    def test_calculate_irr(self):
        initial_investment = 100000
        cash_flows = [10000, 10000, 10000, 10000, 110000]
        final_value = 0
        irr = calculate_irr(initial_investment, cash_flows, final_value)
        self.assertTrue(irr > 0)

    def test_calculate_tax_brackets(self):
        annual_salary = 120000
        tax_brackets = calculate_tax_brackets(annual_salary)
        self.assertTrue(len(tax_brackets) > 0)

    def test_calculate_investment_metrics(self):
        purchase_price = 300000
        down_payment_pct = 20
        interest_rates = [{'rate': 3.5, 'years': 30}]
        holding_period = 30
        monthly_rent = 2000
        annual_rent_increase = 2
        operating_expenses = {'property_tax': 3000, 'insurance': 1200, 'maintenance': 1000}
        vacancy_rate = 5
        metrics = calculate_investment_metrics(purchase_price, down_payment_pct, interest_rates, holding_period, monthly_rent, annual_rent_increase, operating_expenses, vacancy_rate)
        self.assertTrue('monthly_payments' in metrics)

if __name__ == '__main__':
    unittest.main()
