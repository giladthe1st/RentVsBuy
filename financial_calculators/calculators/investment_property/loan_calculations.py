"""
Module for loan-related calculations.
"""

import numpy as np
from typing import Tuple

# Function to calculate monthly mortgage payment

def calculate_monthly_payment(principal: float, annual_rate: float, total_months: int) -> float:
    """Calculate monthly mortgage payment using the standard formula."""
    if principal < 0:
        raise ValueError("Principal amount cannot be negative")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if total_months <= 0:
        raise ValueError("Loan term must be positive")

    if annual_rate == 0:
        return principal / total_months
    monthly_rate = annual_rate / (12 * 100)
    return principal * (monthly_rate * (1 + monthly_rate)**total_months) / ((1 + monthly_rate)**total_months - 1)

# Function to calculate remaining loan balance

def calculate_remaining_balance(principal: float, payment: float, annual_rate: float, months: int) -> float:
    """Calculate remaining loan balance after a number of payments."""
    if principal < 0:
        raise ValueError("Principal amount cannot be negative")
    if payment < 0:
        raise ValueError("Payment amount cannot be negative")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if months <= 0:
        raise ValueError("Number of payments must be positive")

    if annual_rate == 0:
        return principal - (payment * months)
    monthly_rate = annual_rate / (12 * 100)
    return principal * (1 + monthly_rate)**months - payment * ((1 + monthly_rate)**months - 1) / monthly_rate

