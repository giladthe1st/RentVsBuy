import unittest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from financial_calculators.calculators.rent_vs_buy import (
    MortgageCalculation,
    calculate_mortgage_details,
)
from financial_calculators.utils.financial_calculator import FinancialCalculator
from financial_calculators.models.data_models import PurchaseScenarioParams, RentalScenarioParams, Utilities, UtilityData


class TestRentVsBuyCalculator(unittest.TestCase):
    def setUp(self):
        """Set up test cases with common test data"""
        self.house_price = 500000
        self.down_payment_pct = 20
        self.interest_rate = 5.0
        self.years = 30
        
    def test_calculate_mortgage_details_with_interest(self):
        """Test mortgage calculation with non-zero interest rate"""
        result = calculate_mortgage_details(
            self.house_price,
            self.down_payment_pct,
            self.interest_rate,
            self.years
        )
        
        # Expected monthly payment calculation
        loan_amount = self.house_price * (1 - self.down_payment_pct/100)
        monthly_rate = self.interest_rate / (100 * 12)
        num_payments = self.years * 12
        expected_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
        # First month's interest
        expected_first_interest = loan_amount * monthly_rate
        expected_first_principal = expected_payment - expected_first_interest
        
        self.assertIsInstance(result, MortgageCalculation)
        self.assertAlmostEqual(result.monthly_payment, expected_payment, places=2)
        self.assertAlmostEqual(result.first_principal, expected_first_principal, places=2)
        self.assertAlmostEqual(result.first_interest, expected_first_interest, places=2)

    def test_calculate_mortgage_details_zero_interest(self):
        """Test mortgage calculation with zero interest rate"""
        result = calculate_mortgage_details(
            self.house_price,
            self.down_payment_pct,
            0.0,  # Zero interest rate
            self.years
        )
        
        loan_amount = self.house_price * (1 - self.down_payment_pct/100)
        expected_payment = loan_amount / (self.years * 12)
        
        self.assertIsInstance(result, MortgageCalculation)
        self.assertAlmostEqual(result.monthly_payment, expected_payment, places=2)
        self.assertEqual(result.first_interest, 0.0)
        self.assertAlmostEqual(result.first_principal, expected_payment, places=2)

    def test_calculate_mortgage_details_edge_cases(self):
        """Test mortgage calculation with edge cases"""
        # Test with 100% down payment
        result = calculate_mortgage_details(
            self.house_price,
            100.0,  # 100% down payment
            self.interest_rate,
            self.years
        )
        self.assertAlmostEqual(result.monthly_payment, 0.0, places=2)
        self.assertAlmostEqual(result.first_principal, 0.0, places=2)
        self.assertAlmostEqual(result.first_interest, 0.0, places=2)

        # Test with minimum values
        result = calculate_mortgage_details(
            100000,  # Minimum reasonable house price
            5.0,    # Minimum reasonable down payment
            1.0,    # Minimum reasonable interest rate
            1       # Minimum years
        )
        self.assertGreater(result.monthly_payment, 0)
        self.assertGreater(result.first_principal, 0)
        self.assertGreater(result.first_interest, 0)

    @patch('financial_calculators.calculators.rent_vs_buy.ResultsVisualizer')
    @patch('financial_calculators.calculators.rent_vs_buy.InputHandler')
    def test_handle_purchase_inputs(self, mock_input_handler, mock_visualizer):
        """Test handle_purchase_inputs with mocked dependencies"""
        # Create mock purchase parameters
        mock_purchase_params = Mock()
        mock_purchase_params.house_price = self.house_price
        mock_purchase_params.down_payment_pct = self.down_payment_pct
        mock_purchase_params.interest_rate = self.interest_rate
        mock_purchase_params.years = self.years
        
        # Setup mock return value
        mock_input_handler.create_purchase_inputs.return_value = mock_purchase_params
        
        from financial_calculators.calculators.rent_vs_buy import handle_purchase_inputs
        
        # Call the function
        purchase_params, mortgage_details = handle_purchase_inputs()
        
        # Verify the results
        self.assertEqual(purchase_params, mock_purchase_params)
        self.assertIsInstance(mortgage_details, MortgageCalculation)
        
        # Verify that the visualizer was called
        mock_visualizer.create_monthly_payment_chart.assert_called_once()

    @patch('financial_calculators.calculators.rent_vs_buy.InputHandler')
    def test_handle_rental_inputs(self, mock_input_handler):
        """Test handle_rental_inputs"""
        mock_rental_params = Mock()
        mock_input_handler.create_rental_inputs.return_value = mock_rental_params
        
        from financial_calculators.calculators.rent_vs_buy import handle_rental_inputs
        
        down_payment = 100000
        result = handle_rental_inputs(down_payment)
        
        self.assertEqual(result, mock_rental_params)


if __name__ == '__main__':
    unittest.main()
