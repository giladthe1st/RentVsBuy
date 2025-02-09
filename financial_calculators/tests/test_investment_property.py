import unittest
import numpy as np
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from financial_calculators.calculators.property_calculator import (
    calculate_loan_payments,
    calculate_monthly_payment,
    calculate_metrics,
    calculate_noi,
    calculate_cap_rate,
    calculate_coc_return,
    calculate_irr
)
from financial_calculators.models.property_investment import PropertyInvestment, PropertyExpenses

class TestInvestmentPropertyCalculator(unittest.TestCase):
    def test_monthly_payment_calculation(self):
        """Test basic monthly payment calculations."""
        test_cases = [
            # (principal, rate, months, expected_payment)
            (300000, 4.0, 360, 1432.25),  # 30-year fixed at 4%
            (300000, 0.0, 360, 833.33),   # 0% interest
            (300000, 7.0, 360, 1995.91),  # 30-year fixed at 7%
            (300000, 4.0, 180, 2219.06),  # 15-year fixed at 4%
        ]
        
        for principal, rate, months, expected in test_cases:
            payment = calculate_monthly_payment(principal, rate, months)
            self.assertAlmostEqual(payment, expected, places=2)
            
    def test_loan_amortization(self):
        """Test loan amortization with single interest rate."""
        price = 300000
        down_payment_pct = 20
        interest_rates = ((4.0, 30),)  # 4% for 30 years
        loan_years = 30
        
        payments = calculate_loan_payments(price, down_payment_pct, interest_rates, loan_years)
        
        # Check loan amount and payments
        loan_amount = price * (1 - down_payment_pct / 100)
        self.assertAlmostEqual(loan_amount, 240000, places=2)
        
        # Check payment consistency
        self.assertAlmostEqual(payments[0], 1145.80, places=2)  # First payment
        self.assertEqual(len(payments), 360)  # 30 years * 12 months
        
    def test_investment_metrics(self):
        """Test calculation of investment metrics."""
        # Create test investment
        expenses = PropertyExpenses(
            property_tax=3000,
            insurance=1200,
            maintenance=3000,
            utilities=0,
            hoa=0,
            property_management=0
        )
        
        investment = PropertyInvestment(
            purchase_price=300000,
            down_payment_pct=20,
            interest_rates=[{"rate": 4.0, "years": 30}],
            holding_period=30,
            monthly_rent=2000,
            annual_rent_increase=2.0,
            operating_expenses=expenses,
            vacancy_rate=5.0
        )
        
        # Calculate metrics
        metrics = calculate_metrics(investment)
        
        # Test basic metrics
        self.assertGreater(metrics.noi, 0)
        self.assertGreater(metrics.cap_rate, 0)
        self.assertGreater(metrics.coc_return, 0)
        self.assertGreater(metrics.irr, 0)
        self.assertEqual(len(metrics.monthly_payments), 360)
        self.assertEqual(len(metrics.monthly_cash_flows), 360)
        
    def test_noi_calculation(self):
        """Test NOI calculation."""
        expenses = PropertyExpenses(
            property_tax=3000,
            insurance=1200,
            maintenance=3000,
            utilities=0,
            hoa=0,
            property_management=0
        )
        annual_income = 24000
        
        noi = calculate_noi(annual_income, expenses)
        expected_noi = annual_income - (expenses.property_tax + expenses.insurance + 
                                      expenses.maintenance + expenses.utilities + 
                                      expenses.hoa + expenses.property_management)
        
        self.assertEqual(noi, expected_noi)
        
    def test_cap_rate(self):
        """Test cap rate calculation."""
        noi = 15000
        property_value = 300000
        expected_cap_rate = noi / property_value
        
        cap_rate = calculate_cap_rate(noi, property_value)
        self.assertEqual(cap_rate, expected_cap_rate)
        
    def test_coc_return(self):
        """Test cash on cash return calculation."""
        annual_cash_flow = 10000
        total_investment = 60000
        expected_coc = annual_cash_flow / total_investment
        
        coc = calculate_coc_return(annual_cash_flow, total_investment)
        self.assertEqual(coc, expected_coc)
        
    def test_irr(self):
        """Test IRR calculation."""
        initial_investment = -60000
        cash_flows = [5000] * 12  # Monthly cash flows for 1 year
        final_value = 320000
        
        irr = calculate_irr(initial_investment, cash_flows, final_value)
        self.assertGreater(irr, 0)

if __name__ == '__main__':
    unittest.main()
