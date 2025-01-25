DEFAULT_VALUES = {
    'years': 30,
    'house_price': 500000,
    'down_payment': 20,
    'interest_rate': 4.0,
    'property_tax': 1.0,
    'maintenance_rate': 1.0,
    'insurance': 1500,
    'insurance_inflation': 2.0,
    'long_term_growth': 3.0,
    'investment_return': 7.0,
    'monthly_rent': 2500,
    'rent_inflation': 3.0,
    'rent_insurance': 300,
    'rent_insurance_inflation': 2.0,
    'utilities': {
        'electricity': {'base': 150, 'inflation': 2.0},
        'water': {'base': 50, 'inflation': 2.0},
        'other': {'base': 100, 'inflation': 2.0}
    }
}

CLOSING_COSTS = {
    'legal_fees': 600,
    'bank_appraisal_fee': 250,
    'interest_adjustment': 500,
    'title_insurance': 229,
    'land_transfer_base': 1650,
    'land_transfer_threshold': 200000,
    'land_transfer_rate': 0.02,  # 2%
}

CLOSING_COSTS_INFO_URL = "https://royallepageprime.ca/closing-costs.html"