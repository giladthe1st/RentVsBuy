import unittest
import numpy as np
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from financial_calculators.calculators.investment_property import (
    calculate_loan_details,
    calculate_monthly_payment,
    calculate_investment_metrics,
    calculate_noi,
    calculate_cap_rate,
    calculate_coc_return,
    calculate_irr,
    calculate_tax_brackets,
    get_rate_for_month
)

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
        
        payments, loan_amount = calculate_loan_details(price, down_payment_pct, interest_rates, loan_years)
        
        # Check loan amount
        self.assertAlmostEqual(loan_amount, 240000, places=2)
        
        # Check payment consistency
        self.assertAlmostEqual(payments[0], 1145.80, places=2)  # First payment
        self.assertEqual(len(payments), 360)  # 30 years * 12 months
        
        # Calculate total interest paid
        total_payments = sum(payments)
        total_interest = total_payments - loan_amount
        self.assertGreater(total_interest, 0)  # Verify interest is being paid
        
    def test_multiple_rate_periods(self):
        """Test loan calculations with multiple interest rate periods."""
        price = 300000
        down_payment_pct = 20
        interest_rates = ((2.0, 20), (7.0, 10))  # 2% for 20 years, then 7% for 10 years
        loan_years = 30
        
        payments, loan_amount = calculate_loan_details(price, down_payment_pct, interest_rates, loan_years)
        
        # Basic checks
        self.assertEqual(len(payments), 360)
        self.assertGreater(payments[240], payments[239])  # Payment should increase at rate change
        
        # Calculate remaining principal at rate change
        monthly_rate = 0.02 / 12
        remaining_principal = loan_amount
        for _ in range(240):  # 20 years
            interest = remaining_principal * monthly_rate
            principal = payments[0] - interest
            remaining_principal -= principal
            
        # Verify new payment at higher rate
        new_payment = payments[240]
        self.assertGreater(new_payment, payments[0])  # New payment should be higher
        self.assertLess(new_payment, loan_amount * 0.01)  # Sanity check: monthly payment shouldn't exceed 1% of original loan
        
    def test_investment_metrics(self):
        """Test overall investment metrics calculation."""
        test_params = {
            'purchase_price': 300000,
            'down_payment_pct': 20,
            'interest_rates': [{'rate': 4.0, 'years': 30}],
            'holding_period': 30,
            'monthly_rent': 2000,
            'annual_rent_increase': 3,
            'operating_expenses': {
                'property_tax': 3000,
                'insurance': 1200,
                'utilities': 0,
                'mgmt_fee': 200,
                'hoa_fees': 0
            },
            'vacancy_rate': 5
        }
        
        metrics = calculate_investment_metrics(**test_params)
        
        # Basic validation
        self.assertGreater(metrics['noi'], 0)
        self.assertGreater(metrics['cap_rate'], 0)
        self.assertGreater(metrics['irr'], 0)
        
        # Check cash flow progression
        annual_cash_flows = metrics['annual_cash_flows']
        self.assertEqual(len(annual_cash_flows), test_params['holding_period'])
        
        # Cash flows should generally improve over time due to rent increases
        self.assertGreater(annual_cash_flows[-1], annual_cash_flows[0])
        
    def test_edge_cases(self):
        """Test edge cases and potential error conditions."""
        # Test zero price
        payments, loan_amount = calculate_loan_details(0, 20, ((4.0, 30),), 30)
        self.assertEqual(loan_amount, 0)
        self.assertEqual(sum(payments), 0)
        
        # Test 100% down payment
        payments, loan_amount = calculate_loan_details(300000, 100, ((4.0, 30),), 30)
        self.assertEqual(loan_amount, 0)
        self.assertEqual(sum(payments), 0)
        
        # Test zero interest rate
        payments, loan_amount = calculate_loan_details(300000, 20, ((0.0, 30),), 30)
        self.assertGreater(loan_amount, 0)
        self.assertAlmostEqual(payments[0], loan_amount / 360, places=2)
        
        # Test very high interest rate
        payments, loan_amount = calculate_loan_details(300000, 20, ((50.0, 30),), 30)
        self.assertGreater(payments[0], 0)
        self.assertLess(payments[0], loan_amount)  # Payment shouldn't exceed loan amount
        
    def test_cash_flow_consistency(self):
        """Test that cash flows behave consistently with different rate scenarios."""
        base_params = {
            'purchase_price': 300000,
            'down_payment_pct': 20,
            'holding_period': 30,
            'monthly_rent': 2000,
            'annual_rent_increase': 3,
            'operating_expenses': {
                'property_tax': 3000,
                'insurance': 1200,
                'utilities': 0,
                'mgmt_fee': 200,
                'hoa_fees': 0
            },
            'vacancy_rate': 5
        }
        
        # Test scenarios
        scenarios = [
            {'rates': [{'rate': 4.0, 'years': 30}], 'name': 'Fixed 4%'},
            {'rates': [{'rate': 2.0, 'years': 20}, {'rate': 7.0, 'years': 10}], 'name': '2% then 7%'},
            {'rates': [{'rate': 7.0, 'years': 30}], 'name': 'Fixed 7%'}
        ]
        
        results = {}
        for scenario in scenarios:
            params = base_params.copy()
            params['interest_rates'] = scenario['rates']
            metrics = calculate_investment_metrics(**params)
            results[scenario['name']] = metrics['annual_cash_flows']
            
        # Verify cash flow relationships
        fixed_4_flows = results['Fixed 4%']
        variable_flows = results['2% then 7%']
        fixed_7_flows = results['Fixed 7%']
        
        # First 20 years of variable rate should be better than fixed 7%
        self.assertGreater(sum(variable_flows[:20]), sum(fixed_7_flows[:20]))
        
        # Last 10 years should show reasonable transition
        # Cash flows shouldn't drop below a certain percentage of previous cash flow
        for i in range(19, 29):  # Check transition years
            self.assertGreater(variable_flows[i+1], variable_flows[i] * 0.7)  # Max 30% drop

    def test_noi_and_returns(self):
        """Test NOI, Cap Rate, and Cash on Cash Return calculations."""
        # Test NOI calculation
        annual_income = 24000  # $2000/month
        operating_expenses = 5000
        noi = calculate_noi(annual_income, operating_expenses)
        self.assertEqual(noi, 19000)

        # Test Cap Rate calculation
        property_value = 300000
        cap_rate = calculate_cap_rate(noi, property_value)
        self.assertAlmostEqual(cap_rate, 6.33, places=2)  # (19000/300000) * 100

        # Test Cash on Cash Return
        annual_cash_flow = 15000
        total_investment = 60000  # 20% down payment
        coc_return = calculate_coc_return(annual_cash_flow, total_investment)
        self.assertEqual(coc_return, 25.0)  # (15000/60000) * 100

        # Test edge cases
        self.assertEqual(calculate_cap_rate(noi, 0), 0.0)
        self.assertEqual(calculate_coc_return(annual_cash_flow, 0), 0.0)

    def test_tax_bracket_edge_cases(self):
        """Test edge cases for tax bracket calculations."""
        # Test negative income (should raise ValueError)
        with self.assertRaises(ValueError):
            calculate_tax_brackets(-1000)
            
        # Test zero income (should return empty dict)
        self.assertEqual(len(calculate_tax_brackets(0)), 0)
        
        # Test very high income
        high_income = 1e7  # 10 million
        high_brackets = calculate_tax_brackets(high_income)
        
        # Should have all brackets for high income
        self.assertGreaterEqual(len(high_brackets), 9)  # All brackets should be present
        
        # Verify highest bracket is present with correct format
        highest_bracket_key = None
        for key in high_brackets.keys():
            if "400,000+" in key:
                highest_bracket_key = key
                break
        
        self.assertIsNotNone(highest_bracket_key, "Highest bracket (400,000+) not found")
        self.assertIn("50.40%", highest_bracket_key)

    def test_tax_brackets_basic(self):
        """Test basic tax bracket functionality and simple calculations."""
        # Test zero income
        zero_brackets = calculate_tax_brackets(0)
        self.assertEqual(len(zero_brackets), 0)

        # Test low income (single bracket)
        low_income = 40000
        low_brackets = calculate_tax_brackets(low_income)
        self.assertEqual(len(low_brackets), 1)
        self.assertAlmostEqual(sum(low_brackets.values()), low_income * 0.2580, places=2)

        # Test middle income (multiple brackets)
        middle_income = 150000
        middle_brackets = calculate_tax_brackets(middle_income)
        self.assertGreater(len(middle_brackets), 3)
        total_tax = sum(middle_brackets.values())
        self.assertGreater(total_tax, middle_income * 0.30)

    def test_tax_bracket_boundaries(self):
        """Test tax calculations at and around bracket boundaries."""
        # Test exact bracket boundaries and transitions
        boundaries = [47564, 57375, 101200, 114750, 177882, 200000, 253414, 400000]
        
        for boundary in boundaries:
            # Test just below, at, and just above boundary
            below = calculate_tax_brackets(boundary - 0.01)
            at = calculate_tax_brackets(boundary)
            above = calculate_tax_brackets(boundary + 0.01)
            
            # Verify tax rate changes at boundary
            below_rate = sum(below.values()) / (boundary - 0.01)
            at_rate = sum(at.values()) / boundary
            above_rate = sum(above.values()) / (boundary + 0.01)
            
            # Effective rate should increase at each boundary
            self.assertLess(below_rate, above_rate, msg=f"Tax rate should increase at boundary {boundary}")
            self.assertAlmostEqual(at_rate, below_rate, places=4, msg=f"Tax rate should be continuous at boundary {boundary}")

    def test_tax_bracket_precise_calculations(self):
        """Test precise tax calculations for complex scenarios."""
        # Test case 1: Income spanning first three brackets exactly
        income = 101200
        brackets = calculate_tax_brackets(income)
        
        expected_tax = (
            47564 * 0.2580 +  # First bracket
            (57375 - 47564) * 0.2775 +  # Second bracket
            (101200 - 57375) * 0.3325  # Third bracket
        )
        
        self.assertAlmostEqual(sum(brackets.values()), expected_tax, places=2)
        
        # Test case 2: High income with all brackets
        income = 500000
        brackets = calculate_tax_brackets(income)
        
        expected_tax = (
            47564 * 0.2580 +  # First bracket
            (57375 - 47564) * 0.2775 +  # Second bracket
            (101200 - 57375) * 0.3325 +  # Third bracket
            (114750 - 101200) * 0.3790 +  # Fourth bracket
            (177882 - 114750) * 0.4340 +  # Fifth bracket
            (200000 - 177882) * 0.4672 +  # Sixth bracket
            (253414 - 200000) * 0.4758 +  # Seventh bracket
            (400000 - 253414) * 0.5126 +  # Eighth bracket
            (500000 - 400000) * 0.5040    # Ninth bracket
        )
        
        self.assertAlmostEqual(sum(brackets.values()), expected_tax, places=2)

    def test_tax_bracket_formatting(self):
        """Test tax bracket range formatting and continuity."""
        income = 500000
        brackets = calculate_tax_brackets(income)
        
        # Extract and verify ranges
        ranges = []
        for key in brackets.keys():
            range_part = key[key.find('(')+1:key.find(')')]
            if '+' not in range_part:
                start, end = map(lambda x: x.strip().replace(',', ''), range_part.split('to'))
                ranges.append((float(start), float(end)))
        
        # Verify ranges are continuous
        for i in range(len(ranges)-1):
            self.assertEqual(ranges[i][1], ranges[i+1][0], msg=f"Range gap between {ranges[i]} and {ranges[i+1]}")
        
        # Verify range properties
        self.assertEqual(ranges[0][0], 0, msg="First range should start at 0")
        last_key = list(brackets.keys())[-1]
        self.assertIn('+', last_key, msg="Last bracket should be open-ended")
        
        # Verify all brackets have correct format
        for key in brackets.keys():
            self.assertRegex(key, r'^\d+\.\d+% \([0-9,]+ to [0-9,]+\)$|^\d+\.\d+% \([0-9,]+\+\)$',
                           msg=f"Invalid bracket format: {key}")

    def test_get_rate_for_month(self):
        """Test interest rate lookup for specific months."""
        rates = (
            (3.5, 5),   # First 5 years at 3.5%
            (4.0, 15),  # Next 15 years at 4.0%
            (4.5, 10)   # Last 10 years at 4.5%
        )

        # Test first period
        self.assertEqual(get_rate_for_month(rates, 0), 3.5)  # First month
        self.assertEqual(get_rate_for_month(rates, 59), 3.5)  # Last month of first period

        # Test second period
        self.assertEqual(get_rate_for_month(rates, 60), 4.0)  # First month of second period
        self.assertEqual(get_rate_for_month(rates, 239), 4.0)  # Last month of second period

        # Test third period
        self.assertEqual(get_rate_for_month(rates, 240), 4.5)  # First month of third period
        self.assertEqual(get_rate_for_month(rates, 359), 4.5)  # Last month

        # Test empty rates
        empty_rates = tuple()
        self.assertEqual(get_rate_for_month(empty_rates, 0), 0.0)

        # Test single rate
        single_rate = ((5.0, 30),)
        self.assertEqual(get_rate_for_month(single_rate, 0), 5.0)
        self.assertEqual(get_rate_for_month(single_rate, 359), 5.0)

    def test_irr_calculations(self):
        """Test IRR calculations with various scenarios."""
        # Test normal case
        initial_investment = 60000
        cash_flows = [5000] * 5  # 5 years of $5000 annual cash flow
        final_value = 100000
        irr = calculate_irr(initial_investment, cash_flows, final_value)
        self.assertGreater(irr, 0)

        # Test break-even case
        cash_flows = [0] * 5
        final_value = initial_investment
        irr = calculate_irr(initial_investment, cash_flows, final_value)
        self.assertAlmostEqual(irr, 0.0, places=2)

        # Test negative cash flows
        cash_flows = [-1000] * 5
        irr = calculate_irr(initial_investment, cash_flows, final_value)
        self.assertLess(irr, 0)

        # Test no investment case with no returns
        irr = calculate_irr(0, [0] * 5, 0)
        self.assertEqual(irr, 0.0)

        # Test extreme case
        cash_flows = [1000000] * 5  # Very high cash flows
        final_value = 2000000
        irr = calculate_irr(initial_investment, cash_flows, final_value)
        self.assertGreater(irr, 100)  # Should be a very high IRR

    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test negative values
        with self.assertRaises(ValueError):
            calculate_monthly_payment(-300000, 4.0, 360)
        
        # Test invalid percentages
        with self.assertRaises(ValueError):
            calculate_loan_details(300000, -20, ((4.0, 30),), 30)
        
        # Test invalid rate periods
        with self.assertRaises(ValueError):
            calculate_loan_details(300000, 20, ((4.0, -30),), 30)

    def test_floating_point_precision(self):
        """Test handling of floating point calculations."""
        # Test very small numbers
        payment = calculate_monthly_payment(0.01, 4.0, 360)
        self.assertGreaterEqual(payment, 0)
        
        # Test very large numbers
        payment = calculate_monthly_payment(1e9, 4.0, 360)
        self.assertLess(payment, 1e9)
        
        # Test rate precision
        payment1 = calculate_monthly_payment(300000, 4.0, 360)
        payment2 = calculate_monthly_payment(300000, 4.000001, 360)
        self.assertNotEqual(payment1, payment2)


    def test_complex_rate_scenarios(self):
        """Test more complex interest rate scenarios."""
        # Test many rate changes
        rates = tuple((r, 3) for r in [3.0, 4.0, 5.0, 4.5, 3.5])
        payments, _ = calculate_loan_details(300000, 20, rates, 15)
        
        # Verify rate transitions
        for i in range(4):
            transition_month = (i + 1) * 36
            self.assertNotEqual(payments[transition_month-1], 
                            payments[transition_month])
        
        # Test uneven rate periods
        rates = ((3.0, 7), (4.0, 13), (5.0, 10))
        payments, _ = calculate_loan_details(300000, 20, rates, 30)
        self.assertEqual(len(payments), 360)


    def test_operating_expenses(self):
        """Test operating expense calculations with inflation."""
        base_expenses = {
            'property_tax': 3000,
            'insurance': 1200,
            'utilities': 100,
            'mgmt_fee': 200,
            'hoa_fees': 300
        }
        
        metrics = calculate_investment_metrics(
            purchase_price=300000,
            down_payment_pct=20,
            interest_rates=[{'rate': 4.0, 'years': 30}],
            holding_period=30,
            monthly_rent=2000,
            annual_rent_increase=3,
            operating_expenses=base_expenses,
            vacancy_rate=5
        )
        
        # Verify expense inflation
        annual_flows = metrics['annual_cash_flows']
        self.assertLess(annual_flows[0], annual_flows[-1])
        
        # Test with zero expenses
        zero_expenses = {k: 0 for k in base_expenses}
        metrics_zero = calculate_investment_metrics(
            purchase_price=300000,
            down_payment_pct=20,
            interest_rates=[{'rate': 4.0, 'years': 30}],
            holding_period=30,
            monthly_rent=2000,
            annual_rent_increase=3,
            operating_expenses=zero_expenses,
            vacancy_rate=5
        )
        self.assertGreater(metrics_zero['noi'], metrics['noi'])


    def test_vacancy_rate_impact(self):
        """Test the impact of different vacancy rates."""
        base_params = {
            'purchase_price': 300000,
            'down_payment_pct': 20,
            'interest_rates': [{'rate': 4.0, 'years': 30}],
            'holding_period': 30,
            'monthly_rent': 2000,
            'annual_rent_increase': 3,
            'operating_expenses': {
                'property_tax': 3000,
                'insurance': 1200,
                'utilities': 0,
                'mgmt_fee': 200,
                'hoa_fees': 0
            },
            'vacancy_rate': 5
        }
        
        # Test various vacancy rates
        vacancy_rates = [0, 5, 10, 20]
        results = []
        
        for rate in vacancy_rates:
            params = base_params.copy()
            params['vacancy_rate'] = rate
            metrics = calculate_investment_metrics(**params)
            results.append(metrics['noi'])
        
        # Verify NOI decreases with increasing vacancy
        for i in range(len(results)-1):
            self.assertGreater(results[i], results[i+1])

    def test_equity_buildup(self):
        """Test equity buildup calculations including principal paydown and appreciation."""
        test_params = {
            'purchase_price': 300000,
            'down_payment_pct': 20,
            'interest_rates': [{'rate': 4.0, 'years': 30}],
            'holding_period': 30,
            'monthly_rent': 2000,
            'annual_rent_increase': 3,
            'operating_expenses': {
                'property_tax': 3000,
                'insurance': 1200,
                'utilities': 0,
                'mgmt_fee': 200,
                'hoa_fees': 0
            },
            'vacancy_rate': 5
        }
        
        metrics = calculate_investment_metrics(**test_params)
        
        # Test equity from principal payments
        loan_amount = test_params['purchase_price'] * (1 - test_params['down_payment_pct']/100)
        self.assertGreater(metrics['equity_from_principal'], 0)
        self.assertLess(metrics['equity_from_principal'], loan_amount)  # Can't pay down more than borrowed
        
        # Test equity from appreciation
        expected_appreciation = test_params['purchase_price'] * ((1 + test_params['annual_rent_increase']/100) ** test_params['holding_period'] - 1)
        self.assertAlmostEqual(metrics['equity_from_appreciation'], expected_appreciation, places=2)
        
        # Test total equity
        self.assertEqual(metrics['total_equity'], metrics['equity_from_principal'] + metrics['equity_from_appreciation'])
        
        # Test with no loan (100% down payment)
        no_loan_params = test_params.copy()
        no_loan_params['down_payment_pct'] = 100
        no_loan_metrics = calculate_investment_metrics(**no_loan_params)
        
        self.assertEqual(no_loan_metrics['equity_from_principal'], 0)  # No loan means no principal payments
        self.assertEqual(no_loan_metrics['equity_from_appreciation'], metrics['equity_from_appreciation'])  # Appreciation should be the same

if __name__ == '__main__':
    unittest.main()
