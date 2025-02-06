import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from translation_utils import translate_text, translate_number_input
from dateutil.relativedelta import relativedelta

def fetch_etf_data(symbol: str, start_date: datetime, end_date: datetime) -> Tuple[pd.DataFrame, Dict]:
    """Fetch historical ETF data."""
    try:
        # Get ETF data
        etf = yf.Ticker(symbol)
        
        # Get historical data with adjusted prices
        hist_data = etf.history(start=start_date, end=end_date, auto_adjust=True)
        
        # Check if we have any data
        if hist_data.empty:
            st.error(f"No historical data available for '{symbol}'. Please check the symbol and try again.")
            return pd.DataFrame(), {}
        
        # Get ETF info - don't error if this fails
        try:
            info = etf.info
        except:
            info = {'shortName': symbol}
            
        actual_years = (hist_data.index[-1] - hist_data.index[0]).days / 365
        info['available_years'] = actual_years
        
        return hist_data, info
        
    except Exception as e:
        st.error(f"Error fetching ETF data: {str(e)}")
        return pd.DataFrame(), {}

def calculate_etf_metrics(hist_data: pd.DataFrame, initial_investment: float, annual_contribution: float = 0, reinvest_dividends: bool = True) -> Dict:
    """Calculate key ETF metrics."""
    if hist_data.empty:
        return {}
    
    # Calculate total return including dividends
    start_price = hist_data['Close'].iloc[0]  # Already adjusted for splits
    end_price = hist_data['Close'].iloc[-1]   # Already adjusted for splits
    
    # Calculate initial shares (using split-adjusted price)
    initial_shares = initial_investment / start_price
    shares = initial_shares
    
    # Create daily value tracking DataFrame
    daily_data = pd.DataFrame(index=hist_data.index)
    daily_data['Close'] = hist_data['Close']
    daily_data['Shares'] = initial_shares
    daily_data['Value'] = daily_data['Close'] * daily_data['Shares']
    daily_data['Dividends'] = hist_data['Dividends']
    daily_data['Cumulative_Dividends'] = 0.0
    daily_data['Contributions'] = 0.0
    daily_data['Cumulative_Contributions'] = initial_investment
    
    # Track running totals
    total_dividends = 0
    total_cash_dividends = 0
    total_contributions = initial_investment
    
    # Get the start year
    start_year = hist_data.index[0].year
    current_year = start_year
    
    # Process each day
    for i in range(1, len(daily_data)):
        current_date = daily_data.index[i]
        
        # Add annual contribution at the start of each year (except first year)
        if current_date.year > current_year and annual_contribution > 0:
            # Buy new shares with the contribution
            new_shares = annual_contribution / daily_data['Close'].iloc[i]
            daily_data['Shares'].iloc[i:] += new_shares
            total_contributions += annual_contribution
            daily_data['Contributions'].iloc[i] = annual_contribution
            daily_data['Cumulative_Contributions'].iloc[i:] = total_contributions
            current_year = current_date.year
        
        # Get dividend for the day
        dividend = daily_data['Dividends'].iloc[i]
        if dividend > 0:
            dividend_amount = dividend * daily_data['Shares'].iloc[i-1]
            total_cash_dividends += dividend_amount
            
            if reinvest_dividends:
                # Calculate new shares from dividend reinvestment
                new_shares = dividend_amount / daily_data['Close'].iloc[i]
                daily_data['Shares'].iloc[i:] += new_shares
                total_dividends += dividend_amount
            
            daily_data['Cumulative_Dividends'].iloc[i:] = total_cash_dividends
        else:
            daily_data['Shares'].iloc[i] = daily_data['Shares'].iloc[i-1]
    
    # Calculate daily values
    daily_data['Value'] = daily_data['Close'] * daily_data['Shares']
    
    # Calculate final values
    final_value = daily_data['Value'].iloc[-1]
    total_return = ((final_value - total_contributions) / total_contributions) * 100
    
    # Calculate annualized return (CAGR)
    years = (hist_data.index[-1] - hist_data.index[0]).days / 365.25
    annual_return = ((final_value / initial_investment) ** (1/years) - 1) * 100
    
    # Calculate volatility using daily returns (annualized)
    daily_returns = daily_data['Close'].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    
    # Group by year for annual metrics
    yearly_data = daily_data.resample('Y').agg({
        'Close': 'last',
        'Shares': 'last',
        'Value': 'last',
        'Dividends': 'sum',
        'Cumulative_Dividends': 'last',
        'Contributions': 'sum',
        'Cumulative_Contributions': 'last'
    })
    
    # Calculate average annual dividend
    if years > 0:
        avg_annual_cash_dividend = total_cash_dividends / years
    else:
        avg_annual_cash_dividend = 0
    
    metrics = {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'current_value': final_value,
        'annual_dividend_income': avg_annual_cash_dividend,
        'current_shares': daily_data['Shares'].iloc[-1],
        'total_dividends': total_dividends,
        'total_cash_dividends': total_cash_dividends,
        'total_contributions': total_contributions,
        'initial_shares': initial_shares,
        'daily_data': daily_data,
        'yearly_data': yearly_data
    }
    
    # Add debug information in an expander
    with st.expander("Show Calculation Details"):
        st.write("Initial Investment Details:")
        st.write(f"- Initial Investment: ${initial_investment:,.2f}")
        st.write(f"- Annual Contribution: ${annual_contribution:,.2f}")
        st.write(f"- Start Price (Split Adjusted): ${start_price:.2f}")
        st.write(f"- Initial Shares: {initial_shares:,.2f}")
        st.write(f"- Start Date: {hist_data.index[0].strftime('%Y-%m-%d')}")
        st.write(f"- End Date: {hist_data.index[-1].strftime('%Y-%m-%d')}")
        st.write(f"- Total Years: {years:.2f}")
        
        st.write("\nYearly Data:")
        for year, row in yearly_data.iterrows():
            st.write(f"{year.year}:")
            st.write(f"- Year-end price: ${row['Close']:.2f}")
            st.write(f"- Year-end shares: {row['Shares']:,.2f}")
            st.write(f"- Year-end value: ${row['Value']:,.2f}")
            st.write(f"- Year contributions: ${row['Contributions']:,.2f}")
            st.write(f"- Total contributions: ${row['Cumulative_Contributions']:,.2f}")
            st.write(f"- Year dividends: ${row['Dividends'] * row['Shares']:,.2f}")
            yearly_return = (row['Value'] / yearly_data['Value'].shift(1).iloc[yearly_data.index.get_loc(year)] - 1) * 100 if yearly_data.index.get_loc(year) > 0 else 0
            st.write(f"- Year Return: {yearly_return:.2f}%")
        
        st.write("\nFinal Calculations:")
        st.write(f"- Total Contributions: ${total_contributions:,.2f}")
        st.write(f"- Total Cash Dividends: ${total_cash_dividends:,.2f}")
        st.write(f"- Number of Years: {years:.2f}")
        st.write(f"- Average Annual Cash Dividend: ${avg_annual_cash_dividend:,.2f}")
        st.write(f"- Current Shares: {daily_data['Shares'].iloc[-1]:,.2f}")
        st.write(f"- End Price: ${end_price:.2f}")
        st.write(f"- Final Value: ${final_value:,.2f}")
        st.write(f"- CAGR: {annual_return:.2f}%")
        st.write(f"- Daily Volatility: {daily_returns.std() * 100:.2f}%")
        st.write(f"- Annualized Volatility: {volatility:.2f}%")
    
    return metrics

def calculate_tax_brackets(annual_salary: float) -> Dict[str, float]:
    """Calculate tax deductions based on 2025 tax brackets."""
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
    prev_bracket = 0
    
    for bracket, rate in brackets:
        if remaining_income <= 0:
            break
            
        taxable_amount = min(remaining_income, bracket - prev_bracket)
        DOLLAR = "&#36;"
        bracket_range = DOLLAR + str(prev_bracket) + " up to " + DOLLAR + str(bracket)
        tax_paid[bracket_range] = taxable_amount * rate
        remaining_income -= taxable_amount
        prev_bracket = bracket
    
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
