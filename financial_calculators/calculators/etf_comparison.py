import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from translation_utils import translate_text, translate_number_input
from dateutil.relativedelta import relativedelta
from functools import lru_cache

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_etf_data(symbol: str, start_date: datetime, end_date: datetime) -> Tuple[pd.DataFrame, Dict]:
    """Fetch historical ETF data with caching."""
    try:
        etf = yf.Ticker(symbol)
        hist_data = etf.history(start=start_date, end=end_date, auto_adjust=True)
        
        if hist_data.empty:
            st.error(f"No historical data available for '{symbol}'. Please check the symbol and try again.")
            return pd.DataFrame(), {}
        
        try:
            info = etf.info
        except:
            info = {'shortName': symbol}
            
        info['available_years'] = (hist_data.index[-1] - hist_data.index[0]).days / 365
        return hist_data, info
        
    except Exception as e:
        st.error(f"Error fetching ETF data: {str(e)}")
        return pd.DataFrame(), {}

def calculate_etf_metrics(hist_data: pd.DataFrame, initial_investment: float, annual_contribution: float = 0, reinvest_dividends: bool = True) -> Dict:
    """Calculate key ETF metrics using vectorized operations."""
    if hist_data.empty:
        return {}
    
    # Initialize DataFrame with required columns
    daily_data = pd.DataFrame(index=hist_data.index)
    daily_data['Close'] = hist_data['Close']
    daily_data['Dividends'] = hist_data['Dividends']
    
    # Calculate initial shares
    initial_shares = initial_investment / daily_data['Close'].iloc[0]
    
    # Create year markers for contributions
    daily_data['Year'] = daily_data.index.year
    year_starts = daily_data.groupby('Year').head(1).index[1:]  # Skip first year
    
    # Initialize shares array
    shares = np.full(len(daily_data), initial_shares)
    
    # Calculate contributions
    contributions = np.zeros(len(daily_data))
    if annual_contribution > 0:
        for date in year_starts:
            idx = daily_data.index.get_loc(date)
            new_shares = annual_contribution / daily_data['Close'].iloc[idx]
            shares[idx:] += new_shares
            contributions[idx] = annual_contribution
    
    daily_data['Shares'] = shares
    daily_data['Contributions'] = contributions
    daily_data['Cumulative_Contributions'] = np.cumsum(contributions) + initial_investment
    
    # Process dividends efficiently
    if reinvest_dividends:
        dividend_shares = (daily_data['Dividends'] * daily_data['Shares']).fillna(0) / daily_data['Close']
        daily_data['Dividend_Shares'] = dividend_shares
        daily_data['Shares'] = daily_data['Shares'] + dividend_shares.cumsum()
    
    # Calculate values
    daily_data['Value'] = daily_data['Close'] * daily_data['Shares']
    daily_data['Cumulative_Dividends'] = (daily_data['Dividends'] * daily_data['Shares']).fillna(0).cumsum()
    
    # Calculate metrics
    final_value = daily_data['Value'].iloc[-1]
    total_contributions = daily_data['Cumulative_Contributions'].iloc[-1]
    total_return = ((final_value - total_contributions) / total_contributions) * 100
    
    years = (hist_data.index[-1] - hist_data.index[0]).days / 365.25
    annual_return = ((final_value / initial_investment) ** (1/years) - 1) * 100
    
    # Calculate volatility using vectorized operations
    daily_returns = daily_data['Close'].pct_change()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    
    # Calculate yearly metrics efficiently
    yearly_data = daily_data.resample('Y').agg({
        'Close': 'last',
        'Shares': 'last',
        'Value': 'last',
        'Dividends': 'sum',
        'Cumulative_Dividends': 'last',
        'Contributions': 'sum',
        'Cumulative_Contributions': 'last'
    })
    
    total_cash_dividends = daily_data['Cumulative_Dividends'].iloc[-1]
    avg_annual_cash_dividend = total_cash_dividends / years if years > 0 else 0
    
    metrics = {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'current_value': final_value,
        'annual_dividend_income': avg_annual_cash_dividend,
        'current_shares': daily_data['Shares'].iloc[-1],
        'total_dividends': total_cash_dividends,
        'total_cash_dividends': total_cash_dividends,
        'total_contributions': total_contributions,
        'initial_shares': initial_shares,
        'daily_data': daily_data,
        'yearly_data': yearly_data
    }
    
    _display_debug_info(metrics, hist_data, initial_investment, annual_contribution, yearly_data)
    return metrics

