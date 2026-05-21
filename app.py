import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import numpy as np
from currency import convert, fmt, currency_selector

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide", initial_sidebar_state="expanded", page_icon="🌊")

# ─────────────────────────────────────────────
# THEMES
# ─────────────────────────────────────────────
THEMES = {
    "🎨 Fun": {
        "sidebar_css": "linear-gradient(180deg, #F3E5F5 0%, #E8EAF6 50%, #E0F7FA 100%)",
        "sidebar_border": "1px solid #E8EAF6",
        "active_radio": "#7B1FA2",
        "sidebar_hr": "rgba(123, 31, 162, 0.15)",
        "heading_color": "#1A237E",
        "metric_gradient": "linear-gradient(135deg, rgba(46, 125, 50, 0.06) 0%, rgba(123, 31, 162, 0.06) 50%, rgba(3, 155, 229, 0.06) 100%)",
        "metric_border": "rgba(123, 31, 162, 0.1)",
        "metric_value_color": "#1A237E",
        "tab_active_bg": "linear-gradient(135deg, #7B1FA2 0%, #039BE5 100%)",
        "tab_active_shadow": "rgba(123, 31, 162, 0.25)",
        "tab_list_bg": "rgba(232, 234, 246, 0.4)",
        "chart_title_color": "#1A237E",
        "chart_bg": "rgba(123, 31, 162, 0.015)",
        "chart_grid": "rgba(123, 31, 162, 0.06)",
        "product_colors": {
            "Income Protection Insurance": "#2E7D32",
            "Electric Vehicles / Auto": "#7B1FA2",
            "Care - Aqua Warranty": "#039BE5",
        },
        "paid_color": "#26A69A",
        "outstanding_color": "#FF8A65",
        "target_color": "#66BB6A",
        "product_default": "#7B1FA2",
    },
    "👔 Executive": {
        "sidebar_css": "linear-gradient(180deg, #1E3A5F 0%, #0F3460 100%)",
        "sidebar_border": "1px solid #2D4A7A",
        "active_radio": "#D4A017",
        "sidebar_hr": "rgba(212, 160, 23, 0.3)",
        "heading_color": "#1E3A5F",
        "metric_gradient": "linear-gradient(135deg, rgba(30, 58, 95, 0.06) 0%, rgba(15, 118, 110, 0.06) 100%)",
        "metric_border": "rgba(30, 58, 95, 0.12)",
        "metric_value_color": "#1E3A5F",
        "tab_active_bg": "linear-gradient(135deg, #1E3A5F 0%, #0F766E 100%)",
        "tab_active_shadow": "rgba(30, 58, 95, 0.3)",
        "tab_list_bg": "rgba(226, 232, 240, 0.5)",
        "chart_title_color": "#1E3A5F",
        "chart_bg": "rgba(30, 58, 95, 0.015)",
        "chart_grid": "rgba(100, 116, 139, 0.1)",
        "product_colors": {
            "Income Protection Insurance": "#0F766E",
            "Electric Vehicles / Auto": "#D4A017",
            "Care - Aqua Warranty": "#60A5FA",
        },
        "paid_color": "#0F766E",
        "outstanding_color": "#D4A017",
        "target_color": "#64748B",
        "product_default": "#64748B",
        "sidebar_text_color": "#E2E8F0",
        "sidebar_radio_color": "#CBD5E1",
        "sidebar_radio_checked": "#D4A017",
    },
    "✨ Clean": {
        "sidebar_css": "linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)",
        "sidebar_border": "1px solid #E2E8F0",
        "active_radio": "#3B82F6",
        "sidebar_hr": "rgba(59, 130, 246, 0.15)",
        "heading_color": "#1E293B",
        "metric_gradient": "linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)",
        "metric_border": "rgba(59, 130, 246, 0.1)",
        "metric_value_color": "#1E293B",
        "tab_active_bg": "linear-gradient(135deg, #3B82F6 0%, #10B981 100%)",
        "tab_active_shadow": "rgba(59, 130, 246, 0.25)",
        "tab_list_bg": "rgba(241, 245, 249, 0.6)",
        "chart_title_color": "#1E293B",
        "chart_bg": "rgba(59, 130, 246, 0.01)",
        "chart_grid": "rgba(59, 130, 246, 0.07)",
        "product_colors": {
            "Income Protection Insurance": "#3B82F6",
            "Electric Vehicles / Auto": "#1D4ED8",
            "Care - Aqua Warranty": "#93C5FD",
        },
        "paid_color": "#10B981",
        "outstanding_color": "#F59E0B",
        "target_color": "#64748B",
        "product_default": "#64748B",
        "country_product_colors": {
            ("Care - Aqua Warranty", "Europe"): "#93C5FD",
            ("Income Protection Insurance", "Europe"): "#3B82F6",
            ("Electric Vehicles / Auto", "Europe"): "#1D4ED8",
            ("Care - Aqua Warranty", "Singapore"): "#6EE7B7",
            ("Income Protection Insurance", "Singapore"): "#10B981",
            ("Electric Vehicles / Auto", "Singapore"): "#047857",
            ("Care - Aqua Warranty", "Thailand"): "#C4B5FD",
            ("Income Protection Insurance", "Thailand"): "#8B5CF6",
            ("Electric Vehicles / Auto", "Thailand"): "#5B21B6",
            ("Care - Aqua Warranty", "India"): "#FCD34D",
            ("Income Protection Insurance", "India"): "#F59E0B",
            ("Electric Vehicles / Auto", "India"): "#B45309",
        },
    },
}
# Dynamic CSS based on selected theme
_is_exec = t_theme == "👔 Executive"
_sidebar_text = T.get("sidebar_text_color", "#37474F")
_sidebar_radio = T.get("sidebar_radio_color", "#455A64")
_sidebar_checked = T.get("sidebar_radio_checked", T["active_radio"])

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {{
    font-family: 'Inter', sans-serif;
    background: #FAFBFE;
}}

[data-testid="stSidebar"] {{
    background: {T['sidebar_css']};
    border-right: {T['sidebar_border']};
}}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption {{
    color: {_sidebar_text} !important;
}}

[data-testid="stSidebar"] .stRadio label span {{
    color: {_sidebar_radio} !important;
}}

[data-testid="stSidebar"] .stRadio label[data-checked="true"] span {{
    color: {_sidebar_checked} !important;
    font-weight: 700;
}}

[data-testid="stSidebar"] hr {{
    border-color: {T['sidebar_hr']} !important;
}}

h1, h2, h3 {{
    color: {T['heading_color']} !important;
    font-weight: 700 !important;
}}

.stMetric > div {{
    background: {T['metric_gradient']};
    border-radius: 14px;
    padding: 12px 16px;
    border: 1px solid {T['metric_border']};
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    transition: transform 0.15s ease;
}}

.stMetric > div:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}}

.stMetric label {{
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
}}

.stMetric [data-testid="stMetricValue"] {{
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: {T['metric_value_color']} !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    padding: 4px;
    background: {T['tab_list_bg']};
    border-radius: 12px;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 10px;
    padding: 8px 18px;
    font-weight: 500;
    transition: all 0.2s ease;
}}

.stTabs [aria-selected="true"] {{
    background: {T['tab_active_bg']};
    color: white !important;
    box-shadow: 0 2px 8px {T['tab_active_shadow']};
}}

div[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}}

