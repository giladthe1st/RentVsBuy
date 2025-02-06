import streamlit as st
from googletrans import Translator
from typing import Dict, Any, List
from functools import lru_cache
import time

# Create a single translator instance
translator = Translator()

# Cache for translations
translation_cache: Dict[str, Dict[str, str]] = {}

def get_translations() -> Dict[str, Dict[str, str]]:
    """Get translations for all supported languages."""
    return {
        'en': {'name': 'English', 'code': 'en'},
        'he': {'name': 'עברית', 'code': 'he'},
        'ru': {'name': 'Русский', 'code': 'ru'}
    }

def get_all_translatable_text() -> List[str]:
    """Get all text that needs translation."""
    return [
        # Main titles and headers
        "Rent vs. Buy Calculator",
        "Compare the financial implications of renting versus buying a home",
        "Purchase Options",
        "Rental Options",
        "Investment Options",
        "Results",
        
        # Input labels
        "Annual Household Income ($)",
        "Simulation Years:",
        "House Price ($)",
        "Mortgage Interest Rate (%)",
        "Down Payment (%)",
        "Property Tax Rate (%)",
        "Annual Maintenance (%)",
        "Annual Insurance ($)",
        "Property Appreciation Rate (%)",
        "Monthly Rent ($)",
        "Annual Rent Increase (%)",
        "Renter's Insurance ($)",
        "Monthly Investment ($)",
        "Investment Return Rate (%)",
        
        # ETF Comparison labels
        "ETF Symbol",
        "Initial Investment Amount ($)",
        "Investment Period (Years)",
        "Annual Additional Investment ($)",
        "ETF Metrics",
        "Investment Comparison",
        "Total Return",
        "Annual Return",
        "Annual Dividend Income",
        "Current Investment Value",
        "Volatility",
        "Investment Value Over Time",
        "Investment Growth Over Time",
        "Investment Value",
        "Total Contribution",
        "Yearly Performance",
        "Reinvest Dividends",
        "Total Dividends Earned",
        
        # Tax related text
        "Tax Breakdown",
        "Annual Income:",
        "Total Tax:",
        "Net Income:",
        "Tax Brackets Breakdown",
        
        # Help texts
        "Total yearly household income before taxes",
        "Number of years to simulate the comparison",
        "Enter the total price of the house you're considering",
        "Annual mortgage interest rate",
        "Percentage of house price as down payment",
        "Annual property tax as percentage of house value",
        "Annual maintenance and repairs as percentage of house value",
        "Annual homeowner's insurance cost",
        "Expected annual property value appreciation",
        "Monthly rental payment",
        "Expected annual rent increase",
        "Annual renter's insurance cost",
        "Monthly investment amount",
        "Expected annual return on investments",
        
        # Chart labels
        "Year",
        "Value ($)",
        "Net Worth Comparison",
        "Purchase Scenario",
        "Rental Scenario",
    ]

def initialize_translations():
    """Pre-translate all text at startup."""
    texts = get_all_translatable_text()
    languages = [lang['code'] for lang in get_translations().values() if lang['code'] != 'en']
    
    with st.spinner('Initializing translations...'):
        for lang in languages:
            for text in texts:
                # Create cache key
                cache_key = f"{text}:{lang}"
                if cache_key not in translation_cache:
                    try:
                        # Add small delay to avoid rate limiting
                        time.sleep(0.1)
                        result = translator.translate(text, dest=lang)
                        translation_cache[cache_key] = result.text
                    except Exception:
                        translation_cache[cache_key] = text

def create_language_selector():
    """Create a language selector in the sidebar."""
    translations = get_translations()
    
    # Initialize translations if not already done
    if not translation_cache:
        initialize_translations()
    
    # Create a container in the top right
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col2:
            current_lang = st.selectbox(
                '',
                options=list(translations.keys()),
                format_func=lambda x: translations[x]['name'],
                key='language_selector'
            )
    
    return current_lang

@lru_cache(maxsize=1000)
def cached_translate(text: str, target_lang: str) -> str:
    """Cached translation function."""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception:
        return text

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language using cache."""
    if target_lang == 'en':
        return text
    
    # Create cache key
    cache_key = f"{text}:{target_lang}"
    
    # Check cache first
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    # If not in cache, translate and cache result
    translated = cached_translate(text, target_lang)
    translation_cache[cache_key] = translated
    return translated

def translate_number_input(text: str, target_lang: str, **kwargs) -> Any:
    """Create a translated number input."""
    translated_label = translate_text(text, target_lang)
    translated_help = translate_text(kwargs.get('help', ''), target_lang) if 'help' in kwargs else None
    
    if 'help' in kwargs:
        kwargs['help'] = translated_help
    
    return st.number_input(translated_label, **kwargs)

def translate_slider(text: str, target_lang: str, **kwargs) -> Any:
    """Create a translated slider."""
    translated_label = translate_text(text, target_lang)
    translated_help = translate_text(kwargs.get('help', ''), target_lang) if 'help' in kwargs else None
    
    if 'help' in kwargs:
        kwargs['help'] = translated_help
    
    return st.slider(translated_label, **kwargs)