def _display_debug_info(metrics: Dict, hist_data: pd.DataFrame, initial_investment: float, annual_contribution: float, yearly_data: pd.DataFrame) -> None:
    """Display debug information in a streamlit expander."""
    with st.expander("Show Calculation Details"):
        years = (hist_data.index[-1] - hist_data.index[0]).days / 365.25
        
        st.write("Initial Investment Details:")
        st.write({
            'Initial Investment': f"${initial_investment:,.2f}",
            'Annual Contribution': f"${annual_contribution:,.2f}",
            'Start Price': f"${hist_data['Close'].iloc[0]:.2f}",
            'Initial Shares': f"{metrics['initial_shares']:,.2f}",
            'Date Range': f"{hist_data.index[0].strftime('%Y-%m-%d')} to {hist_data.index[-1].strftime('%Y-%m-%d')}",
            'Total Years': f"{years:.2f}"
        })
        
        st.write("\nYearly Data:")
        for year, row in yearly_data.iterrows():
            yearly_return = (row['Value'] / yearly_data['Value'].shift(1).iloc[yearly_data.index.get_loc(year)] - 1) * 100 if yearly_data.index.get_loc(year) > 0 else 0
            st.write({
                'Year': year.year,
                'Price': f"${row['Close']:.2f}",
                'Shares': f"{row['Shares']:,.2f}",
                'Value': f"${row['Value']:,.2f}",
                'Contributions': f"${row['Contributions']:,.2f}",
                'Total Contributions': f"${row['Cumulative_Contributions']:,.2f}",
                'Dividends': f"${row['Dividends'] * row['Shares']:,.2f}",
                'Return': f"{yearly_return:.2f}%"
            })
        
        st.write("\nFinal Calculations:", {
            'Total Contributions': f"${metrics['total_contributions']:,.2f}",
            'Total Cash Dividends': f"${metrics['total_cash_dividends']:,.2f}",
            'Years': f"{years:.2f}",
            'Avg Annual Dividend': f"${metrics['annual_dividend_income']:,.2f}",
            'Final Shares': f"{metrics['current_shares']:,.2f}",
            'Final Value': f"${metrics['current_value']:,.2f}",
            'CAGR': f"{metrics['annual_return']:.2f}%",
            'Volatility': f"{metrics['volatility']:.2f}%"
        })

@lru_cache(maxsize=128)
def calculate_tax_brackets(annual_salary: float) -> Dict[str, float]:
    """Calculate tax deductions based on 2025 tax brackets with caching."""
    brackets = [
        (47564, 0.2580),
        (57375, 0.2775),
        (101200, 0.3325),
        (114750, 0.3790),
        (177882, 0.4340),
        (200000, 0.4672),
        (253414, 0.4758),
        (400000, 0.5126),
        (float('inf'), 0.5040)
    ]
    
    tax_paid = {}
    remaining_income = annual_salary
    prev_threshold = 0
    
    for threshold, rate in brackets:
        if remaining_income <= 0:
            break
            
        taxable_amount = min(remaining_income, threshold - prev_threshold)
        tax_paid[f"{rate*100:.2f}%"] = taxable_amount * rate
        remaining_income -= taxable_amount
        prev_threshold = threshold
    
    return tax_paid