.stPlotlyChart {{
    border-radius: 12px;
    background: white;
    padding: 4px;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────
PRODUCTS = {
    "EV / Auto": {
        "label": "Electric Vehicles / Auto",
        "desc": "Service Contracts & Warranties",
        "plans": {
            "India": ["EV Warranty"],
            "Singapore": ["EV Warranty"],
            "Thailand": ["EV Warranty"],
        },
    },
    "Income Protection": {
        "label": "Income Protection Insurance",
        "desc": "Contracts & Premiums",
        "plans": {
            "India": ["RQBE (All)"],
            "Singapore": ["DBS Staff 2000", "DBS Staff 5000", "OCBC GA 12M A", "OCBC GA 12M B", "OCBC GA 12M C", "OCBC GA 12M D"],
        },
        "premiums": {
            "DBS Staff 2000": 200,
            "DBS Staff 5000": 450,
            "OCBC GA 12M A": 100,
            "OCBC GA 12M B": 150,
            "OCBC GA 12M C": 200,
            "OCBC GA 12M D": 200,
            "RQBE (All)": 350,
        },
        "types": {
            "DBS Staff 2000": "Individual",
            "DBS Staff 5000": "Individual",
            "OCBC GA 12M A": "Corporate",
            "OCBC GA 12M B": "Corporate",
            "OCBC GA 12M C": "Corporate",
            "OCBC GA 12M D": "Corporate",
            "RQBE (All)": "Individual",
        },
    },
    "Care Aqua": {
        "label": "Care - Aqua Warranty",
        "desc": "Warranty Contracts & Amounts",
        "plans": {
            "India": ["Pure", "Fresh", "Pro"],
            "Singapore": ["Pure", "Fresh", "Pro"],
            "Thailand": ["Pure", "Fresh", "Pro"],
            "Europe": ["Pure", "Fresh", "Pro"],
        },
    },
}

COUNTRIES = {
    "Thailand": "Asia",
    "India": "Asia",
    "Singapore": "Asia",
    "Europe": "Europe",
}
REGIONS = ["Asia", "Europe"]
CLIENTS_BY_PRODUCT_COUNTRY = {
    "EV / Auto": {
        "India": ["Mahindra Trucks and Buses (MTB)"],
        "Singapore": ["BYD", "Porsche", "Cycle and Carriage"],
        "Thailand": ["BYD", "Porsche", "Subaru", "Hyundai", "BYD Forklift"],
    },
    "Income Protection": {
        "India": ["Raheja (RQBE)"],
        "Singapore": ["OCBC (GE)", "DBS (ECICS)"],
        "Thailand": ["Muang Thai"],
    },
    "Care Aqua": {
        "Europe": ["Airspring"],
    },
}

CLIENTS = list(set(c for p in CLIENTS_BY_PRODUCT_COUNTRY.values() for cs in p.values() for c in cs))
TYPES = ["Individual", "Corporate"]
TRAN_TYPES = ["Inst", "Single"]

# Client launch dates (for staggered client entries)
CLIENT_LAUNCH_DATES = {
    "EV / Auto": {
        "Thailand": {
            "BYD": datetime(2024, 7, 1),
            "Porsche": datetime(2025, 1, 1),
            "Subaru": datetime(2026, 1, 1),
            "Hyundai": datetime(2099, 1, 1),  # Not yet active
            "BYD Forklift": datetime(2099, 1, 1),  # Not yet active
        },
        "Singapore": {
            "BYD": datetime(2024, 7, 1),
            "Porsche": datetime(2025, 1, 1),
            "Cycle and Carriage": datetime(2024, 7, 1),
        },
    },
}


def get_plan_premium(prod, plan):
    premiums = PRODUCTS.get(prod, {}).get("premiums", {})
    return premiums.get(plan)

def get_plan_type(prod, plan):
    types = PRODUCTS.get(prod, {}).get("types", {})
    return types.get(plan)

def get_client(product, country, current_date=None):
    clients = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {}).get(country, [])
    if not clients:
        all_pc = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {})
        clients = [c for cs in all_pc.values() for c in cs]
    # Filter by client launch date if applicable
    if current_date and product in CLIENT_LAUNCH_DATES and country in CLIENT_LAUNCH_DATES[product]:
        launch_dates = CLIENT_LAUNCH_DATES[product][country]
        clients = [c for c in clients if c not in launch_dates or current_date >= launch_dates[c]]
    if not clients:
        return "Unknown"
    # EV weighted client selection — realistic contract volume ranking
    if product == "EV / Auto":
        ev_weights = {
            # Singapore
            ("Singapore", "BYD"): 55,
            ("Singapore", "Porsche"): 30,
            ("Singapore", "Cycle and Carriage"): 15,
            # Thailand
            ("Thailand", "BYD"): 30,
            ("Thailand", "Porsche"): 5,
            ("Thailand", "Subaru"): 3,
            ("Thailand", "Hyundai"): 1,
            ("Thailand", "BYD Forklift"): 1,
            # India
            ("India", "Mahindra Trucks and Buses (MTB)"): 1,
        }
        weights = [ev_weights.get((country, c), 1) for c in clients]
        return random.choices(clients, weights=weights, k=1)[0]
    return random.choice(clients)

# Product launch dates
PRODUCT_LAUNCH = {
    "Income Protection": datetime(2023, 7, 1),
    "EV / Auto": datetime(2024, 1, 1),
    "Care Aqua": datetime(2026, 1, 1),
}

# Per-policy premium range in SGD
POLICY_PREMIUM_RANGE_SGD = {
    "Income Protection": (100, 450),
    "EV / Auto": (250, 450),
    "Care Aqua": (1800, 2200),
}

# Monthly contract targets by date range.
# Each entry: (start_date, end_date, monthly_count)
# Evaluated top-to-bottom; first matching range wins.
#
# Targets:
#   IPI  Oct 2024–May 2026: 2,400 total  → ~67/mo pre-2026, 280/mo in 2026
#   EV   Jan 2024–May 2026: 2,000 total  → ~42/mo pre-2026, 400/mo in 2026
#   Aqua Jan 2026–May 2026:    50 total  → 10/mo
MONTHLY_POLICY_COUNTS = {
    "Income Protection": 50,
    "EV / Auto": 30,
    "Care Aqua": 10,
}

RATE_SCHEDULE = {
    "Income Protection": [
        (datetime(2026, 1, 1), datetime(2026, 5, 31), 320),
        (datetime(2024, 10, 1), datetime(2025, 12, 31), 75),
    ],
    "EV / Auto": [
        (datetime(2026, 1, 1), datetime(2026, 5, 31), 400),
        (datetime(2024, 1, 1), datetime(2025, 12, 31), 150),
    ],
    "Care Aqua": [
        (datetime(2026, 1, 1), datetime(2026, 5, 31), 12),
    ],
}

SGD_TO_USD = 1.35

EV_HEALTH_STATES = ["Healthy", "Fair", "Poor"]
EV_BRANDS = ["Mahindra", "BYD", "Porsche", "Subaru", "Hyundai", "Cycle & Carriage"]
EV_COUNTRIES = ["India", "Singapore", "Thailand"]
IPI_PLANS = {
    "DBS Staff 2000": {"premium": 200, "type": "Individual", "insurer": "DBS", "sum_insured": 2000},
    "DBS Staff 5000": {"premium": 450, "type": "Individual", "insurer": "DBS", "sum_insured": 5000},
    "OCBC GA 12M A": {"premium": 100, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 50000},
    "OCBC GA 12M B": {"premium": 150, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 100000},
    "OCBC GA 12M C": {"premium": 200, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 150000},
    "OCBC GA 12M D": {"premium": 200, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 200000},
    "RQBE (All)": {"premium": 350, "type": "Individual", "insurer": "RQBE", "sum_insured": 25000},
}

def _random_n_contracts(target_n, prod):
    """Return a random policy count with tight variance (±15%)."""
    r = random.random()
    if r < 0.05:       # 5% chance: slow month
        return max(3, int(target_n * random.uniform(0.7, 0.85)))
    elif r < 0.25:     # 20% chance: below average
        return max(5, int(target_n * random.uniform(0.85, 0.95)))
    elif r < 0.75:     # 50% chance: around average
        return int(target_n * random.uniform(0.95, 1.05))
    elif r < 0.95:     # 20% chance: good month
        return int(target_n * random.uniform(1.05, 1.15))
    else:              # 5% chance: blowout month
        return int(target_n * random.uniform(1.15, 1.3))

