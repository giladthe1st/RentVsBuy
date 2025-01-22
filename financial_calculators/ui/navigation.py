import streamlit as st
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto
from translation_utils import translate_text

class CalculatorType(Enum):
    """Enum for different calculator types."""
    RENT_VS_BUY = auto()
    INVESTMENT_PROPERTY = auto()

@dataclass
class NavigationItem:
    """Data model for a navigation item."""
    id: CalculatorType
    label: str
    icon: Optional[str] = None
    help_text: Optional[str] = None

class Navigation:
    """Handles navigation between different calculators."""
    
    def __init__(self, current_lang: str = 'en'):
        """Initialize navigation with default items."""
        self.current_lang = current_lang
        self.nav_items = [
            NavigationItem(
                id=CalculatorType.RENT_VS_BUY,
                label="Rent vs. Buy",
                icon="🏠",
                help_text="Compare renting versus buying a home"
            ),
            NavigationItem(
                id=CalculatorType.INVESTMENT_PROPERTY,
                label="Investment Property",
                icon="💰",
                help_text="Analyze investment property opportunities"
            )
        ]
        
        # Initialize session state if not exists
        if 'current_calculator' not in st.session_state:
            st.session_state.current_calculator = CalculatorType.RENT_VS_BUY

    def create_navigation(self) -> CalculatorType:
        """Create navigation interface and return selected calculator type."""
        # Create navigation buttons in columns
        cols = st.columns(len(self.nav_items))
        
        for col, item in zip(cols, self.nav_items):
            with col:
                # Create button with icon if available
                button_label = f"{item.icon} {translate_text(item.label, self.current_lang)}" if item.icon else translate_text(item.label, self.current_lang)
                
                if st.button(
                    button_label,
                    help=translate_text(item.help_text, self.current_lang) if item.help_text else None,
                    use_container_width=True,
                    type="primary" if st.session_state.current_calculator == item.id else "secondary"
                ):
                    st.session_state.current_calculator = item.id
        
        return st.session_state.current_calculator

class NavigationManager:
    """Manages the overall navigation state and layout."""
    
    @staticmethod
    def setup_page_config():
        """Configure the page layout and settings."""
        st.set_page_config(
            layout="wide",
            page_title="Real Estate Financial Calculator",
            page_icon="🏠",
            initial_sidebar_state="collapsed"
        )
    
    @staticmethod
    def get_current_calculator() -> CalculatorType:
        """Get the currently selected calculator type."""
        return st.session_state.current_calculator
    
    @staticmethod
    def create_breadcrumbs():
        """Create breadcrumb navigation (if needed in the future)."""
        # Placeholder for potential breadcrumb navigation
        pass
    
    @staticmethod
    def create_sidebar_nav():
        """Create sidebar navigation (if needed in the future)."""
        # Placeholder for potential sidebar navigation
        pass