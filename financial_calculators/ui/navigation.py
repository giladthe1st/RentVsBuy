import streamlit as st
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto

class CalculatorType(Enum):
    """Enum for different calculator types."""
    RENT_VS_BUY = auto()
    INVESTMENT_PROPERTY = auto()
    ETF_COMPARISON = auto()

@dataclass
class NavigationItem:
    """Data class for navigation items."""
    id: CalculatorType
    label: str
    icon: Optional[str] = None
    help_text: Optional[str] = None

class Navigation:
    """Navigation component for the calculator."""
    def __init__(self):
        """Initialize navigation with default items."""
        self.nav_items = [
            NavigationItem(
                id=CalculatorType.RENT_VS_BUY,
                label="Rent vs. Buy",
                icon="🏠",
                help_text="Compare renting vs. buying a home"
            ),
            NavigationItem(
                id=CalculatorType.INVESTMENT_PROPERTY,
                label="Investment Property",
                icon="💰",
                help_text="Analyze investment property opportunities"
            ),
            NavigationItem(
                id=CalculatorType.ETF_COMPARISON,
                label="ETF Comparison",
                icon="📈",
                help_text="Compare ETF investments with real estate"
            )
        ]

    def render(self):
        """Render the navigation component."""
        # Create columns for each navigation item
        cols = st.columns(len(self.nav_items))
        
        for col, item in zip(cols, self.nav_items):
            with col:
                button_label = f"{item.icon} {item.label}" if item.icon else item.label
                is_selected = st.session_state.current_calculator == item.id
                
                if st.button(
                    button_label,
                    key=f"nav_button_{item.id}",
                    help=item.help_text if item.help_text else None,
                    type="primary" if is_selected else "secondary",
                    use_container_width=True
                ):
                    st.session_state.current_calculator = item.id
                    st.rerun()

class NavigationManager:
    """Manager for handling navigation state and rendering."""
    def __init__(self):
        """Initialize navigation manager."""
        if 'current_calculator' not in st.session_state:
            st.session_state.current_calculator = CalculatorType.RENT_VS_BUY
        
        self.navigation = Navigation()
    
    def render(self):
        """Render navigation and current calculator."""
        self.navigation.render()