def generate_data():
    """Generate monthly contract data with staggered product launches.
    IPI: Jul 2023, EV: Jan 2024, Aqua: Jan 2026.
    Per-policy premium: 100-450 SGD. Max 300 policies/month.
    """
    rows = []
    end_date = datetime.now()
    current = datetime(2023, 7, 1)

    while current <= end_date:
        year, month = current.year, current.month
        days_in_month = 28 if month == 2 else (30 if month in (4, 6, 9, 11) else 31)

        # Seasonal multiplier
        seasonal = 1.0
        if month in (10, 11, 12):
            seasonal = random.uniform(1.05, 1.2)
        elif month in (1, 2):
            seasonal = random.uniform(0.8, 0.95)
        else:
            seasonal = random.uniform(0.9, 1.1)

        for prod in PRODUCT_LAUNCH:
            launch = PRODUCT_LAUNCH[prod]
            if current < launch:
                continue  # product not launched yet

            # Months since launch (for growth calc)
            months_since_launch = (current.year - launch.year) * 12 + (current.month - launch.month)
            # Ramp-up: start at 40% capacity, reach full after 6 months
            ramp = min(1.0, 0.4 + 0.6 * (months_since_launch / 6))

            # Look up rate from schedule, fall back to default
            target_n = MONTHLY_POLICY_COUNTS[prod]
            for sched_start, sched_end, sched_n in RATE_SCHEDULE.get(prod, []):
                if sched_start <= current <= sched_end:
                    target_n = sched_n
                    break
            premium_lo, premium_hi = POLICY_PREMIUM_RANGE_SGD[prod]
            premium_lo_usd = premium_lo / SGD_TO_USD
            premium_hi_usd = premium_hi / SGD_TO_USD

            n_policies = max(3, int(_random_n_contracts(target_n, prod) * seasonal * ramp))

            for i in range(n_policies):
                # Each policy: random premium in range
                premium_sgd = random.uniform(premium_lo, premium_hi)
                premium = round(premium_sgd / SGD_TO_USD)  # convert to USD

                # Country distribution — weighted so Singapore dominates EV
                if prod == "Care Aqua":
                    country = "Europe"  # Aqua only sold in Europe
                elif prod == "EV / Auto":
                    ev_countries = ["Singapore", "Thailand", "India"]
                    country = random.choices(ev_countries, weights=[60, 32, 8])[0]
                else:
                    country = random.choice([c for c in COUNTRIES.keys() if c != "Europe"])
                region = COUNTRIES[country]

                plan = random.choice(PRODUCTS[prod]["plans"].get(country, PRODUCTS[prod]["plans"][list(PRODUCTS[prod]["plans"].keys())[0]]))
                plan_type = get_plan_type(prod, plan)
                ctype = plan_type if plan_type else random.choice(TYPES)
                client = get_client(prod, country, current)
                trantype = random.choice(TRAN_TYPES)

                paid_pct = random.uniform(0.3, 1.0)
                paid = round(premium * paid_pct)
                outstanding = premium - paid
                inst_count = random.randint(1, 12) if trantype == "Inst" else 1

                start_day = random.randint(1, min(days_in_month, 28))
                start = datetime(year, month, start_day)
                end = start + timedelta(days=365)
                target = round(premium * random.uniform(0.85, 1.15))  # Target close to actuals

                row = {
                    "Contract ID": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(10000,99999)}",
                    "Type": ctype, "Client": client, "Product": prod,
                    "Product Label": PRODUCTS[prod]["label"], "Plan": plan,
                    "Region": region, "Country": country,
                    "Annual Premium": premium, "Paid": paid,
                    "Outstanding": outstanding, "Target": round(target),
                    "Trantype": trantype, "Installment Count": inst_count,
                    "Start Date": start.strftime("%Y-%m-%d"),
                    "End Date": end.strftime("%Y-%m-%d"),
                    "Year": year, "Month": month,
                    "YearMonth": f"{year}-{month:02d}",
                }

                # EV-specific fields
                if prod == "EV / Auto":
                    brand = random.choice(EV_BRANDS)
                    health = random.choices(EV_HEALTH_STATES, weights=[60, 30, 10])[0]
                    age = random.randint(1, 15)
                    km = random.randint(5000, 250000)
                    if age > 10 or km > 150000:
                        health = random.choices(EV_HEALTH_STATES, weights=[20, 40, 40])[0]
                    elif age > 5 or km > 80000:
                        health = random.choices(EV_HEALTH_STATES, weights=[40, 40, 20])[0]
                    claim_count = random.randint(0, 5) if health == "Poor" else random.randint(0, 3)
                    claim_amount = claim_count * random.randint(500, 5000)
                    row.update({
                        "Health State": health,
                        "Brand": brand,
                        "Vehicle Age": age,
                        "KM Driven": km,
                        "Claims": claim_count,
                        "Claim Amount": claim_amount,
                    })

                # IPI-specific fields
                if prod == "Income Protection":
                    plan_info = IPI_PLANS.get(plan, {})
                    ipi_type = plan_info.get("type", ctype)
                    insurer = plan_info.get("insurer", "Unknown")
                    sum_insured = plan_info.get("sum_insured", random.randint(2000, 200000))
                    renewed = random.random() < (0.85 if ipi_type == "Corporate" else 0.65)
                    lives = random.randint(1, 3) if ipi_type == "Corporate" else 1
                    row.update({
                        "Insurer": insurer,
                        "Sum Insured": sum_insured,
                        "Renewed": renewed,
                        "Lives Insured": lives,
                    })

                rows.append(row)

        if month == 12:
            current = datetime(year + 1, 1, 1)
        else:
            current = datetime(year, month + 1, 1)

    return pd.DataFrame(rows)

@st.cache_data
def load_data():
    return generate_data()

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("📊 Sales Dashboard")
st.sidebar.markdown("---")

# Theme selector
t_theme = st.sidebar.selectbox("🎨 Theme", list(THEMES.keys()), key="theme_sel")
T = THEMES[t_theme]

# Dynamic product colors
PRODUCT_COLORS = T["product_colors"]
PAID_COLOR = T["paid_color"]
OUTSTANDING_COLOR = T["outstanding_color"]
TARGET_COLOR = T["target_color"]
PRODUCT_DEFAULT_COLOR = T["product_default"]
BG_COLOR = T["chart_bg"]
GRID_COLOR = T["chart_grid"]

# Clean theme: country-specific product color lookup
def get_product_country_color(product, country):
    cpc = T.get("country_product_colors", {})
    if (product, country) in cpc:
        return cpc[(product, country)]
    return PRODUCT_COLORS.get(product, PRODUCT_DEFAULT_COLOR)

cur = currency_selector("Display Currency", "app_currency")

