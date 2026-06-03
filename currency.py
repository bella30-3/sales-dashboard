"""Currency conversion helpers for the Sales Dashboard."""

import streamlit as st

# Exchange rates relative to USD
RATES = {
    "USD": 1.0,
    "SGD": 1.35,
    "EUR": 0.92,
    "GBP": 0.79,
    "INR": 83.5,
    "THB": 35.0,
    "JPY": 155.0,
    "MYR": 4.70,
    "IDR": 15800.0,
}

SYMBOLS = {
    "USD": "$",
    "SGD": "S$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "THB": "฿",
    "JPY": "¥",
    "MYR": "RM",
    "IDR": "Rp",
}


def convert(amount_usd: float, target_currency: str) -> float:
    """Convert from USD to target currency."""
    rate = RATES.get(target_currency, 1.0)
    return amount_usd * rate


def fmt(amount: float, currency: str = "USD") -> str:
    """Format amount with currency symbol and k/M suffix."""
    symbol = SYMBOLS.get(currency, currency + " ")
    if abs(amount) >= 1_000_000:
        return f"{symbol}{amount / 1_000_000:.2f}M"
    elif abs(amount) >= 1_000:
        return f"{symbol}{amount / 1_000:.2f}k"
    else:
        return f"{symbol}{amount:,.0f}"


def currency_selector(label: str = "Currency", key: str = "currency"):
    """Streamlit selectbox for currency choice."""
    return st.sidebar.selectbox(
        label,
        list(RATES.keys()),
        index=0,
        key=key,
    )