def calculate_yearly_etf_performance(initial_investment: float, annual_return: float, annual_contribution: float, 
                                   years: int, hist_data: pd.DataFrame = None, initial_shares: float = None,
                                   reinvest_dividends: bool = True) -> pd.DataFrame:
    """Calculate yearly ETF performance including contributions and dividends."""
    yearly_data = []
    current_value = initial_investment
    shares = initial_shares if initial_shares is not None else initial_investment / hist_data['Close'][0]
    
    # Calculate average dividend yield using historical data
    if hist_data is not None:
        yearly_data_hist = hist_data.resample('Y').agg({
            'Dividends': 'sum',
            'Close': 'mean'
        })
        avg_dividend_yield = (yearly_data_hist['Dividends'].mean() / yearly_data_hist['Close'].mean()) * 100
    else:
        avg_dividend_yield = 0
    
    for year in range(years + 1):
        if year > 0:
            # Calculate dividend for the year based on current shares
            dividend_amount = (current_value * avg_dividend_yield / 100) if hist_data is not None else 0
            
            # Add annual contribution at start of year
            current_value += annual_contribution
            
            # Apply annual return (excluding dividends as they're calculated separately)
            current_value *= (1 + (annual_return - avg_dividend_yield)/100)
            
            # Handle dividends based on reinvestment choice
            if reinvest_dividends:
                current_value += dividend_amount
                # Increase shares proportionally
                shares *= (current_value / (current_value - dividend_amount))
        
        yearly_data.append({
            'Year': year,
            'Value': current_value,
            'Cumulative Contribution': initial_investment + (annual_contribution * year),
            'Annual Dividend': 0 if year == 0 else dividend_amount
        })
    
    return pd.DataFrame(yearly_data)