# Date range filter
st.sidebar.markdown("### 📅 Date Range")
date_min = pd.to_datetime(df["Start Date"]).min().date()
date_max = pd.to_datetime(df["Start Date"]).max().date()
current_year_start = datetime(datetime.now().year, 1, 1).date()
default_start = max(current_year_start, date_min)
date_range = st.sidebar.date_input(
    "Select period",
    value=(default_start, date_max),
    min_value=date_min,
    max_value=date_max,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = date_range
else:
    d_start, d_end = date_min, date_max

df_filtered = df[(pd.to_datetime(df["Start Date"]).dt.date >= d_start) &
                  (pd.to_datetime(df["Start Date"]).dt.date <= d_end)]

# Comparison selector
st.sidebar.markdown("### 🔄 Compare With")
compare_mode = st.sidebar.selectbox(
    "Comparison period",
    ["None", "Previous Year", "Previous Quarter", "Previous Month"],
    index=0,
    key="compare_mode",
)

# Auto-adjust date range for quarter/month comparisons and compute comparison dates
now = datetime.now()
if compare_mode == "Previous Quarter":
    # Snap to current quarter
    q = (d_start.month - 1) // 3 + 1
    q_start_month = (q - 1) * 3 + 1
    d_start = datetime(d_start.year, q_start_month, 1).date()
    q_end_month = q_start_month + 2
    q_end_day = 28 if q_end_month == 2 else (30 if q_end_month in (4, 6, 9, 11) else 31)
    d_end = datetime(d_start.year, q_end_month, q_end_day).date()
    # Previous quarter
    if q == 1:
        cmp_start = datetime(d_start.year - 1, 10, 1).date()
        cmp_end = datetime(d_start.year - 1, 12, 31).date()
    else:
        cmp_s_month = (q - 2) * 3 + 1
        cmp_start = datetime(d_start.year, cmp_s_month, 1).date()
        cmp_e_month = cmp_s_month + 2
        cmp_e_day = 28 if cmp_e_month == 2 else (30 if cmp_e_month in (4, 6, 9, 11) else 31)
        cmp_end = datetime(d_start.year, cmp_e_month, cmp_e_day).date()
    cmp_label = "Prev Quarter"
elif compare_mode == "Previous Month":
    # Snap to current month
    d_start = datetime(d_start.year, d_start.month, 1).date()
    last_day = 28 if d_start.month == 2 else (30 if d_start.month in (4, 6, 9, 11) else 31)
    d_end = datetime(d_start.year, d_start.month, last_day).date()
    # Previous month
    if d_start.month == 1:
        cmp_start = datetime(d_start.year - 1, 12, 1).date()
        cmp_end = datetime(d_start.year - 1, 12, 31).date()
    else:
        cmp_start = datetime(d_start.year, d_start.month - 1, 1).date()
        cmp_e_day = 28 if d_start.month - 1 == 2 else (30 if d_start.month - 1 in (4, 6, 9, 11) else 31)
        cmp_end = datetime(d_start.year, d_start.month - 1, cmp_e_day).date()
    cmp_label = "Prev Month"
elif compare_mode == "Previous Year":
    cmp_start = datetime(d_start.year - 1, d_start.month, d_start.day).date()
    cmp_end = datetime(d_end.year - 1, d_end.month, d_end.day).date()
    cmp_label = "Prev Year"
else:
    cmp_start = None
    cmp_end = None
    cmp_label = ""

# Re-filter with possibly adjusted dates
df_filtered = df[(pd.to_datetime(df["Start Date"]).dt.date >= d_start) &
                  (pd.to_datetime(df["Start Date"]).dt.date <= d_end)]

# Comparison data
cmp_filtered = None
if compare_mode != "None" and cmp_start and cmp_end:
    cmp_filtered = df[(pd.to_datetime(df["Start Date"]).dt.date >= cmp_start) &
                       (pd.to_datetime(df["Start Date"]).dt.date <= cmp_end)]

st.sidebar.markdown("---")
st.sidebar.caption(f"Period: **{d_start}** → **{d_end}**")
if cmp_filtered is not None:
    st.sidebar.caption(f"Compare: **{cmp_start}** → **{cmp_end}**")

PAGES = [
    "🌍 Executive Summary",
    "🗺️ Region Drill Down",
    "🏳️ Country Drill Down",
    "📦 Product Drill Down",
    "🚗 EV Warranty Analysis",
    "🛡️ IPI Policy Analysis",
    "📋 Raw Data",
]
# Support navigation from region drill-down
nav = st.session_state.pop("nav_page", None)
nav_idx = PAGES.index(nav) if nav in PAGES else 0
page = st.sidebar.radio("Navigate", PAGES, index=nav_idx)

st.sidebar.markdown("---")
st.sidebar.caption(f"Contracts: **{len(df_filtered):,}**")
st.sidebar.caption(f"Premium: **{fmt(convert(df_filtered['Annual Premium'].sum(), cur), cur)}**")

# ─────────────────────────────────────────────
# THEME — Cute Futuristic Blue
# ─────────────────────────────────────────────
PALETTE = [
    "#4FC3F7",  # sky blue
    "#81D4FA",  # light blue
    "#80DEEA",  # cyan
    "#B39DDB",  # soft purple
    "#CE93D8",  # lavender
    "#F48FB1",  # pink
    "#FFD54F",  # warm yellow
    "#A5D6A7",  # mint green
]
PALETTE_BARS = ["#4FC3F7", "#80DEEA", "#B39DDB", "#F48FB1", "#FFD54F", "#A5D6A7"]


def _base_layout(fig, height=420):
    fig.update_layout(
        height=height,
        title_font_size=16,
        title_font_color=T.get("chart_title_color", "#1A237E"),
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        plot_bgcolor=BG_COLOR,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#37474F", size=13),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=60, b=50, l=60, r=30),
    )
    return fig

def empty_state(title="No data available"):
    """Return a blank figure with a friendly message for empty DataFrames."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        height=300,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text="No data for selected filters",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color="#90A4AE"),
        )],
    )
    return fig

def _fmt_val(v):
    """Format a numeric value in k/M, handling NaN/inf."""
    if pd.isna(v) or (isinstance(v, float) and np.isinf(v)):
        return "—"
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"{v/1_000:.2f}k"
    else:
        return f"{v:,.0f}"

def bar_chart(data, x, y, title, color=None, barmode="group", height=420, color_map=None):
    title = str(title) if title else ""
    data = data.dropna(subset=[x]).copy()
    data[y] = data[y].fillna(0)
    if data.empty:
        return empty_state(title)
    if color_map:
        fig = px.bar(data, x=x, y=y, color=color, title=title, barmode=barmode,
                     color_discrete_map=color_map)
    else:
        fig = px.bar(data, x=x, y=y, color=color, title=title, barmode=barmode,
                     color_discrete_sequence=PALETTE)
    # Per-trace annotations instead of text= (avoids NaN → "undefined")
    fig.update_traces(textposition="outside", textfont_size=13)
    for trace in fig.data:
        trace.text = [_fmt_val(v) for v in trace.y]
    _base_layout(fig, height)
    return fig

def make_summary(df_in, group_col):
    return df_in.groupby(group_col).agg(
        Contracts=("Contract ID", "count"),
        Total_Premium=("Annual Premium", "sum"),
        Paid=("Paid", "sum"),
        Outstanding=("Outstanding", "sum"),
        Target=("Target", "sum"),
    ).reset_index()

def convert_cols(agg, cols, currency):
    for c in cols:
        agg[c] = agg[c].apply(lambda v: convert(v, currency))
    return agg

# ─────────────────────────────────────────────
# COMPARISON HELPERS
# ─────────────────────────────────────────────

def make_compare_summary(df_curr, df_cmp, group_col):
    """Build a merged summary with Current and Comparison period values."""
    curr = make_summary(df_curr, group_col)
    cmp = make_summary(df_cmp, group_col)
    merged = curr.merge(cmp, on=group_col, how="outer", suffixes=("", "_cmp"))
    merged = merged.fillna(0)
    return merged

def _safe_text(series, currency):
    """Convert a numeric series to formatted text, replacing NaN/inf with '—'."""
    return series.apply(lambda v: fmt(v, currency) if pd.notna(v) and not (isinstance(v, float) and np.isinf(v)) else "—")

def premium_chart(agg, group_col, title, currency, height=420):
    """Stacked bar chart: Paid + Outstanding stacked with total annotations."""
    title = str(title) if title else ""
    agg = agg.dropna(subset=[group_col]).copy()
    if agg.empty:
        return empty_state(title)

    agg["Paid"] = agg["Paid"].fillna(0)
    agg["Outstanding"] = agg["Outstanding"].fillna(0)

    totals = agg["Paid"] + agg["Outstanding"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg[group_col], y=agg["Paid"], name="Paid",
        marker_color=PAID_COLOR, marker_line=dict(width=0),
        text=[fmt(v, currency) for v in agg["Paid"]],
        textposition="inside", textfont=dict(size=11, color="white"),
    ))
    fig.add_trace(go.Bar(
        x=agg[group_col], y=agg["Outstanding"], name="Outstanding",
        marker_color=OUTSTANDING_COLOR, marker_line=dict(width=0),
        text=[fmt(v, currency) for v in agg["Outstanding"]],
        textposition="inside", textfont=dict(size=11, color="white"),
    ))
    for x_val, total in zip(agg[group_col], totals):
        if pd.isna(x_val) or pd.isna(total):
            continue
        fig.add_annotation(
            x=x_val, y=total,
            text=f"<b>{fmt(total, currency)}</b>",
            showarrow=False, yshift=20,
            font=dict(size=12, color="#37474F"),
            align="center",
        )
    _base_layout(fig, height)
    fig.update_layout(title=title, barmode="stack", margin=dict(t=65))
    return fig

def premium_chart_compare(merged, group_col, title, currency, cmp_label="", height=420):
    """Grouped bar chart: Current vs Comparison period, with Target line."""
    title = str(title) if title else ""
    cmp_label = str(cmp_label) if cmp_label else "Comparison"
    merged = merged.dropna(subset=[group_col]).copy()
    if merged.empty:
        return empty_state(title)

    for c in ["Paid", "Outstanding", "Paid_cmp", "Outstanding_cmp"]:
        if c in merged.columns:
            merged[c] = merged[c].fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged[group_col], y=merged["Paid"], name="Paid (Current)",
        marker_color=PAID_COLOR, marker_line=dict(width=0),
        text=[fmt(v, currency) for v in merged["Paid"]],
        textposition="inside", textfont=dict(size=10, color="white"),
    ))
    fig.add_trace(go.Bar(
        x=merged[group_col], y=merged["Outstanding"], name="Outstanding (Current)",
        marker_color=OUTSTANDING_COLOR, marker_line=dict(width=0),
        text=[fmt(v, currency) for v in merged["Outstanding"]],
        textposition="inside", textfont=dict(size=10, color="white"),
    ))
    fig.add_trace(go.Bar(
        x=merged[group_col], y=merged["Paid_cmp"], name=f"Paid ({cmp_label})",
        marker_color="rgba(79, 195, 247, 0.35)", marker_line=dict(width=1, color=PAID_COLOR),
        text=[fmt(v, currency) for v in merged["Paid_cmp"]],
        textposition="inside", textfont=dict(size=10, color="#37474F"),
    ))
    fig.add_trace(go.Bar(
        x=merged[group_col], y=merged["Outstanding_cmp"], name=f"Outstanding ({cmp_label})",
        marker_color="rgba(206, 147, 216, 0.35)", marker_line=dict(width=1, color=OUTSTANDING_COLOR),
        text=[fmt(v, currency) for v in merged["Outstanding_cmp"]],
        textposition="inside", textfont=dict(size=10, color="#37474F"),
    ))
    _base_layout(fig, height)
    fig.update_layout(barmode="group", margin=dict(t=50))
    return fig

def bar_chart_compare(merged, group_col, y_curr, y_cmp, title, currency, cmp_label="", height=420):
    """Simple grouped bar: current vs comparison for a single metric."""
    title = str(title) if title else ""
    cmp_label = str(cmp_label) if cmp_label else "Comparison"
    merged = merged.dropna(subset=[group_col]).copy()
    if merged.empty:
        return empty_state(title)
    merged[y_curr] = merged[y_curr].fillna(0)
    merged[y_cmp] = merged[y_cmp].fillna(0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged[group_col], y=merged[y_curr], name="Current",
        marker_color=PAID_COLOR,
        text=[fmt(v, currency) for v in merged[y_curr]],
        textposition="outside", textfont=dict(size=11),
    ))
    fig.add_trace(go.Bar(
        x=merged[group_col], y=merged[y_cmp], name=cmp_label,
        marker_color="rgba(79, 195, 247, 0.35)", marker_line=dict(width=1, color=PAID_COLOR),
        text=[fmt(v, currency) for v in merged[y_cmp]],
        textposition="outside", textfont=dict(size=11),
    ))
    _base_layout(fig, height)
    fig.update_layout(barmode="group", margin=dict(t=50))
    return fig


def render_metrics(df_curr, df_cmp, cur, cmp_label=""):
    """Render metric cards. If comparison data exists, show deltas."""
    cmp_label = str(cmp_label) if cmp_label else "Comparison"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Contracts", f"{len(df_curr):,}")
    c2.metric("Total Premium", fmt(convert(df_curr['Annual Premium'].sum(), cur), cur))
    c3.metric("Paid", fmt(convert(df_curr['Paid'].sum(), cur), cur))
    c4.metric("Outstanding", fmt(convert(df_curr['Outstanding'].sum(), cur), cur))
    if df_cmp is not None and len(df_cmp) > 0:
        curr_total = df_curr['Annual Premium'].sum()
        cmp_total = df_cmp['Annual Premium'].sum()
        if cmp_total > 0:
            pct = ((curr_total - cmp_total) / cmp_total) * 100
            arrow = "🟢" if pct >= 0 else "🔴"
            st.caption(f"{arrow} Premium vs {cmp_label}: **{pct:+.1f}%** | Contracts: {len(df_cmp):,} | Premium: {fmt(convert(cmp_total, cur), cur)}")

# ─────────────────────────────────────────────
# PAGE 1: OVERALL PRODUCT (WORLD)
# ─────────────────────────────────────────────
if page == "🌍 Executive Summary":
    st.title("🌍 Executive Summary — Worldwide")

    render_metrics(df_filtered, cmp_filtered, cur, cmp_label)
    st.markdown("---")

    # 1. Contracts by Product
    pc = df_filtered.groupby("Product Label")["Contract ID"].count().reset_index()
    pc.columns = ["Product", "Contracts"]
    st.plotly_chart(bar_chart(pc, "Product", "Contracts", "Contracts by Product", color_map=PRODUCT_COLORS), use_container_width=True)

    # 2. Revenue by Product
    rev = df_filtered.groupby("Product Label")["Annual Premium"].sum().reset_index()
    rev.columns = ["Product", "Premium"]
    rev["Premium"] = rev["Premium"].apply(lambda v: convert(v, cur))
    st.plotly_chart(bar_chart(rev, "Product", "Premium", f"Revenue by Product ({cur})", color_map=PRODUCT_COLORS), use_container_width=True)

    # 3. Revenue Breakdown by Product
    st.markdown("---")
    agg = make_summary(df_filtered, "Product Label")
    agg.rename(columns={"Product Label": "Product"}, inplace=True)
    agg = convert_cols(agg, ["Paid", "Outstanding", "Target"], cur)
    st.plotly_chart(premium_chart(agg, "Product", f"Pending Receivables by Product ({cur})", cur), use_container_width=True)

    # 4. Monthly revenue (with contract count)
    st.markdown("---")
    monthly_agg = df_filtered.groupby("YearMonth").agg(
        Premium=("Annual Premium", "sum"), Contracts=("Contract ID", "count"),
    ).reset_index().sort_values("YearMonth")
    monthly_agg["Premium"] = monthly_agg["Premium"].apply(lambda v: convert(v, cur))
    monthly_agg["Month"] = monthly_agg["YearMonth"].apply(lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%b %Y"))
    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(
        x=monthly_agg["Month"], y=monthly_agg["Premium"], name="Revenue",
        marker_color=PAID_COLOR,
        hovertemplate="%{x}<br>Revenue: %{y:,.2f}<extra></extra>",
    ))
    for xm, ym, cm in zip(monthly_agg["Month"], monthly_agg["Premium"], monthly_agg["Contracts"]):
        fig_m.add_annotation(
            x=xm, y=ym,
            text=f"<b>{_fmt_val(ym)}</b><br>{cm:,} contracts",
            showarrow=False, yshift=15,
            font=dict(size=10, color="#37474F"),
            align="center",
        )
    _base_layout(fig_m, 400)
    fig_m.update_layout(title=f"Monthly Revenue ({cur})", xaxis=dict(gridcolor=GRID_COLOR, tickangle=-45), margin=dict(t=50, b=70, l=60, r=30))
    st.plotly_chart(fig_m, use_container_width=True)

    # 5. Monthly revenue by product — clean line chart with distinct colours
    st.markdown("---")
    mp = df_filtered.groupby(["YearMonth", "Product Label"]).agg(
        Premium=("Annual Premium", "sum"), Target=("Target", "sum"),
        Contracts=("Contract ID", "count"),
    ).reset_index().sort_values("YearMonth")
    mp["Premium"] = mp["Premium"].apply(lambda v: convert(v, cur))
    mp["Month"] = mp["YearMonth"].apply(lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%b %Y"))
    mp.rename(columns={"Product Label": "Product"}, inplace=True)

    fig_mp = go.Figure()
    for prod_name in mp["Product"].unique():
        pp = mp[mp["Product"] == prod_name].sort_values("YearMonth")
        color = PRODUCT_COLORS.get(prod_name, PRODUCT_DEFAULT_COLOR)
        fig_mp.add_trace(go.Scatter(
            x=pp["Month"], y=pp["Premium"], name=prod_name,
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=7, color=color, line=dict(width=1, color="white")),
            hovertemplate=(
                f"<b>{prod_name}</b><br>"
                "Month: %{x}<br>"
                "Revenue: %{y:,.2f}<br>"
                "Contracts: %{customdata[0]:,}"
                "<extra></extra>"
            ),
            customdata=pp[["Contracts"]].values,
        ))
    _base_layout(fig_mp, 400)
    fig_mp.update_layout(
        title=f"Monthly Revenue by Product ({cur})",
        xaxis=dict(gridcolor=GRID_COLOR, tickangle=-45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_mp, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 2: REGION DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🗺️ Region Drill Down":
    st.title("🗺️ Region Drill Down")
    region_sel = st.selectbox("Select Region", REGIONS)
    rdf = df_filtered[df_filtered["Region"] == region_sel]
    r_cmp = cmp_filtered[cmp_filtered["Region"] == region_sel] if cmp_filtered is not None else None

    render_metrics(rdf, r_cmp, cur, cmp_label)
    st.markdown("---")

    # 1. Contracts by Product (with revenue hover)
    rp = rdf.groupby("Product Label").agg(
        Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
    ).reset_index()
    rp.columns = ["Product", "Contracts", "Revenue"]
    rp["Revenue"] = rp["Revenue"].apply(lambda v: convert(v, cur))
    fig_c = bar_chart(rp[["Product", "Contracts"]], "Product", "Contracts", f"Contracts — {region_sel}", color_map=PRODUCT_COLORS)
    fig_c.update_traces(
        hovertemplate="<b>%{x}</b><br>Contracts: %{y:,}<br>Revenue: %{customdata}<extra></extra>",
        customdata=[fmt(v, cur) for v in rp["Revenue"]],
    )
    st.plotly_chart(fig_c, use_container_width=True)

    # 2. Revenue Breakdown (Product)
    if r_cmp is not None and len(r_cmp) > 0:
        merged = make_compare_summary(rdf, r_cmp, "Product Label")
        merged.rename(columns={"Product Label": "Product"}, inplace=True)
        merged = convert_cols(merged, ["Paid", "Outstanding", "Target", "Paid_cmp", "Outstanding_cmp", "Target_cmp"], cur)
        st.plotly_chart(premium_chart_compare(merged, "Product", f"Revenue Breakdown (Product) — {cur} vs {cmp_label}", cur, cmp_label), use_container_width=True)
    else:
        agg = make_summary(rdf, "Product Label")
        agg.rename(columns={"Product Label": "Product"}, inplace=True)
        agg = convert_cols(agg, ["Paid", "Outstanding", "Target"], cur)
        st.plotly_chart(premium_chart(agg, "Product", f"Revenue Breakdown (Product) — {cur}", cur), use_container_width=True)

    # 3. Revenue Breakdown (Country)
    if r_cmp is not None and len(r_cmp) > 0:
        merged_c = make_compare_summary(rdf, r_cmp, "Country")
        merged_c = convert_cols(merged_c, ["Paid", "Outstanding", "Target", "Paid_cmp", "Outstanding_cmp", "Target_cmp"], cur)
        st.plotly_chart(premium_chart_compare(merged_c, "Country", f"Revenue Breakdown (Country) — {cur} vs {cmp_label}", cur, cmp_label), use_container_width=True)
    else:
        rc = rdf.groupby("Country").agg(
            Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"), Target=("Target", "sum"),
        ).reset_index()
        rc = convert_cols(rc, ["Paid", "Outstanding", "Target"], cur)
        st.plotly_chart(premium_chart(rc, "Country", f"Revenue Breakdown (Country) — {cur}", cur), use_container_width=True)

    # 4. Contracts by Country & Product
    cp = rdf.groupby(["Country", "Product Label"]).agg(
        Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
    ).reset_index()
    cp.columns = ["Country", "Product", "Contracts", "Revenue"]
    cp["Revenue"] = cp["Revenue"].apply(lambda v: convert(v, cur))
    fig_cp = bar_chart(cp[["Country", "Product", "Contracts"]], "Country", "Contracts", f"Contracts by Country & Product", color="Product", color_map=PRODUCT_COLORS)
    for trace in fig_cp.data:
        mask = cp["Product"] == trace.name
        trace.customdata = [[fmt(v, cur)] for v in cp[mask]["Revenue"]]
        trace.hovertemplate = "<b>%{x} — " + trace.name + "</b><br>Contracts: %{y:,}<br>Revenue: %{customdata[0]}<extra></extra>"
    st.plotly_chart(fig_cp, use_container_width=True)

    # Drill-down button: navigate to Country Drill Down with region's countries
    region_countries = [c for c, r in COUNTRIES.items() if r == region_sel]
    if st.button(f"🏳️ Drill into {region_sel} Countries ({', '.join(region_countries)})", key="drill_region"):
        st.session_state["country_select"] = region_countries
        st.session_state["nav_page"] = "🏳️ Country Drill Down"
        st.rerun()

# ─────────────────────────────────────────────
# PAGE 3: COUNTRY DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🏳️ Country Drill Down":
    st.title("🏳️ Country Drill Down")
    # Use session state for pre-selected countries (from region drill-down)
    default_countries = st.session_state.pop("country_select", list(COUNTRIES.keys()))
    countries_sel = st.multiselect("Select Countries", list(COUNTRIES.keys()), default=default_countries)
    if not countries_sel:
        countries_sel = list(COUNTRIES.keys())
    cdf = df_filtered[df_filtered["Country"].isin(countries_sel)]
    sel_label = ", ".join(countries_sel) if len(countries_sel) <= 3 else f"{len(countries_sel)} countries"

    cc_cmp = cmp_filtered[cmp_filtered["Country"].isin(countries_sel)] if cmp_filtered is not None else None
    render_metrics(cdf, cc_cmp, cur, cmp_label)
    st.markdown("---")

    # 1. Contracts by Country (product as color)
    cp = cdf.groupby(["Country", "Product Label"]).agg(
        Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
    ).reset_index()
    cp.rename(columns={"Product Label": "Product"}, inplace=True)
    cp["Revenue"] = cp["Revenue"].apply(lambda v: convert(v, cur))
    fig_cp = go.Figure()
    for prod_name in cp["Product"].unique():
        pdata = cp[cp["Product"] == prod_name]
        bar_colors = [get_product_country_color(prod_name, c) for c in pdata["Country"]]
        fig_cp.add_trace(go.Bar(
            x=pdata["Country"], y=pdata["Contracts"], name=prod_name,
            marker_color=bar_colors,
            text=[f"{int(c):,}" for c in pdata["Contracts"]],
            textposition="outside", textfont=dict(size=10),
            customdata=[[fmt(v, cur)] for v in pdata["Revenue"]],
            hovertemplate=f"<b>%{{x}} — {prod_name}</b><br>Contracts: %{{y:,}}<br>Revenue: %{{customdata[0]}}<extra></extra>",
        ))
    _base_layout(fig_cp, 400)
    fig_cp.update_layout(
        title=f"Contracts by Country — {sel_label}",
        barmode="group",
        xaxis=dict(gridcolor=GRID_COLOR),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_cp, use_container_width=True)

    # 2. Revenue by Country (paid + outstanding stacked, product as color)
    rev = cdf.groupby(["Country", "Product Label"]).agg(
        Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"),
    ).reset_index()
    rev.rename(columns={"Product Label": "Product"}, inplace=True)
    rev = convert_cols(rev, ["Paid", "Outstanding"], cur)
    fig_rev = go.Figure()
    for prod_name in rev["Product"].unique():
        pdata = rev[rev["Product"] == prod_name]
        fig_rev.add_trace(go.Bar(
            x=pdata["Country"], y=pdata["Paid"], name=f"Paid — {prod_name}",
            marker_color=PAID_COLOR,
            text=[fmt(v, cur) for v in pdata["Paid"]],
            textposition="outside", textfont=dict(size=10),
            hovertemplate=f"<b>%{{x}} — {prod_name}</b><br>Paid: %{{y}}<extra></extra>",
        ))
        fig_rev.add_trace(go.Bar(
            x=pdata["Country"], y=pdata["Outstanding"], name=f"Pending — {prod_name}",
            marker_color=OUTSTANDING_COLOR,
            text=[fmt(v, cur) for v in pdata["Outstanding"]],
            textposition="outside", textfont=dict(size=10),
            hovertemplate=f"<b>%{{x}} — {prod_name}</b><br>Pending: %{{y}}<extra></extra>",
        ))
    _base_layout(fig_rev, 400)
    fig_rev.update_layout(
        title=f"Revenue by Country — {sel_label} ({cur})",
        barmode="group",
        xaxis=dict(gridcolor=GRID_COLOR),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    # 3. Top Clients
    cl = cdf.groupby(["Country", "Client"]).agg(
        Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
    ).reset_index()
    cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
    cl = cl.sort_values("Revenue", ascending=False).head(15)
    fig_cl = go.Figure()
    for country in cl["Country"].unique():
        cdata = cl[cl["Country"] == country]
        fig_cl.add_trace(go.Bar(
            y=cdata["Client"], x=cdata["Revenue"], name=country,
            orientation="h",
            text=[fmt(v, cur) for v in cdata["Revenue"]],
            textposition="outside", textfont=dict(size=10),
            customdata=cdata[["Contracts"]].values,
            hovertemplate=f"<b>%{{y}} — {country}</b><br>Revenue: %{{x}}<br>Contracts: %{{customdata[0]:,}}<extra></extra>",
        ))
    _base_layout(fig_cl, max(400, len(cl) * 30))
    fig_cl.update_layout(
        title=f"Top Clients — {sel_label} ({cur})",
        barmode="group",
        xaxis=dict(gridcolor=GRID_COLOR),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_cl, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 4: PRODUCT DRILL DOWN
# ─────────────────────────────────────────────
elif page == "📦 Product Drill Down":
    st.title("📦 Product Drill Down")
    prod_sel = st.selectbox("Select Product", list(PRODUCTS.keys()))
    pdf = df_filtered[df_filtered["Product"] == prod_sel]

    if pdf.empty:
        st.warning(f"No data for {prod_sel} in selected period.")
    else:
        st.subheader(f"{PRODUCTS[prod_sel]['label']}")
        render_metrics(pdf, cmp_filtered[cmp_filtered["Product"] == prod_sel] if cmp_filtered is not None else None, cur, cmp_label)
        st.markdown("---")

        # 1. Revenue by Country (hover shows contract count)
        cp = pdf.groupby("Country").agg(
            Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
        ).reset_index()
        cp["Revenue"] = cp["Revenue"].apply(lambda v: convert(v, cur))
        fig_cp = go.Figure()
        bar_colors = [get_product_country_color(prod_sel, c) for c in cp["Country"]]
        fig_cp.add_trace(go.Bar(
            y=cp["Country"], x=cp["Revenue"], name=f"Revenue ({cur})",
            orientation="h", marker_color=bar_colors,
            text=[fmt(v, cur) for v in cp["Revenue"]],
            textposition="outside", textfont=dict(size=11),
            customdata=cp[["Contracts"]].values,
            hovertemplate="<b>%{y}</b><br>Revenue: %{x}<br>Contracts: %{customdata[0]:,}<extra></extra>",
        ))
        _base_layout(fig_cp, max(300, len(cp) * 80))
        fig_cp.update_layout(
            title=f"Revenue by Country — {prod_sel}",
            xaxis=dict(gridcolor=GRID_COLOR),
            showlegend=False,
        )
        st.plotly_chart(fig_cp, use_container_width=True)

        # 2. Plan breakdown — skip for EV (single plan)
        if prod_sel != "EV / Auto":
            plan_data = pdf.groupby(["Plan", "Country"]).agg(
                Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"),
            ).reset_index()
            plan_data = convert_cols(plan_data, ["Paid", "Outstanding"], cur)
            if not plan_data.empty:
                fig_plan = go.Figure()
                for country in plan_data["Country"].unique():
                    cdata = plan_data[plan_data["Country"] == country]
                    fig_plan.add_trace(go.Bar(
                        y=cdata["Plan"], x=cdata["Paid"], name=f"Paid — {country}",
                        orientation="h", marker_color=PAID_COLOR,
                        text=[fmt(v, cur) for v in cdata["Paid"]],
                        textposition="outside", textfont=dict(size=10),
                        hovertemplate=f"<b>%{{y}} — {country}</b><br>Paid: %{{x}}<extra></extra>",
                    ))
                    fig_plan.add_trace(go.Bar(
                        y=cdata["Plan"], x=cdata["Outstanding"], name=f"Pending — {country}",
                        orientation="h", marker_color=OUTSTANDING_COLOR,
                        text=[fmt(v, cur) for v in cdata["Outstanding"]],
                        textposition="outside", textfont=dict(size=10),
                        hovertemplate=f"<b>%{{y}} — {country}</b><br>Pending: %{{x}}<extra></extra>",
                    ))
                _base_layout(fig_plan, max(300, len(plan_data["Plan"].unique()) * 100))
                fig_plan.update_layout(
                    title=f"Plan Breakdown — {prod_sel} ({cur})",
                    barmode="group",
                    xaxis=dict(gridcolor=GRID_COLOR),
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig_plan, use_container_width=True)

        # 3. Top Clients (horizontal bar)
        st.markdown("---")
        cl = pdf.groupby(["Country", "Client"]).agg(
            Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
        ).reset_index()
        cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
        cl = cl.sort_values("Revenue", ascending=False).head(15)
        prod_color = PRODUCT_COLORS.get(prod_sel, PRODUCT_DEFAULT_COLOR)
        fig_cl = go.Figure()
        for country in cl["Country"].unique():
            cdata = cl[cl["Country"] == country]
            fig_cl.add_trace(go.Bar(
                y=cdata["Client"], x=cdata["Revenue"], name=country,
                orientation="h", marker_color=prod_color,
                text=[fmt(v, cur) for v in cdata["Revenue"]],
                textposition="outside", textfont=dict(size=10),
                customdata=cdata[["Contracts"]].values,
                hovertemplate=f"<b>%{{y}} — {country}</b><br>Revenue: %{{x}}<br>Contracts: %{{customdata[0]:,}}<extra></extra>",
            ))
        _base_layout(fig_cl, max(400, len(cl) * 30))
        fig_cl.update_layout(
            title=f"Top Clients — {prod_sel} ({cur})",
            barmode="group",
            xaxis=dict(gridcolor=GRID_COLOR),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_cl, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 5: EV WARRANTY ANALYSIS
# ─────────────────────────────────────────────
elif page == "🚗 EV Warranty Analysis":
    st.title("🚗 EV Warranty Analysis")
    ev = df_filtered[df_filtered["Product"] == "EV / Auto"].copy()
    if ev.empty:
        st.warning("No EV data in selected period.")
    else:
        ev_tab1, ev_tab2, ev_tab3, ev_tab4, ev_tab5 = st.tabs([
            "🩺 State of Health", "📅 By Age", "🛣️ By KM", "🔄 Health vs KM", "🔄 Health vs Age"])

        with ev_tab1:
            st.subheader("EV — State of Health")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_health_c")
            hdf = ev[ev["Country"].isin(h_country)]

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies", f"{len(hdf):,}")
            col2.metric("Healthy", f"{len(hdf[hdf['Health State']=='Healthy']):,}")
            col3.metric("Poor", f"{len(hdf[hdf['Health State']=='Poor']):,}")
            st.markdown("---")

            hc = hdf.groupby("Health State").agg(
                Policies=("Contract ID", "count"), Avg_Premium=("Annual Premium", "mean"),
                Claims=("Claims", "sum"), Claim_Amount=("Claim Amount", "sum"),
            ).reset_index()
            hc["Avg_Premium"] = hc["Avg_Premium"].apply(lambda v: convert(v, cur))
            hc["Claim_Amount"] = hc["Claim_Amount"].apply(lambda v: convert(v, cur))

            fig1 = bar_chart(hc.rename(columns={"Health State": "Health", "Policies": "Count"}),
                             "Health", "Count", "Policies by Health State")
            st.plotly_chart(fig1, use_container_width=True)

            hcc = hdf.groupby(["Health State", "Country"])["Contract ID"].count().reset_index()
            hcc.columns = ["Health State", "Country", "Policies"]
            st.plotly_chart(bar_chart(hcc, "Health State", "Policies", "Health State by Country", color="Country"), use_container_width=True)

            fig2 = bar_chart(hc.rename(columns={"Health State": "Health", "Avg_Premium": f"Avg Premium ({cur})"}),
                             "Health", f"Avg Premium ({cur})", f"Avg Premium by Health ({cur})")
            st.plotly_chart(fig2, use_container_width=True)

        with ev_tab2:
            st.subheader("EV — Vehicle Age")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_age_c")
            adf = ev[ev["Country"].isin(h_country)].copy()
            adf["Age Bracket"] = pd.cut(adf["Vehicle Age"], bins=[0, 3, 5, 10, 15],
                                         labels=["1-3 yrs", "4-5 yrs", "6-10 yrs", "11-15 yrs"])

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies", f"{len(adf):,}")
            col2.metric("Avg Age", f"{adf['Vehicle Age'].mean():.1f} yrs")
            col3.metric("Avg KM", f"{adf['KM Driven'].mean():,.0f}")
            st.markdown("---")

            ac = adf.groupby("Age Bracket", observed=True)["Contract ID"].count().reset_index()
            ac.columns = ["Age Bracket", "Policies"]
            st.plotly_chart(bar_chart(ac, "Age Bracket", "Policies", "Policies by Vehicle Age"), use_container_width=True)

            acc = adf.groupby(["Age Bracket", "Country"], observed=True)["Contract ID"].count().reset_index()
            acc.columns = ["Age Bracket", "Country", "Policies"]
            st.plotly_chart(bar_chart(acc, "Age Bracket", "Policies", "Vehicle Age by Country", color="Country"), use_container_width=True)

        with ev_tab3:
            st.subheader("EV — KM Driven")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_km_c")
            kdf = ev[ev["Country"].isin(h_country)].copy()
            kdf["KM Bracket"] = pd.cut(kdf["KM Driven"], bins=[0, 25000, 50000, 100000, 150000, 250000],
                                        labels=["0-25K", "25-50K", "50-100K", "100-150K", "150K+"])

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies", f"{len(kdf):,}")
            col2.metric("Avg KM", f"{kdf['KM Driven'].mean():,.0f}")
            col3.metric("Max KM", f"{kdf['KM Driven'].max():,.0f}")
            st.markdown("---")

            kc = kdf.groupby("KM Bracket", observed=True)["Contract ID"].count().reset_index()
            kc.columns = ["KM Bracket", "Policies"]
            st.plotly_chart(bar_chart(kc, "KM Bracket", "Policies", "Policies by KM Driven"), use_container_width=True)

            kcc = kdf.groupby(["KM Bracket", "Country"], observed=True)["Contract ID"].count().reset_index()
            kcc.columns = ["KM Bracket", "Country", "Policies"]
            st.plotly_chart(bar_chart(kcc, "KM Bracket", "Policies", "KM by Country", color="Country"), use_container_width=True)

        with ev_tab4:
            st.subheader("EV — Health State vs KM Driven")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_hkm_c")
            hmdf = ev[ev["Country"].isin(h_country)].copy()
            hmdf["KM Bracket"] = pd.cut(hmdf["KM Driven"], bins=[0, 25000, 50000, 100000, 150000, 250000],
                                          labels=["0-25K", "25-50K", "50-100K", "100-150K", "150K+"])

            hkh = hmdf.groupby(["KM Bracket", "Health State"], observed=True)["Contract ID"].count().reset_index()
            hkh.columns = ["KM Bracket", "Health State", "Policies"]
            st.plotly_chart(bar_chart(hkh, "KM Bracket", "Policies", "Health State by KM Driven", color="Health State"), use_container_width=True)

            pivot = hmdf.groupby(["KM Bracket", "Health State"], observed=True)["Contract ID"].count().reset_index()
            pivot.columns = ["KM", "Health", "Count"]
            piv = pivot.pivot(index="Health", columns="KM", values="Count").fillna(0)
            fig_hm = px.imshow(piv, text_auto=True, color_continuous_scale=[[0, "#E3F2FD"], [0.5, "#4FC3F7"], [1, "#01579B"]],
                               title="Heatmap: Health State vs KM")
            fig_hm.update_layout(height=400)
            st.plotly_chart(fig_hm, use_container_width=True)

        with ev_tab5:
            st.subheader("EV — Health State vs Vehicle Age")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_hage_c")
            hadf = ev[ev["Country"].isin(h_country)].copy()
            hadf["Age Bracket"] = pd.cut(hadf["Vehicle Age"], bins=[0, 3, 5, 10, 15],
                                          labels=["1-3 yrs", "4-5 yrs", "6-10 yrs", "11-15 yrs"])

            hah = hadf.groupby(["Age Bracket", "Health State"], observed=True)["Contract ID"].count().reset_index()
            hah.columns = ["Age Bracket", "Health State", "Policies"]
            st.plotly_chart(bar_chart(hah, "Age Bracket", "Policies", "Health State by Vehicle Age", color="Health State"), use_container_width=True)

            pivot2 = hadf.groupby(["Age Bracket", "Health State"], observed=True)["Contract ID"].count().reset_index()
            pivot2.columns = ["Age", "Health", "Count"]
            piv2 = pivot2.pivot(index="Health", columns="Age", values="Count").fillna(0)
            fig_hm2 = px.imshow(piv2, text_auto=True, color_continuous_scale=[[0, "#F3E5F5"], [0.5, "#CE93D8"], [1, "#4A148C"]],
                                title="Heatmap: Health State vs Vehicle Age")
            fig_hm2.update_layout(height=400)
            st.plotly_chart(fig_hm2, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 6: IPI POLICY ANALYSIS
# ─────────────────────────────────────────────
elif page == "🛡️ IPI Policy Analysis":
    st.title("🛡️ IPI Policy Analysis")
    ipi = df_filtered[df_filtered["Product"] == "Income Protection"].copy()
    if ipi.empty:
        st.warning("No IPI data in selected period.")
    else:
        ipi_tab1, ipi_tab2, ipi_tab3 = st.tabs([
            "📋 Sum Insured by Plan", "🔄 Renewal Rate", "👥 Lives Insured"])

        with ipi_tab1:
            st.subheader("IPI — Sum Insured by Plan Type")
            i_country = st.multiselect("Country", ["India", "Singapore", "Thailand"],
                                        default=["India", "Singapore", "Thailand"], key="ipisi_c")
            sidf = ipi[ipi["Country"].isin(i_country)]

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies", f"{len(sidf):,}")
            col2.metric("Total Sum Insured", fmt(convert(sidf["Sum Insured"].sum(), cur), cur))
            col3.metric("Avg Sum Insured", fmt(convert(sidf["Sum Insured"].mean(), cur), cur))
            st.markdown("---")

            si = sidf.groupby("Plan").agg(
                Policies=("Contract ID", "count"),
                Total_SI=("Sum Insured", "sum"),
                Avg_SI=("Sum Insured", "mean"),
            ).reset_index().sort_values("Total_SI", ascending=False)
            si["Total_SI"] = si["Total_SI"].apply(lambda v: convert(v, cur))
            si["Avg_SI"] = si["Avg_SI"].apply(lambda v: convert(v, cur))
            st.plotly_chart(bar_chart(si, "Plan", "Total_SI", f"Total Sum Insured by Plan ({cur})"), use_container_width=True)

            ti = sidf.groupby("Type").agg(
                Policies=("Contract ID", "count"),
                Total_SI=("Sum Insured", "sum"),
                Avg_SI=("Sum Insured", "mean"),
            ).reset_index()
            ti["Total_SI"] = ti["Total_SI"].apply(lambda v: convert(v, cur))
            ti["Avg_SI"] = ti["Avg_SI"].apply(lambda v: convert(v, cur))
            st.plotly_chart(bar_chart(ti, "Type", "Total_SI", f"Sum Insured by Type ({cur})"), use_container_width=True)

            sic = sidf.groupby(["Plan", "Country"])["Sum Insured"].sum().reset_index()
            sic["Sum Insured"] = sic["Sum Insured"].apply(lambda v: convert(v, cur))
            st.plotly_chart(bar_chart(sic, "Plan", "Sum Insured", f"Sum Insured by Plan & Country ({cur})", color="Country"), use_container_width=True)

        with ipi_tab2:
            st.subheader("IPI — Renewal Rate")
            i_country = st.multiselect("Country", ["India", "Singapore", "Thailand"],
                                        default=["India", "Singapore", "Thailand"], key="ipirr_c")
            rrf = ipi[ipi["Country"].isin(i_country)]

            col1, col2, col3 = st.columns(3)
            overall_rate = rrf["Renewed"].mean() * 100
            col1.metric("Renewal Rate", f"{overall_rate:.1f}%")
            col2.metric("Renewed", f"{rrf['Renewed'].sum():,}")
            col3.metric("Not Renewed", f"{(~rrf['Renewed']).sum():,}")
            st.markdown("---")

            rr = rrf.groupby("Plan")["Renewed"].mean().reset_index()
            rr["Renewal %"] = rr["Renewed"] * 100
            st.plotly_chart(bar_chart(rr, "Plan", "Renewal %", "Renewal Rate by Plan"), use_container_width=True)

            rt = rrf.groupby("Type")["Renewed"].mean().reset_index()
            rt["Renewal %"] = rt["Renewed"] * 100
            st.plotly_chart(bar_chart(rt, "Type", "Renewal %", "Renewal Rate by Type"), use_container_width=True)

            rc = rrf.groupby("Country")["Renewed"].mean().reset_index()
            rc["Renewal %"] = rc["Renewed"] * 100
            st.plotly_chart(bar_chart(rc, "Country", "Renewal %", "Renewal Rate by Country"), use_container_width=True)

            rpc = rrf.groupby(["Plan", "Country"])["Renewed"].mean().reset_index()
            rpc["Renewal %"] = rpc["Renewed"] * 100
            st.plotly_chart(bar_chart(rpc, "Plan", "Renewal %", "Renewal Rate by Plan & Country", color="Country"), use_container_width=True)

        with ipi_tab3:
            st.subheader("IPI — Lives Insured")
            i_country = st.multiselect("Country", ["India", "Singapore", "Thailand"],
                                        default=["India", "Singapore", "Thailand"], key="ipili_c")
            lif = ipi[ipi["Country"].isin(i_country)]

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies", f"{len(lif):,}")
            col2.metric("Total Lives", f"{lif['Lives Insured'].sum():,}")
            col3.metric("Avg Lives/Policy", f"{lif['Lives Insured'].mean():.0f}")
            st.markdown("---")

            ll = lif.groupby("Plan")["Lives Insured"].sum().reset_index().sort_values("Lives Insured", ascending=False)
            st.plotly_chart(bar_chart(ll, "Plan", "Lives Insured", "Lives Insured by Plan"), use_container_width=True)

            lt = lif.groupby("Type")["Lives Insured"].agg(["sum", "mean"]).reset_index()
            lt.columns = ["Type", "Total", "Avg"]
            lt_m = lt.melt(id_vars="Type", var_name="Metric", value_name="Value")
            st.plotly_chart(bar_chart(lt_m, "Type", "Value", "Lives Insured by Type", color="Metric"), use_container_width=True)

            lc = lif.groupby("Country")["Lives Insured"].sum().reset_index()
            st.plotly_chart(bar_chart(lc, "Country", "Lives Insured", "Lives Insured by Country"), use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 7: RAW DATA
# ─────────────────────────────────────────────
elif page == "📋 Raw Data":
    st.title("📋 Contract Data")
    col1, col2, col3 = st.columns(3)
    f_product = col1.multiselect("Product", df_filtered["Product"].unique(), default=df_filtered["Product"].unique())
    f_country = col2.multiselect("Country", df_filtered["Country"].unique(), default=df_filtered["Country"].unique())
    f_type = col3.multiselect("Type", df_filtered["Type"].unique(), default=df_filtered["Type"].unique())

    filtered = df_filtered[(df_filtered["Product"].isin(f_product)) & (df_filtered["Country"].isin(f_country)) & (df_filtered["Type"].isin(f_type))]
    st.dataframe(filtered, use_container_width=True, height=600)
    st.caption(f"Showing {len(filtered):,} of {len(df_filtered):,} contracts")
    st.download_button("📥 Download CSV", filtered.to_csv(index=False), "contracts.csv", "text/csv")
