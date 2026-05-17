"""Shared currency config for dashboards."""

EXCHANGE_RATES = {
    "USD": 1.0,
    "SGD": 1.35,
    "INR": 85.5,
    "THB": 35.0,
    "EUR": 0.92,
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "SGD": "S$",
    "INR": "₹",
    "THB": "฿",
    "EUR": "€",
}

# Map countries to their local currency
LOCAL_CURRENCY = {
    "India": "INR",
    "Singapore": "SGD",
    "Thailand": "THB",
    "Europe": "EUR",
}


def convert(amount_usd, target_currency):
    """Convert from USD to target currency."""
    return amount_usd * EXCHANGE_RATES.get(target_currency, 1.0)


def fmt(amount, currency):
    """Format amount with currency symbol."""
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    if amount >= 1_000_000:
        return f"{symbol}{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{symbol}{amount/1_000:.1f}K"
    else:
        return f"{symbol}{amount:,.0f}"


def currency_selector(label="Display Currency", key="currency"):
    """Streamlit sidebar currency selector. Returns currency code."""
    import streamlit as st
    options = list(EXCHANGE_RATES.keys())
    return st.sidebar.selectbox(label, options, index=1, key=key)  # default SGD


def get_currency_for_country(country, selected):
    """Resolve selected currency — 'Local' maps to country's currency."""
    if selected == "Local":
        return LOCAL_CURRENCY.get(country, "USD")
    return selected