def show(property_metrics: Dict = None):
    """Display ETF comparison calculator."""
    current_lang = st.session_state.get('current_lang', 'en')
    
    st.subheader("📈 " + translate_text("Investment Comparison", current_lang))
    
    # Create three columns for better layout
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Basic ETF inputs
        etf_symbol = st.text_input(
            translate_text("ETF Symbol", current_lang),
            value="SPY",
            help="Enter ETF symbol (e.g., SPY, VTI, QQQ)"
        )
        
        annual_salary = translate_number_input(
            "Annual Household Income ($)",
            current_lang,
            min_value=0.0,
            value=100000.0,
            step=1000.0
        )
        
        investment_amount = st.number_input(
            translate_text("Initial Investment Amount ($)", current_lang),
            min_value=0.0,
            value=property_metrics.get('down_payment', 50000.0) if property_metrics else 50000.0,
            step=1000.0
        )
    
    with col2:
        # Additional investment inputs
        annual_contribution = translate_number_input(
            "Annual Additional Investment ($)",
            current_lang,
            min_value=0.0,
            value=0.0,
            step=1000.0
        )
        
        # Date selection
        default_end_date = datetime.now()
        default_start_date = default_end_date - timedelta(days=10*365)  # 10 years by default
        
        # Month/Year selection for end date
        st.write(translate_text("End Date", current_lang))
        end_col1, end_col2 = st.columns(2)
        with end_col1:
            end_month = st.selectbox(
                "End Month",
                range(1, 13),
                index=default_end_date.month - 1,
                format_func=lambda x: datetime(2000, x, 1).strftime('%B')
            )
        with end_col2:
            year_range = list(range(2000, default_end_date.year + 1))
            end_year = st.selectbox(
                "End Year",
                year_range,
                index=len(year_range) - 1  # Select the last year
            )
        
        # Month/Year selection for start date
        st.write(translate_text("Start Date", current_lang))
        start_col1, start_col2 = st.columns(2)
        with start_col1:
            start_month = st.selectbox(
                "Start Month",
                range(1, 13),
                index=default_start_date.month - 1,
                format_func=lambda x: datetime(2000, x, 1).strftime('%B')
            )
        with start_col2:
            year_range = list(range(2000, end_year + 1))
            default_start_year_index = max(0, len(year_range) - 11)  # 10 years back or earliest available
            start_year = st.selectbox(
                "Start Year",
                year_range,
                index=default_start_year_index
            )
            
        reinvest_dividends = st.checkbox(
            translate_text("Reinvest Dividends", current_lang),
            value=True,
            help="If checked, dividends will be automatically reinvested to buy more shares"
        )
    
    # Calculate tax brackets
    tax_brackets = calculate_tax_brackets(annual_salary)
    total_tax = sum(tax_brackets.values())
    net_income = annual_salary - total_tax
    
    # Display tax information in a new container
    with st.expander("💰 " + translate_text("Tax Breakdown", current_lang)):
        st.write(translate_text("Annual Income:", current_lang), f"${annual_salary:,.2f}")
        st.write(translate_text("Total Tax:", current_lang), f"${total_tax:,.2f}")
        st.write(translate_text("Net Income:", current_lang), f"${net_income:,.2f}")
        
        # Display tax brackets
        st.write("### " + translate_text("Tax Brackets Breakdown", current_lang))
        for bracket, amount in tax_brackets.items():
            st.write(f"{bracket}: ${amount:,.2f}")
    
    if etf_symbol:
        try:
            # Create dates from selected month/year
            start_date = datetime(start_year, start_month, 1)
            end_date = datetime(end_year, end_month, 1) + relativedelta(months=1) - timedelta(days=1)  # Last day of selected month
            
            # Fetch ETF data
            hist_data, etf_info = fetch_etf_data(etf_symbol, start_date, end_date)
            
            if not hist_data.empty:
                # Use actual available years for calculations if less than requested
                actual_years = etf_info.get('available_years', (end_date - start_date).days / 365)
                metrics = calculate_etf_metrics(hist_data, investment_amount, annual_contribution, reinvest_dividends)
                
                with col3:
                    st.markdown("### " + translate_text("ETF Metrics", current_lang))
                    
                    # Show ETF info if available
                    if etf_info:
                        st.markdown(f"**{etf_info.get('shortName', etf_symbol)}**")
                        if 'longName' in etf_info:
                            st.markdown(f"*{etf_info['longName']}*")
                    
                    st.metric(translate_text("Total Return", current_lang), f"{metrics['total_return']:.2f}%")
                    st.metric(translate_text("Annual Return", current_lang), f"{metrics['annual_return']:.2f}%")
                    st.metric(translate_text("Annual Dividend Income", current_lang), f"${metrics['annual_dividend_income']:,.2f}")
                    st.metric(translate_text("Current Investment Value", current_lang), f"${metrics['current_value']:,.2f}")
                    st.metric(translate_text("Volatility", current_lang), f"{metrics['volatility']:.2f}%")
                    st.metric(translate_text("Total Dividends Earned", current_lang), f"${metrics['total_cash_dividends']:,.2f}")
                
                # Calculate yearly performance using actual available years
                yearly_performance = calculate_yearly_etf_performance(
                    investment_amount,
                    metrics['annual_return'],
                    annual_contribution,
                    int(actual_years),
                    hist_data,
                    metrics['current_shares'],
                    reinvest_dividends
                )
                
                # Create detailed yearly chart
                st.markdown("### " + translate_text("Yearly Performance", current_lang))
                
                fig = go.Figure()
                
                # Add investment value line
                fig.add_trace(go.Scatter(
                    name=translate_text('Investment Value', current_lang),
                    x=yearly_performance['Year'],
                    y=yearly_performance['Value'],
                    line=dict(color='green')
                ))
                
                # Add contribution line
                fig.add_trace(go.Scatter(
                    name=translate_text('Total Contribution', current_lang),
                    x=yearly_performance['Year'],
                    y=yearly_performance['Cumulative Contribution'],
                    line=dict(color='blue', dash='dash')
                ))
                
                # Add dividend income line with secondary y-axis
                fig.add_trace(go.Bar(
                    name=translate_text('Annual Dividend Income', current_lang),
                    x=yearly_performance['Year'],
                    y=yearly_performance['Annual Dividend'],
                    marker=dict(
                        color='rgba(0, 255, 0, 0.2)',  # Transparent green
                        line=dict(color='rgba(0, 255, 0, 0.5)', width=1)  # Slightly more opaque border
                    ),
                    yaxis='y2'  # Use secondary y-axis
                ))
                
                # Update layout with secondary y-axis
                fig.update_layout(
                    title=translate_text('Investment Growth Over Time', current_lang),
                    xaxis_title=translate_text('Years', current_lang),
                    yaxis_title=translate_text('Value ($)', current_lang),
                    yaxis2=dict(
                        title=translate_text('Dividend Income ($)', current_lang),
                        overlaying='y',
                        side='right',
                        showgrid=False,
                        rangemode='tozero'
                    ),
                    hovermode='x unified',
                    barmode='overlay',
                    showlegend=True
                )
                
                st.plotly_chart(fig, key="yearly_performance")
                
                # Show daily value graph
                st.markdown("### " + translate_text("Daily Investment Value", current_lang))
                
                fig = go.Figure()
                
                # Add investment value line
                fig.add_trace(go.Scatter(
                    name=translate_text('Investment Value', current_lang),
                    x=metrics['daily_data'].index,
                    y=metrics['daily_data']['Value'],
                    line=dict(color='green')
                ))
                
                # Add cumulative dividends line
                fig.add_trace(go.Scatter(
                    name=translate_text('Cumulative Dividends', current_lang),
                    x=metrics['daily_data'].index,
                    y=metrics['daily_data']['Cumulative_Dividends'],
                    line=dict(color='blue', dash='dash')
                ))
                
                fig.update_layout(
                    title=translate_text('Daily Investment Value and Cumulative Dividends', current_lang),
                    xaxis_title=translate_text('Date', current_lang),
                    yaxis_title=translate_text('Value ($)', current_lang),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, key="daily_value")
                
                # Create comparison if property metrics are available
                if property_metrics:
                    st.markdown("### 📊 " + translate_text("Investment Comparison", current_lang))
                    
                    comparison_data = {
                        'Metric': [
                            translate_text("Annual Return (%)", current_lang),
                            translate_text("Monthly Income ($)", current_lang),
                            translate_text("Initial Investment ($)", current_lang),
                            translate_text("Current Investment Value", current_lang)
                        ],
                        'Real Estate': [
                            property_metrics.get('annual_return', 0),
                            property_metrics.get('monthly_cash_flow', 0),
                            property_metrics.get('down_payment', 0),
                            property_metrics.get('property_value', 0)
                        ],
                        'ETF Investment': [
                            metrics['annual_return'],
                            metrics['annual_dividend_income'] / 12,
                            investment_amount,
                            metrics['current_value']
                        ]
                    }
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df.style.format({
                        'Real Estate': '${:,.2f}',
                        'ETF Investment': '${:,.2f}'
                    }))
                    
                    # Create comparison chart
                    fig = go.Figure()
                    
                    # Add real estate line
                    fig.add_trace(go.Scatter(
                        name='Real Estate',
                        x=list(range(int(actual_years) + 1)),
                        y=[property_metrics['down_payment']] + [
                            property_metrics['property_value'] * (1 + property_metrics['appreciation_rate']/100)**year 
                            for year in range(1, int(actual_years) + 1)
                        ],
                        line=dict(color='blue')
                    ))
                    
                    # Add ETF line with contributions
                    fig.add_trace(go.Scatter(
                        name='ETF Investment',
                        x=yearly_performance['Year'],
                        y=yearly_performance['Value'],
                        line=dict(color='green')
                    ))
                    
                    fig.update_layout(
                        title=translate_text('Investment Value Over Time', current_lang),
                        xaxis_title=translate_text('Years', current_lang),
                        yaxis_title=translate_text('Value ($)', current_lang),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, key="comparison_chart")
        except Exception as e:
            st.error(f"Error calculating ETF metrics: {str(e)}")
