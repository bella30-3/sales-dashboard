import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import numpy as np
from currency import convert, fmt, currency_selector, SYMBOLS

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide", initial_sidebar_state="expanded", page_icon="🌊")

# ─────────────────────────────────────────────
# THEMES
# ─────────────────────────────────────────────
THEMES = {
    "Dark Blue": {
        "accent": "#3360F0",
        "paid": "#3360F0",
        "outstanding": "#E04050",
        "target": "#60B0A0",
        "bg": "#0E1117",
        "card_bg": "#1A1F2E",
        "card_border": "#2A3040",
        "grid": "rgba(255,255,255,0.06)",
        "text_primary": "#E8ECF1",
        "text_secondary": "#8899AA",
        "chart_text": "#8899AA",
        "gauge_green": "#00D68F",
        "gauge_amber": "#FFB020",
        "gauge_red": "#FF4D4F",
        "product_colors": {
            "Income Protection": "#3360F0",
            "Automotive": "#60B0A0",
            "Care - Aqua": "#F0B020",
        },
        "country_colors": {
            "Singapore": "#E04050",
            "Thailand": "#3050F0",
            "India": "#F0B020",
            "Europe": "#60B0A0",
        },
    },
    "Sea Green": {
        "accent": "#006D6D",
        "paid": "#006D6D",
        "outstanding": "#D94F4F",
        "target": "#4CAF80",
        "bg": "#006D6D",
        "card_bg": "#FFFFFF",
        "card_border": "#006D6D",
        "grid": "rgba(0,109,109,0.10)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#C0E0E0",
        "chart_text": "#333333",
        "gauge_green": "#006D6D",
        "gauge_amber": "#E6A800",
        "gauge_red": "#D94F4F",
        "product_colors": {
            "Income Protection": "#006D6D",
            "Automotive": "#4CAF80",
            "Care - Aqua": "#E6A800",
        },
        "country_colors": {
            "Singapore": "#D94F4F",
            "Thailand": "#009999",
            "India": "#E6A800",
            "Europe": "#4CAF80",
        },
    },
}

# Commission rate (15% of annual premium)
COMMISSION_RATE = 0.15


def true_premium_sum(df):
    """Sum annual premium once per contract — avoids 12x inflation on monthly billing rows."""
    return df.groupby("Contract ID")["Annual Premium"].first().sum()

# ─────────────────────────────────────────────
# THEME SELECTION (before CSS)
# ─────────────────────────────────────────────
_theme_sel = st.sidebar.selectbox("🎨 Theme", list(THEMES.keys()), key="theme_sel")
T = THEMES[_theme_sel]
ACCENT = T["accent"]
PAID_COLOR = T["paid"]
OUTSTANDING_COLOR = T["outstanding"]
TARGET_COLOR = T["target"]
BG_COLOR = T["bg"]
CARD_BG = T["card_bg"]
CARD_BORDER = T["card_border"]
SIDEBAR_BG = T["bg"]
TEXT_PRIMARY = T["text_primary"]
TEXT_SECONDARY = T["text_secondary"]
GRID_COLOR = T["grid"]
HEADING_COLOR = T["text_primary"]
CHART_BG = T["card_bg"]
PRODUCT_COLORS = T["product_colors"]
PRODUCT_DEFAULT_COLOR = ACCENT
COUNTRY_COLORS = T["country_colors"]
COUNTRY_DEFAULT_COLOR = ACCENT
GAUGE_GREEN = T["gauge_green"]
GAUGE_AMBER = T["gauge_amber"]
GAUGE_RED = T["gauge_red"]
CHART_TEXT = T.get("chart_text", TEXT_SECONDARY)

# Build CSS with theme colors
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Dark app background */
.stApp {{
    font-family: 'Inter', sans-serif;
    background: {BG_COLOR};
    color: {TEXT_PRIMARY};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {BG_COLOR};
    border-right: 1px solid {CARD_BORDER};
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {{
    color: {TEXT_SECONDARY} !important;
}}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {{
    color: {TEXT_PRIMARY} !important;
    background-color: {CARD_BG} !important;
}}
section[data-testid="stSidebar"] .stDateInput label {{
    color: {TEXT_PRIMARY} !important;
    font-weight: 500 !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="input"] > div {{
    background-color: {CARD_BG} !important;
    border-color: {CARD_BORDER} !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="popover"] {{
    background-color: {CARD_BG} !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="calendar"] {{
    background-color: {CARD_BG} !important;
}}

/* Headings */
h1, h2, h3, h4 {{
    color: {TEXT_PRIMARY} !important;
    font-weight: 700 !important;
}}
h1 {{ font-size: 1.5rem !important; }}
h2 {{ font-size: 1.25rem !important; }}
h3 {{ font-size: 1.1rem !important; }}

/* General text */
p, li, span, label, .stMarkdown {{
    color: {TEXT_SECONDARY};
}}

/* Metric cards — dark glass look */
.stMetric > div {{
    background: {CARD_BG};
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid {CARD_BORDER};
}}
.stMetric label {{
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: {TEXT_SECONDARY} !important;
}}
.stMetric [data-testid="stMetricValue"] {{
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: {TEXT_PRIMARY} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    padding: 4px;
    background: {CARD_BG};
    border-radius: 10px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 500;
    color: {TEXT_SECONDARY};
}}
.stTabs [aria-selected="true"] {{
    background: {ACCENT};
    color: #FFFFFF !important;
    font-weight: 700;
}}

/* Plotly charts — dark card with border & shadow */
.stPlotlyChart {{
    border-radius: 12px;
    background: {CHART_BG};
    padding: 6px;
    border: 1px solid {CARD_BORDER};
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), 0 1px 4px rgba(0, 0, 0, 0.2);
}}

/* Dataframes */
div[data-testid="stDataFrame"] {{
    border-radius: 10px;
    overflow: hidden;
}}

/* Selectbox / multiselect dropdowns */
div[data-baseweb="select"] > div {{
    background: {CHART_BG};
    border-color: {CARD_BORDER};
    color: {TEXT_PRIMARY};
}}

/* Date input */
div[data-testid="stDateInput"] input {{
    color: {TEXT_PRIMARY};
}}

/* Horizontal rule */
hr {{
    border-color: {CARD_BORDER} !important;
}}

/* Caption / small text */
.stMarkdown small, .stCaption, figcaption {{
    color: {TEXT_SECONDARY} !important;
}}

/* Force all Plotly chart titles to be light */
g.g-gtitle .gtitle-text,
.g-gtitle text,
g.infolayer .g-gtitle text {{
    fill: {CHART_TEXT} !important;
}}

/* Date picker calendar popup */
div[data-baseweb="datepicker"] {{
    background: {CHART_BG} !important;
    color: {TEXT_PRIMARY} !important;
}}
div[data-baseweb="datepicker"] td,
div[data-baseweb="datepicker"] th {{
    color: {TEXT_PRIMARY} !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA DEFINITIONS
# ─────────────────────────────────────────────
PRODUCTS = {
    "EV / Auto": {
        "label": "Automotive",
        "desc": "Service Contracts & Warranties",
        "plans": {
            "India": ["EV Warranty"],
            "Singapore": ["EV Warranty"],
            "Thailand": ["EV Warranty"],
        },
    },
    "Income Protection": {
        "label": "Income Protection",
        "desc": "Contracts & Premiums",
        "plans": {
            "India": ["RQBE (All)"],
            "Singapore": ["DBS Staff 2000", "DBS Staff 5000", "OCBC GA 12M A", "OCBC GA 12M B", "OCBC GA 12M C", "OCBC GA 12M D"],
        },
        "premiums": {
            "DBS Staff 2000": 500, "DBS Staff 5000": 800,
            "OCBC GA 12M A": 100, "OCBC GA 12M B": 150,
            "OCBC GA 12M C": 200, "OCBC GA 12M D": 200,
            "RQBE (All)": 350,
        },
        "types": {
            "DBS Staff 2000": "Individual", "DBS Staff 5000": "Individual",
            "OCBC GA 12M A": "Corporate", "OCBC GA 12M B": "Corporate",
            "OCBC GA 12M C": "Corporate", "OCBC GA 12M D": "Corporate",
            "RQBE (All)": "Individual",
        },
    },
    "Care Aqua": {
        "label": "Care - Aqua",
        "desc": "Warranty Contracts & Amounts",
        "plans": {
            "India": ["Pure", "Fresh", "Pro"],
            "Singapore": ["Pure", "Fresh", "Pro"],
            "Thailand": ["Pure", "Fresh", "Pro"],
            "Europe": ["Pure", "Fresh", "Pro"],
        },
    },
}

COUNTRIES = {"Thailand": "Asia", "India": "Asia", "Singapore": "Asia", "Europe": "Europe"}
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

CLIENT_LAUNCH_DATES = {
    "EV / Auto": {
        "Thailand": {
            "BYD": datetime(2024, 7, 1), "Porsche": datetime(2025, 1, 1),
            "Subaru": datetime(2026, 1, 1),
            "Hyundai": datetime(2099, 1, 1), "BYD Forklift": datetime(2099, 1, 1),
        },
        "Singapore": {
            "BYD": datetime(2024, 7, 1), "Porsche": datetime(2025, 1, 1),
            "Cycle and Carriage": datetime(2024, 7, 1),
        },
    },
}

def get_plan_premium(prod, plan):
    return PRODUCTS.get(prod, {}).get("premiums", {}).get(plan)

def get_plan_type(prod, plan):
    return PRODUCTS.get(prod, {}).get("types", {}).get(plan)

def get_client(product, country, current_date=None):
    clients = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {}).get(country, [])
    if not clients:
        all_pc = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {})
        clients = [c for cs in all_pc.values() for c in cs]
    if current_date and product in CLIENT_LAUNCH_DATES and country in CLIENT_LAUNCH_DATES[product]:
        launch_dates = CLIENT_LAUNCH_DATES[product][country]
        clients = [c for c in clients if c not in launch_dates or current_date >= launch_dates[c]]
    if not clients:
        return "Unknown"
    if product == "EV / Auto":
        ev_weights = {
            ("Singapore", "BYD"): 55, ("Singapore", "Porsche"): 30,
            ("Singapore", "Cycle and Carriage"): 15,
            ("Thailand", "BYD"): 30, ("Thailand", "Porsche"): 5,
            ("Thailand", "Subaru"): 3, ("Thailand", "Hyundai"): 1,
            ("Thailand", "BYD Forklift"): 1,
            ("India", "Mahindra Trucks and Buses (MTB)"): 1,
        }
        weights = [ev_weights.get((country, c), 1) for c in clients]
        return random.choices(clients, weights=weights, k=1)[0]
    if product == "Income Protection":
        ipi_weights = {
            ("Singapore", "OCBC (GE)"): 65, ("Singapore", "DBS (ECICS)"): 35,
            ("India", "Raheja (RQBE)"): 20, ("Thailand", "Muang Thai"): 15,
        }
        weights = [ipi_weights.get((country, c), 1) for c in clients]
        return random.choices(clients, weights=weights, k=1)[0]
    return random.choice(clients)

PRODUCT_LAUNCH = {
    "Income Protection": datetime(2023, 7, 1),
    "EV / Auto": datetime(2024, 1, 1),
    "Care Aqua": datetime(2026, 1, 1),
}

POLICY_PREMIUM_RANGE_SGD = {
    "Income Protection": (100, 450),
    "EV / Auto": (250, 450),
    "Care Aqua": (1800, 2200),
}

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
EV_MODELS = {
    "Porsche": ["Taycan", "Macan", "Cayenne"],
    "BYD": ["Atto 3", "Seal", "Dolphin", "Tang"],
    "Subaru": ["Solterra", "Evoltis"],
    "Hyundai": ["Ioniq 5", "Ioniq 6", "Kona Electric"],
    "Mahindra": ["eVerito", "XEV 9e", "BE 6"],
    "Cycle & Carriage": ["Multi-Brand"],
}

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
    r = random.random()
    if r < 0.05:
        return max(3, int(target_n * random.uniform(0.7, 0.85)))
    elif r < 0.25:
        return max(5, int(target_n * random.uniform(0.85, 0.95)))
    elif r < 0.75:
        return int(target_n * random.uniform(0.95, 1.05))
    elif r < 0.95:
        return int(target_n * random.uniform(1.05, 1.15))
    else:
        return int(target_n * random.uniform(1.15, 1.3))


def generate_data():
    rows = []
    end_date = datetime.now()
    current = datetime(2023, 7, 1)

    while current <= end_date:
        year, month = current.year, current.month
        days_in_month = 28 if month == 2 else (30 if month in (4, 6, 9, 11) else 31)

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
                continue

            months_since_launch = (current.year - launch.year) * 12 + (current.month - launch.month)
            ramp = min(1.0, 0.4 + 0.6 * (months_since_launch / 6))

            target_n = MONTHLY_POLICY_COUNTS[prod]
            for sched_start, sched_end, sched_n in RATE_SCHEDULE.get(prod, []):
                if sched_start <= current <= sched_end:
                    target_n = sched_n
                    break
            premium_lo, premium_hi = POLICY_PREMIUM_RANGE_SGD[prod]

            n_policies = max(3, int(_random_n_contracts(target_n, prod) * seasonal * ramp))

            for i in range(n_policies):
                premium_sgd = random.uniform(premium_lo, premium_hi)
                premium = round(premium_sgd / SGD_TO_USD)

                if prod == "Care Aqua":
                    country = "Europe"
                elif prod == "EV / Auto":
                    country = random.choices(["Singapore", "Thailand", "India"], weights=[60, 32, 8])[0]
                elif prod == "Income Protection":
                    country = random.choices(["Singapore", "India", "Thailand"], weights=[70, 18, 12])[0]
                else:
                    country = random.choice([c for c in COUNTRIES.keys() if c != "Europe"])
                region = COUNTRIES[country]

                plan = random.choice(PRODUCTS[prod]["plans"].get(country, PRODUCTS[prod]["plans"][list(PRODUCTS[prod]["plans"].keys())[0]]))
                plan_type = get_plan_type(prod, plan)
                ctype = plan_type if plan_type else random.choice(TYPES)
                client = get_client(prod, country, current)

                if prod == "Income Protection":
                    if client == "DBS (ECICS)":
                        premium_sgd = random.uniform(500, 800)
                    elif client == "OCBC (GE)":
                        premium_sgd = random.uniform(80, 200)
                    premium = round(premium_sgd / SGD_TO_USD)

                trantype = random.choice(TRAN_TYPES)
                paid_pct = random.uniform(0.3, 1.0)
                paid = round(premium * paid_pct)
                outstanding = premium - paid
                inst_count = random.randint(1, 12) if trantype == "Inst" else 1

                start_day = random.randint(1, min(days_in_month, 28))
                start = datetime(year, month, start_day)
                end = start + timedelta(days=365)
                target = round(premium * random.uniform(0.85, 1.15))

                row = {
                    "Contract ID": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(10000, 99999)}",
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

                if prod == "EV / Auto":
                    brand = random.choice(EV_BRANDS)
                    model = random.choice(EV_MODELS.get(brand, ["Unknown"]))
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
                        "Health State": health, "Brand": brand, "Model": model,
                        "Vehicle Age": age, "KM Driven": km,
                        "Claims": claim_count, "Claim Amount": claim_amount,
                    })

                if prod == "Income Protection":
                    plan_info = IPI_PLANS.get(plan, {})
                    ipi_type = plan_info.get("type", ctype)
                    insurer = plan_info.get("insurer", "Unknown")
                    sum_insured = plan_info.get("sum_insured", random.randint(2000, 200000))
                    renewed = random.random() < (0.85 if ipi_type == "Corporate" else 0.65)
                    lives = random.randint(1, 3) if ipi_type == "Corporate" else 1
                    row.update({
                        "Insurer": insurer, "Sum Insured": sum_insured,
                        "Renewed": renewed, "Lives Insured": lives,
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

cur = currency_selector("Display Currency", "app_currency")

st.sidebar.markdown("### 📅 Date Range")
date_min = pd.to_datetime(df["Start Date"]).min().date()
date_max = pd.to_datetime(df["Start Date"]).max().date()
current_year_start = datetime(datetime.now().year, 1, 1).date()
default_start = max(current_year_start, date_min)
date_range = st.sidebar.date_input(
    "Select period",
    value=(default_start, date_max),
    min_value=date_min, max_value=date_max,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = date_range
else:
    d_start, d_end = date_min, date_max

df_filtered = df[(pd.to_datetime(df["Start Date"]).dt.date >= d_start) &
                 (pd.to_datetime(df["Start Date"]).dt.date <= d_end)]

st.sidebar.markdown("---")
st.sidebar.caption(f"Period: **{d_start}** → **{d_end}**")

PAGES = [
    "🌍 Executive Summary",
    "🗺️ Region Drill Down",
    "🏳️ Country Drill Down",
    "📦 Product Drill Down",
    "🚗 EV Warranty Analysis",
    "🛡️ IPI Policy Analysis",
    "📋 Raw Data",
]
nav = st.session_state.pop("nav_page", None)
nav_idx = PAGES.index(nav) if nav in PAGES else 0
page = st.sidebar.radio("Navigate", PAGES, index=nav_idx)

st.sidebar.markdown("---")
st.sidebar.caption(f"Policies Sold: **{len(df_filtered):,}**")
st.sidebar.caption(f"Premium: **{fmt(convert(true_premium_sum(df_filtered), cur), cur)}**")

# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
PALETTE = [ACCENT]


def _base_layout(fig, height=420):
    fig.update_layout(
        height=height,
        title_font_size=16,
        title_font_color=CHART_TEXT,
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(family="Inter, sans-serif", color=CHART_TEXT, size=13),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, color=CHART_TEXT),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, color=CHART_TEXT),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(color=CHART_TEXT)),
        margin=dict(t=60, b=50, l=60, r=30),
    )
    return fig


def empty_state(title="No data available"):
    fig = go.Figure()
    fig.update_layout(
        title=title, height=300,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        annotations=[dict(
            text="No data for selected filters",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color=CHART_TEXT),
        )],
    )
    return fig


def _fmt_val(v):
    if pd.isna(v) or (isinstance(v, float) and np.isinf(v)):
        return "—"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"{v / 1_000:.2f}k"
    else:
        return f"{v:,.2f}"

def fmt2(amount: float, currency: str = "USD") -> str:
    """Format amount with currency symbol, always 2 decimals."""
    symbol = SYMBOLS.get(currency, currency + " ")
    if abs(amount) >= 1_000_000:
        return f"{symbol}{amount / 1_000_000:,.2f}M"
    elif abs(amount) >= 1_000:
        return f"{symbol}{amount / 1_000:,.2f}k"
    else:
        return f"{symbol}{amount:,.2f}"


def bar_chart(data, x, y, title, color=None, barmode="group", height=420, color_map=None):
    title = str(title) if title else ""
    data = data.dropna(subset=[x]).copy()
    data[y] = data[y].fillna(0)
    if data.empty:
        return empty_state(title)
    if color_map:
        fig = px.bar(data, x=x, y=y, color=color, title=title, barmode=barmode, color_discrete_map=color_map)
    else:
        fig = px.bar(data, x=x, y=y, color=color, title=title, barmode=barmode, color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="outside", textfont_size=13)
    for trace in fig.data:
        trace.text = [_fmt_val(v) for v in trace.y]
    _base_layout(fig, height)
    return fig


def make_summary(df_in, group_col):
    """Aggregate by group_col. Premium is deduplicated per contract first."""
    base = df_in.groupby(group_col).agg(
        Contracts=("Contract ID", "count"),
        Paid=("Paid", "sum"),
        Outstanding=("Outstanding", "sum"),
        Target=("Target", "sum"),
    ).reset_index()
    premium = (df_in.drop_duplicates("Contract ID")
               .groupby(group_col)["Annual Premium"].sum()
               .reset_index())
    premium.rename(columns={"Annual Premium": "Total_Premium"}, inplace=True)
    return base.merge(premium, on=group_col, how="left").fillna({"Total_Premium": 0})


def convert_cols(agg, cols, currency):
    for c in cols:
        agg[c] = agg[c].apply(lambda v: convert(v, currency))
    return agg


def premium_chart(agg, group_col, title, currency, height=420):
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
            font=dict(size=12, color=CHART_TEXT), align="center",
        )
    _base_layout(fig, height)
    fig.update_layout(title=title, barmode="stack", margin=dict(t=65))
    return fig


# ─────────────────────────────────────────────
# SEMICIRCLE GAUGE HELPER
# ─────────────────────────────────────────────
def make_gauge(value, title, max_val=100, suffix="%"):
    """Return a Plotly semicircle gauge figure for dark background."""
    v = min(value, max_val)
    if v >= 70:
        bar_color = GAUGE_GREEN
    elif v >= 40:
        bar_color = GAUGE_AMBER
    else:
        bar_color = GAUGE_RED

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=v,
        number={"suffix": suffix, "font": {"size": 28, "color": CHART_TEXT, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": TEXT_SECONDARY,
                     "tickfont": {"size": 11, "color": TEXT_SECONDARY}},
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": CARD_BG,
            "borderwidth": 0,
            "steps": [
                {"range": [0, max_val * 0.4], "color": "rgba(255,77,79,0.15)"},
                {"range": [max_val * 0.4, max_val * 0.7], "color": "rgba(255,176,32,0.15)"},
                {"range": [max_val * 0.7, max_val], "color": "rgba(0,214,143,0.15)"},
            ],
            "shape": "angular",
        },
        title={"text": title, "font": {"size": 14, "color": "#8899AA", "family": "Inter"}},
    ))
    fig.update_layout(
        height=220,
        margin=dict(t=60, b=10, l=30, r=30),
        paper_bgcolor=CHART_BG,
        font=dict(family="Inter, sans-serif"),
    )
    return fig

def make_nested_donut(actuals_by_month, budget_by_month, proj_by_month, currency):
    """Nested donut chart: inner=Actuals, middle=Budget, outer=Projection, each by month."""
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Green shades (inner ring — Actuals)
    green_colors = ["#0B3D2E", "#0F5132", "#137A4A", "#1A9E5F",
                    "#22B86E", "#2ED88A", "#5CE8A2", "#8CF0BE",
                    "#B0F5D4", "#D0FAE8", "#E8FDF2", "#F0FEF6"]
    # Blue shades (middle ring — Budget)
    blue_colors = ["#0D1F4A", "#122D66", "#1A3F88", "#2255AA",
                   "#2B6ACC", "#3360F0", "#5580F4", "#77A0F6",
                   "#99BDF9", "#BBC8FB", "#DDE5FD", "#EEF2FE"]
    # Amber shades (outer ring — Projection)
    amber_colors = ["#4A3000", "#6B4500", "#8C5A00", "#AD7000",
                    "#CC8800", "#E69E00", "#F0B020", "#F4C040",
                    "#F7D060", "#FADE80", "#FCEAA0", "#FDF4C0"]

    current_month = datetime.now().month  # 1-indexed
    active_months = month_labels[:current_month]

    fig = go.Figure()

    # Outer ring — Projection
    proj_vals = [proj_by_month.get(i + 1, 0) for i in range(current_month)]
    fig.add_trace(go.Pie(
        values=proj_vals,
        labels=active_months,
        domain=dict(x=[0.12, 0.88], y=[0.05, 0.95]),
        hole=0.72,
        marker=dict(colors=amber_colors[:current_month], line=dict(color=CHART_BG, width=2)),
        textinfo="none",
        hovertemplate="<b>Projection — %{label}</b><br>%{value:,.0f}<extra></extra>",
        sort=False,
        name="Projection",
    ))

    # Middle ring — Budget
    bud_vals = [budget_by_month.get(i + 1, 0) for i in range(current_month)]
    fig.add_trace(go.Pie(
        values=bud_vals,
        labels=active_months,
        domain=dict(x=[0.18, 0.82], y=[0.10, 0.90]),
        hole=0.68,
        marker=dict(colors=blue_colors[:current_month], line=dict(color=CHART_BG, width=2)),
        textinfo="none",
        hovertemplate="<b>Budget — %{label}</b><br>%{value:,.0f}<extra></extra>",
        sort=False,
        name="Budget",
    ))

    # Inner ring — Actuals
    act_vals = [actuals_by_month.get(i + 1, 0) for i in range(current_month)]
    fig.add_trace(go.Pie(
        values=act_vals,
        labels=active_months,
        domain=dict(x=[0.24, 0.76], y=[0.15, 0.85]),
        hole=0.60,
        marker=dict(colors=green_colors[:current_month], line=dict(color=CHART_BG, width=2)),
        textinfo="none",
        hovertemplate="<b>Actuals — %{label}</b><br>%{value:,.0f}<extra></extra>",
        sort=False,
        name="Actuals",
    ))

    # Center label
    total_actuals = sum(act_vals)
    fig.add_annotation(
        text=f"<b>{fmt(convert(total_actuals, currency), currency)}</b><br><span style='font-size:10px;color:{TEXT_SECONDARY}'>Actuals YTD</span>",
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(size=16, color=TEXT_PRIMARY, family="Inter"),
    )

    fig.update_layout(
        height=320,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter, sans-serif", color=TEXT_SECONDARY),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="top", y=-0.02,
            xanchor="center", x=0.5,
            font=dict(size=11, color=CHART_TEXT),
            itemsizing="constant",
        ),

    )
    return fig


# ─────────────────────────────────────────────
# METRIC HELPERS
# ─────────────────────────────────────────────
def compute_kpis(df_curr, currency):
    """Compute all KPI values for the executive summary."""
    today = pd.Timestamp(datetime.now().date())
    n_policies = len(df_curr)

    # Active %: policies whose End Date >= today
    end_dates = pd.to_datetime(df_curr["End Date"], errors="coerce")
    active_mask = end_dates >= today
    active_pct = (active_mask.sum() / n_policies * 100) if n_policies > 0 else 0

    # Renewal %: policies with Renewed == True (IPI only); others treated as not renewed
    if "Renewed" in df_curr.columns:
        renewed_mask = df_curr["Renewed"].fillna(False).astype(bool)
        renewal_pct = (renewed_mask.sum() / n_policies * 100) if n_policies > 0 else 0
    else:
        renewal_pct = 0

    # Lapse %: policies expired AND not renewed
    expired_mask = end_dates < today
    if "Renewed" in df_curr.columns:
        not_renewed_mask = ~df_curr["Renewed"].fillna(False).astype(bool)
        lapsed_mask = expired_mask & not_renewed_mask
    else:
        lapsed_mask = expired_mask
    lapse_pct = (lapsed_mask.sum() / n_policies * 100) if n_policies > 0 else 0

    # Deduplicated per-contract premiums for accurate totals
    unique_contracts = df_curr.drop_duplicates("Contract ID")
    n_unique = len(unique_contracts)

    # Average premium in USD (per contract, not per installment row)
    avg_premium = unique_contracts["Annual Premium"].mean() if n_unique > 0 else 0

    # Commission (per contract)
    total_commission = unique_contracts["Annual Premium"].sum() * COMMISSION_RATE
    avg_commission = (unique_contracts["Annual Premium"] * COMMISSION_RATE).mean() if n_unique > 0 else 0

    # Total premium (per contract)
    total_premium = unique_contracts["Annual Premium"].sum()

    return {
        "n_policies": n_policies,
        "total_premium": total_premium,
        "active_pct": active_pct,
        "renewal_pct": renewal_pct,
        "lapse_pct": lapse_pct,
        "avg_premium": avg_premium,
        "avg_commission": avg_commission,
        "total_commission": total_commission,
    }


def _kpi_card(label, value, delta=None, positive=True):
    """HTML metric card with value colored green/red based on delta direction."""
    color = GAUGE_GREEN if positive else GAUGE_RED
    arrow = "▲" if positive else "▼"
    delta_html = ""
    if delta is not None:
        delta_html = f'<div style="font-size:0.78rem;color:{color};margin-top:4px">{arrow} {delta}</div>'
    return f"""
    <div style="background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:10px;padding:16px 20px;text-align:center">
      <div style="font-size:0.85rem;color:{CHART_TEXT};font-weight:600">{label}</div>
      <div style="font-size:1.35rem;font-weight:700;color:{color};margin-top:6px">{value}</div>
      {delta_html}
    </div>
    """

def _kpi_card_neutral(label, value):
    """HTML metric card with neutral color (no delta)."""
    return f"""
    <div style="background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:10px;padding:16px 20px;text-align:center">
      <div style="font-size:0.85rem;color:{CHART_TEXT};font-weight:600">{label}</div>
      <div style="font-size:1.35rem;font-weight:700;color:{CHART_TEXT};margin-top:6px">{value}</div>
    </div>
    """

def render_metrics(currency):
    """Render KPI metrics: delta cards in first 2 cols, neutral in remaining."""
    kpis = compute_kpis(df_filtered, currency)

    # Last year comparison — same date range shifted back 1 year
    ly_start = d_start.replace(year=d_start.year - 1)
    ly_end = d_end.replace(year=d_end.year - 1)
    df_ly = df[(pd.to_datetime(df["Start Date"]).dt.date >= ly_start) &
               (pd.to_datetime(df["Start Date"]).dt.date <= ly_end)]
    kpis_ly = compute_kpis(df_ly, currency)

    def _pct_delta(curr, prev):
        if prev == 0:
            return None, True
        pct = ((curr - prev) / prev) * 100
        return f"{pct:+.1f}%", pct >= 0

    def _pp_delta(curr, prev):
        diff = curr - prev
        return f"{diff:+.1f}pp", diff >= 0

    # Deltas
    d_policies, pos_policies = _pct_delta(kpis["n_policies"], kpis_ly["n_policies"])
    d_premium, pos_premium = _pct_delta(kpis["total_premium"], kpis_ly["total_premium"])
    d_commission, pos_commission = _pct_delta(kpis["total_commission"], kpis_ly["total_commission"])
    d_renewal, pos_renewal = _pp_delta(kpis["renewal_pct"], kpis_ly["renewal_pct"])

    # Row 1: Delta metrics in first 2 columns (wider cards)
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    with c1:
        st.markdown(_kpi_card("📋 Policies Sold (YTD)", f"{kpis['n_policies']:,}", d_policies, pos_policies), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card("💰 Total Premium", fmt(convert(kpis["total_premium"], currency), currency), d_premium, pos_premium), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_card_neutral("📊 Avg Premium", fmt2(convert(kpis["avg_premium"], currency), currency)), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi_card_neutral("📈 Avg Commission", fmt2(convert(kpis["avg_commission"], currency), currency)), unsafe_allow_html=True)

    # Row 2: Delta metrics in first 2 columns
    c5, c6, c7, c8 = st.columns([2, 2, 1, 1])
    with c5:
        st.markdown(_kpi_card("💵 Total Commission", fmt(convert(kpis["total_commission"], currency), currency), d_commission, pos_commission), unsafe_allow_html=True)
    with c6:
        st.markdown(_kpi_card("🔄 Renewal %", f"{kpis['renewal_pct']:.1f}%", d_renewal, pos_renewal), unsafe_allow_html=True)
    with c7:
        st.markdown(_kpi_card_neutral("✅ Active %", f"{kpis['active_pct']:.1f}%"), unsafe_allow_html=True)
    with c8:
        st.markdown(_kpi_card_neutral("⚠️ Lapse Rate", f"{kpis['lapse_pct']:.1f}%"), unsafe_allow_html=True)


def render_gauge_row(currency):
    """Render nested donut (Actuals vs Budget vs Projection by month) + Renewal & Lapse meters."""
    kpis = compute_kpis(df_filtered, currency)

    # Monthly actuals from filtered data
    monthly_actuals = (df_filtered.drop_duplicates("Contract ID")
                        .groupby("Month")["Annual Premium"].sum().to_dict())
    current_month = datetime.now().month

    # Generate budget (~10% above) and projection (~20% above) with some tight months
    budget_monthly = {}
    proj_monthly = {}
    for m in range(1, current_month + 1):
        a = monthly_actuals.get(m, 0)
        if m in (3, 7, 11):  # tight months
            budget_monthly[m] = a * random.uniform(0.98, 1.05)
            proj_monthly[m] = a * random.uniform(1.00, 1.08)
        else:
            budget_monthly[m] = a * random.uniform(1.06, 1.14)
            proj_monthly[m] = a * random.uniform(1.15, 1.25)

    g1, g2, g3 = st.columns(3)
    with g1:
        fig_donut = make_nested_donut(monthly_actuals, budget_monthly, proj_monthly, currency)
        st.plotly_chart(fig_donut, use_container_width=True)
    with g2:
        fig_renewal = make_gauge(kpis["renewal_pct"], "Renewal %")
        st.plotly_chart(fig_renewal, use_container_width=True)
    with g3:
        fig_lapse = make_gauge(kpis["lapse_pct"], "Lapse Rate %")
        st.plotly_chart(fig_lapse, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 1: EXECUTIVE SUMMARY
# ─────────────────────────────────────────────
if page == "🌍 Executive Summary":
    st.title("🌍 Executive Summary")

    # KPI metrics
    render_metrics(cur)
    st.markdown("---")

    # Gauge meters
    st.subheader("📊 Key Health Indicators")
    render_gauge_row(cur)
    st.markdown("---")

    # Charts in 3-column layout
    # Row 1: Pie chart (policies by product) | Revenue by product | Pending receivables
    st.subheader("📋 Policy & Revenue Breakdown")
    c1, c2, c3 = st.columns(3)

    with c1:
        # PIE chart — Policies Sold by Product
        pc = df_filtered.groupby("Product Label")["Contract ID"].count().reset_index()
        pc.columns = ["Product", "Policies Sold"]
        if not pc.empty:
            pie_colors = [PRODUCT_COLORS.get(p, PRODUCT_DEFAULT_COLOR) for p in pc["Product"]]
            fig_pie = go.Figure(go.Pie(
                labels=pc["Product"], values=pc["Policies Sold"],
                marker=dict(colors=pie_colors, line=dict(color=BG_COLOR, width=2)),
                textinfo="label+percent",
                textfont=dict(size=12, color=TEXT_PRIMARY),
                hole=0.35,
            ))
            fig_pie.update_layout(
                title="Policies Sold by Product",
                height=420,
                paper_bgcolor=CHART_BG,
                plot_bgcolor=CHART_BG,
                font=dict(family="Inter, sans-serif", color=TEXT_SECONDARY),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                            font=dict(color=TEXT_SECONDARY)),
                margin=dict(t=60, b=60, l=30, r=30),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.plotly_chart(empty_state("Policies Sold by Product"), use_container_width=True)

    with c2:
        # Revenue by Product (deduplicated per contract)
        rev = (df_filtered.drop_duplicates("Contract ID")
               .groupby("Product Label")["Annual Premium"].sum().reset_index())
        rev.columns = ["Product", "Premium"]
        rev["Premium"] = rev["Premium"].apply(lambda v: convert(v, cur))
        fig_rev = bar_chart(rev, "Product", "Premium", f"Revenue by Product ({cur})", color_map=PRODUCT_COLORS)
        st.plotly_chart(fig_rev, use_container_width=True)

    with c3:
        # Pending Receivables
        agg = make_summary(df_filtered, "Product Label")
        agg.rename(columns={"Product Label": "Product"}, inplace=True)
        agg = convert_cols(agg, ["Paid", "Outstanding", "Target"], cur)
        fig_agg = premium_chart(agg, "Product", f"Pending Receivables ({cur})", cur)
        st.plotly_chart(fig_agg, use_container_width=True)

    st.markdown("---")

    # Row 2: Monthly revenue | Monthly by product | (empty or additional)
    st.subheader("📈 Monthly Trends")
    c4, c5, c6 = st.columns(3)

    with c4:
        # Monthly revenue
        ma = df_filtered.groupby("YearMonth").agg(
            Contracts=("Contract ID", "count"),
        ).reset_index()
        ma_premium = (df_filtered.drop_duplicates("Contract ID")
                      .groupby("YearMonth")["Annual Premium"].sum()
                      .reset_index().rename(columns={"Annual Premium": "Premium"}))
        ma = ma.merge(ma_premium, on="YearMonth", how="left").fillna({"Premium": 0})
        ma = ma.sort_values("YearMonth")
        ma["Premium"] = ma["Premium"].apply(lambda v: convert(v, cur))
        ma["Month"] = ma["YearMonth"].apply(lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%b %Y"))

        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(
            x=ma["Month"], y=ma["Premium"], name="Revenue",
            marker_color=PAID_COLOR,
            customdata=ma[["Contracts"]].values,
            hovertemplate="%{x}<br>Revenue: %{y:,.2f}<br>Policies: %{customdata[0]:,}<extra></extra>",
        ))
        _base_layout(fig_m, 420)
        fig_m.update_layout(title=f"Monthly Revenue ({cur})", xaxis=dict(tickangle=-45, gridcolor=GRID_COLOR),
                            margin=dict(t=50, b=70))
        st.plotly_chart(fig_m, use_container_width=True)

    with c5:
        # Monthly revenue by product (line)
        mp = df_filtered.groupby(["YearMonth", "Product Label"]).agg(
            Contracts=("Contract ID", "count"),
        ).reset_index()
        mp_premium = (df_filtered.drop_duplicates("Contract ID")
                      .groupby(["YearMonth", "Product Label"])["Annual Premium"].sum()
                      .reset_index().rename(columns={"Annual Premium": "Premium"}))
        mp = mp.merge(mp_premium, on=["YearMonth", "Product Label"], how="left").fillna({"Premium": 0})
        mp = mp.sort_values("YearMonth")
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
                marker=dict(size=6, color=color, line=dict(width=1, color="white")),
                customdata=pp[["Contracts"]].values,
                hovertemplate=(
                    f"<b>{prod_name}</b><br>Month: %{{x}}<br>"
                    f"Revenue: %{{y:,.2f}}<br>Policies: %{{customdata[0]:,}}<extra></extra>"
                ),
            ))
        _base_layout(fig_mp, 420)
        fig_mp.update_layout(
            title=f"Monthly Revenue by Product ({cur})",
            xaxis=dict(tickangle=-45, gridcolor=GRID_COLOR),
            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_mp, use_container_width=True)

    with c6:
        # Policies sold by country (horizontal bar)
        cc = df_filtered.groupby("Country")["Contract ID"].count().reset_index()
        cc.columns = ["Country", "Policies Sold"]
        cc = cc.sort_values("Policies Sold", ascending=True)

        fig_cc = go.Figure(go.Bar(
            y=cc["Country"], x=cc["Policies Sold"], orientation="h",
            marker_color=[COUNTRY_COLORS.get(c, COUNTRY_DEFAULT_COLOR) for c in cc["Country"]],
            text=[f"{int(v):,}" for v in cc["Policies Sold"]],
            textposition="outside", textfont=dict(size=11, color=CHART_TEXT),
            hovertemplate="<b>%{y}</b><br>Policies Sold: %{x:,}<extra></extra>",
        ))
        _base_layout(fig_cc, 420)
        fig_cc.update_layout(title="Policies Sold by Country", showlegend=False,
                             margin=dict(t=50, b=50, l=100))
        st.plotly_chart(fig_cc, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 2: REGION DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🗺️ Region Drill Down":
    st.title("🗺️ Region Drill Down")
    region_sel = st.selectbox("Select Region", REGIONS)
    rdf = df_filtered[df_filtered["Region"] == region_sel]

    st.subheader(f"Region: {region_sel}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Policies Sold", f"{len(rdf):,}")
    rdf_unique = rdf.drop_duplicates("Contract ID")
    c2.metric("💰 Total Premium", fmt(convert(true_premium_sum(rdf), cur), cur))
    c3.metric("📊 Avg Premium", fmt(convert(rdf_unique["Annual Premium"].mean(), cur) if len(rdf_unique) > 0 else 0, cur))
    c4.metric("💵 Total Commission", fmt(convert(true_premium_sum(rdf) * COMMISSION_RATE, cur), cur))
    st.markdown("---")

    # 3-column charts
    c1, c2, c3 = st.columns(3)

    with c1:
        rp = rdf.groupby("Product Label").agg(
            Contracts=("Contract ID", "count"),
        ).reset_index()
        rp.rename(columns={"Product Label": "Product", "Contracts": "Policies Sold"}, inplace=True)
        fig_rc = bar_chart(rp, "Product", "Policies Sold", f"Policies Sold — {region_sel}", color_map=PRODUCT_COLORS)
        st.plotly_chart(fig_rc, use_container_width=True)

    with c2:
        agg = make_summary(rdf, "Product Label")
        agg.rename(columns={"Product Label": "Product"}, inplace=True)
        agg = convert_cols(agg, ["Paid", "Outstanding", "Target"], cur)
        fig_rbp = premium_chart(agg, "Product", f"Receivables — {region_sel} ({cur})", cur)
        st.plotly_chart(fig_rbp, use_container_width=True)

    with c3:
        rc = rdf.groupby("Country").agg(
            Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"), Target=("Target", "sum"),
        ).reset_index()
        rc = convert_cols(rc, ["Paid", "Outstanding", "Target"], cur)
        fig_rbc = premium_chart(rc, "Country", f"Receivables by Country ({cur})", cur)
        st.plotly_chart(fig_rbc, use_container_width=True)

    st.markdown("---")

    # Second row
    c4, c5, c6 = st.columns(3)

    with c4:
        cp = rdf.groupby(["Country", "Product Label"]).agg(
            Contracts=("Contract ID", "count"),
        ).reset_index()
        cp.columns = ["Country", "Product", "Policies Sold"]
        fig_ccp = bar_chart(cp, "Country", "Policies Sold", "Policies by Country & Product",
                            color="Product", color_map=PRODUCT_COLORS)
        st.plotly_chart(fig_ccp, use_container_width=True)

    with c5:
        cl = (rdf.drop_duplicates("Contract ID")
              .groupby(["Country", "Client"])
              .agg(Revenue=("Annual Premium", "sum"))
              .reset_index())
        cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
        cl = cl.sort_values("Revenue", ascending=False).head(10)
        fig_tc = go.Figure()
        for country in cl["Country"].unique():
            cdata = cl[cl["Country"] == country]
            fig_tc.add_trace(go.Bar(
                y=cdata["Client"], x=cdata["Revenue"], name=country, orientation="h",
                marker_color=COUNTRY_COLORS.get(country, COUNTRY_DEFAULT_COLOR),
                text=[fmt(v, cur) for v in cdata["Revenue"]],
                textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
            ))
        _base_layout(fig_tc, max(350, len(cl) * 30))
        fig_tc.update_layout(title=f"Top Clients — {region_sel} ({cur})", barmode="group",
                             margin=dict(t=50, b=50, l=150))
        st.plotly_chart(fig_tc, use_container_width=True)

    with c6:
        # Commission by country (deduplicated per contract)
        comm = (rdf.drop_duplicates("Contract ID")
                .assign(Commission=lambda x: x["Annual Premium"] * COMMISSION_RATE)
                .groupby("Country")["Commission"].sum()
                .reset_index())
        comm["Commission"] = comm["Commission"].apply(lambda v: convert(v, cur))
        fig_comm = bar_chart(comm, "Country", "Commission", f"Commission by Country ({cur})",
                             color_map=COUNTRY_COLORS)
        st.plotly_chart(fig_comm, use_container_width=True)

    # Drill-down button
    region_countries = [c for c, r in COUNTRIES.items() if r == region_sel]
    if st.button(f"🏳️ Drill into {region_sel} Countries ({', '.join(region_countries)})"):
        st.session_state["country_select"] = region_countries
        st.session_state["nav_page"] = "🏳️ Country Drill Down"
        st.rerun()

# ─────────────────────────────────────────────
# PAGE 3: COUNTRY DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🏳️ Country Drill Down":
    st.title("🏳️ Country Drill Down")
    default_countries = st.session_state.pop("country_select", list(COUNTRIES.keys()))
    countries_sel = st.multiselect("Select Countries", list(COUNTRIES.keys()), default=default_countries)
    if not countries_sel:
        countries_sel = list(COUNTRIES.keys())
    cdf = df_filtered[df_filtered["Country"].isin(countries_sel)]
    sel_label = ", ".join(countries_sel) if len(countries_sel) <= 3 else f"{len(countries_sel)} countries"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Policies Sold", f"{len(cdf):,}")
    cdf_unique = cdf.drop_duplicates("Contract ID")
    c2.metric("💰 Total Premium", fmt(convert(true_premium_sum(cdf), cur), cur))
    c3.metric("📊 Avg Premium", fmt(convert(cdf_unique["Annual Premium"].mean(), cur) if len(cdf_unique) > 0 else 0, cur))
    c4.metric("💵 Total Commission", fmt(convert(true_premium_sum(cdf) * COMMISSION_RATE, cur), cur))
    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        cp = cdf.groupby(["Country", "Product Label"]).agg(
            Contracts=("Contract ID", "count"),
        ).reset_index()
        cp.rename(columns={"Product Label": "Product", "Contracts": "Policies Sold"}, inplace=True)
        fig_cc = go.Figure()
        for prod_name in cp["Product"].unique():
            pdata = cp[cp["Product"] == prod_name]
            fig_cc.add_trace(go.Bar(
                x=pdata["Country"], y=pdata["Policies Sold"], name=prod_name,
                marker_color=PRODUCT_COLORS.get(prod_name, PRODUCT_DEFAULT_COLOR),
                text=[f"{int(c):,}" for c in pdata["Policies Sold"]],
                textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
            ))
        _base_layout(fig_cc, 420)
        fig_cc.update_layout(title=f"Policies Sold — {sel_label}", barmode="group",
                             xaxis=dict(gridcolor=GRID_COLOR))
        st.plotly_chart(fig_cc, use_container_width=True)

    with c2:
        rev = cdf.groupby(["Country", "Product Label"]).agg(
            Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"),
        ).reset_index()
        rev.rename(columns={"Product Label": "Product"}, inplace=True)
        rev = convert_cols(rev, ["Paid", "Outstanding"], cur)
        fig_cr = go.Figure()
        for prod_name in rev["Product"].unique():
            pdata = rev[rev["Product"] == prod_name]
            fig_cr.add_trace(go.Bar(x=pdata["Country"], y=pdata["Paid"], name=f"Paid — {prod_name}",
                                    marker_color=PAID_COLOR, text=[fmt(v, cur) for v in pdata["Paid"]],
                                    textposition="outside", textfont=dict(size=10, color=CHART_TEXT)))
            fig_cr.add_trace(go.Bar(x=pdata["Country"], y=pdata["Outstanding"], name=f"Pending — {prod_name}",
                                    marker_color=OUTSTANDING_COLOR,
                                    text=[fmt(v, cur) for v in pdata["Outstanding"]],
                                    textposition="outside", textfont=dict(size=10, color=CHART_TEXT)))
        _base_layout(fig_cr, 420)
        fig_cr.update_layout(title=f"Revenue — {sel_label} ({cur})", barmode="group",
                             xaxis=dict(gridcolor=GRID_COLOR))
        st.plotly_chart(fig_cr, use_container_width=True)

    with c3:
        cl = (cdf.drop_duplicates("Contract ID")
              .groupby(["Country", "Client"])
              .agg(Revenue=("Annual Premium", "sum"))
              .reset_index())
        cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
        cl = cl.sort_values("Revenue", ascending=False).head(15)
        fig_tc = go.Figure()
        for country in cl["Country"].unique():
            cdata = cl[cl["Country"] == country]
            fig_tc.add_trace(go.Bar(
                y=cdata["Client"], x=cdata["Revenue"], name=country, orientation="h",
                marker_color=COUNTRY_COLORS.get(country, COUNTRY_DEFAULT_COLOR),
                text=[fmt(v, cur) for v in cdata["Revenue"]],
                textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
            ))
        _base_layout(fig_tc, max(400, len(cl) * 30))
        fig_tc.update_layout(title=f"Top Clients — {sel_label} ({cur})", barmode="group",
                             margin=dict(t=50, b=50, l=150))
        st.plotly_chart(fig_tc, use_container_width=True)

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
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Policies Sold", f"{len(pdf):,}")
        pdf_unique = pdf.drop_duplicates("Contract ID")
        c2.metric("💰 Total Premium", fmt(convert(true_premium_sum(pdf), cur), cur))
        c3.metric("📊 Avg Premium", fmt(convert(pdf_unique["Annual Premium"].mean(), cur), cur))
        c4.metric("💵 Total Commission", fmt(convert(true_premium_sum(pdf) * COMMISSION_RATE, cur), cur))
        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        with c1:
            cp = pdf.groupby("Country").agg(
                Contracts=("Contract ID", "count"),
            ).reset_index()
            cp_rev = (pdf.drop_duplicates("Contract ID")
                      .groupby("Country")["Annual Premium"].sum()
                      .reset_index().rename(columns={"Annual Premium": "Revenue"}))
            cp = cp.merge(cp_rev, on="Country", how="left").fillna({"Revenue": 0})
            cp["Revenue"] = cp["Revenue"].apply(lambda v: convert(v, cur))
            bar_colors = [COUNTRY_COLORS.get(c, COUNTRY_DEFAULT_COLOR) for c in cp["Country"]]
            fig_prc = go.Figure(go.Bar(
                y=cp["Country"], x=cp["Revenue"], orientation="h",
                marker_color=bar_colors,
                text=[fmt(v, cur) for v in cp["Revenue"]],
                textposition="outside", textfont=dict(size=11, color=CHART_TEXT),
                customdata=cp[["Contracts"]].values,
                hovertemplate="<b>%{y}</b><br>Revenue: %{x}<br>Policies: %{customdata[0]:,}<extra></extra>",
            ))
            _base_layout(fig_prc, max(300, len(cp) * 80))
            fig_prc.update_layout(title=f"Revenue by Country ({cur})", showlegend=False)
            st.plotly_chart(fig_prc, use_container_width=True)

        with c2:
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
                            textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
                        ))
                        fig_plan.add_trace(go.Bar(
                            y=cdata["Plan"], x=cdata["Outstanding"], name=f"Pending — {country}",
                            orientation="h", marker_color=OUTSTANDING_COLOR,
                            text=[fmt(v, cur) for v in cdata["Outstanding"]],
                            textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
                        ))
                    _base_layout(fig_plan, max(300, len(plan_data["Plan"].unique()) * 100))
                    fig_plan.update_layout(
                        title=f"Plan Breakdown ({cur})", barmode="group",
                        xaxis=dict(gridcolor=GRID_COLOR),
                        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                    )
                    st.plotly_chart(fig_plan, use_container_width=True)
            else:
                st.info("Single plan type for EV / Auto")

        with c3:
            cl = pdf.groupby(["Country", "Client"]).agg(
                Contracts=("Contract ID", "count"),
            ).reset_index()
            cl_rev = (pdf.drop_duplicates("Contract ID")
                      .groupby(["Country", "Client"])["Annual Premium"].sum()
                      .reset_index().rename(columns={"Annual Premium": "Revenue"}))
            cl = cl.merge(cl_rev, on=["Country", "Client"], how="left").fillna({"Revenue": 0})
            cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
            cl = cl.sort_values("Revenue", ascending=False).head(10)
            fig_ptc = go.Figure()
            for country in cl["Country"].unique():
                cdata = cl[cl["Country"] == country]
                fig_ptc.add_trace(go.Bar(
                    y=cdata["Client"], x=cdata["Revenue"], name=country, orientation="h",
                    marker_color=COUNTRY_COLORS.get(country, COUNTRY_DEFAULT_COLOR),
                    text=[fmt(v, cur) for v in cdata["Revenue"]],
                    textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
                    customdata=cdata[["Contracts"]].values,
                    hovertemplate=f"<b>%{{y}}</b><br>Revenue: %{{x}}<br>Policies: %{{customdata[0]:,}}<extra></extra>",
                ))
            _base_layout(fig_ptc, max(350, len(cl) * 30))
            fig_ptc.update_layout(title=f"Top Clients ({cur})", barmode="group",
                                  margin=dict(t=50, b=50, l=150))
            st.plotly_chart(fig_ptc, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 5: EV WARRANTY ANALYSIS
# ─────────────────────────────────────────────
elif page == "🚗 EV Warranty Analysis":
    st.title("🚗 EV Warranty Analysis")
    ev = df_filtered[df_filtered["Product"] == "EV / Auto"].copy()
    if ev.empty:
        st.warning("No EV data in selected period.")
    else:
        ev_tab1, ev_tab2, ev_tab3, ev_tab4, ev_tab5, ev_tab6 = st.tabs([
            "🩺 State of Health", "📅 By Age", "🛣️ By KM", "🔄 Health vs KM", "🔄 Health vs Age", "🚗 By Model"])

        with ev_tab1:
            st.subheader("EV — State of Health")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_health_c")
            hdf = ev[ev["Country"].isin(h_country)]

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies", f"{len(hdf):,}")
            col2.metric("Healthy", f"{len(hdf[hdf['Health State'] == 'Healthy']):,}")
            col3.metric("Poor", f"{len(hdf[hdf['Health State'] == 'Poor']):,}")
            st.markdown("---")

            c1, c2, c3 = st.columns(3)
            with c1:
                hc = hdf.groupby("Health State")["Contract ID"].count().reset_index()
                hc.columns = ["Health", "Count"]
                fig1 = bar_chart(hc, "Health", "Count", "Policies by Health State")
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                hcc = hdf.groupby(["Health State", "Country"])["Contract ID"].count().reset_index()
                hcc.columns = ["Health State", "Country", "Policies"]
                fig1b = bar_chart(hcc, "Health State", "Policies", "Health State by Country", color="Country")
                st.plotly_chart(fig1b, use_container_width=True)
            with c3:
                havg = hdf.groupby("Health State")["Annual Premium"].mean().reset_index()
                havg.columns = ["Health", "Avg Premium"]
                havg["Avg Premium"] = havg["Avg Premium"].apply(lambda v: convert(v, cur))
                fig1c = bar_chart(havg, "Health", "Avg Premium", f"Avg Premium by Health ({cur})")
                st.plotly_chart(fig1c, use_container_width=True)

        with ev_tab2:
            st.subheader("EV — Vehicle Age")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_age_c")
            adf = ev[ev["Country"].isin(h_country)].copy()
            adf["Age Bracket"] = pd.cut(adf["Vehicle Age"], bins=[0, 3, 5, 10, 15],
                                        labels=["1-3 yrs", "4-5 yrs", "6-10 yrs", "11-15 yrs"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Policies", f"{len(adf):,}")
            c2.metric("Avg Age", f"{adf['Vehicle Age'].mean():.1f} yrs")
            c3.metric("Avg KM", f"{adf['KM Driven'].mean():,.0f}")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                ac = adf.groupby("Age Bracket", observed=True)["Contract ID"].count().reset_index()
                ac.columns = ["Age Bracket", "Policies"]
                st.plotly_chart(bar_chart(ac, "Age Bracket", "Policies", "Policies by Vehicle Age"),
                                use_container_width=True)
            with col2:
                acc = adf.groupby(["Age Bracket", "Country"], observed=True)["Contract ID"].count().reset_index()
                acc.columns = ["Age Bracket", "Country", "Policies"]
                st.plotly_chart(bar_chart(acc, "Age Bracket", "Policies", "Vehicle Age by Country", color="Country"),
                                use_container_width=True)
            with col3:
                aavg = adf.groupby("Age Bracket", observed=True)["Annual Premium"].mean().reset_index()
                aavg.columns = ["Age Bracket", "Avg Premium"]
                aavg["Avg Premium"] = aavg["Avg Premium"].apply(lambda v: convert(v, cur))
                st.plotly_chart(bar_chart(aavg, "Age Bracket", "Avg Premium", f"Avg Premium by Age ({cur})"),
                                use_container_width=True)

        with ev_tab3:
            st.subheader("EV — KM Driven")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_km_c")
            kdf = ev[ev["Country"].isin(h_country)].copy()
            kdf["KM Bracket"] = pd.cut(kdf["KM Driven"], bins=[0, 25000, 50000, 100000, 150000, 250000],
                                        labels=["0-25K", "25-50K", "50-100K", "100-150K", "150K+"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Policies", f"{len(kdf):,}")
            c2.metric("Avg KM", f"{kdf['KM Driven'].mean():,.0f}")
            c3.metric("Avg Age", f"{kdf['Vehicle Age'].mean():.1f} yrs")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                kc = kdf.groupby("KM Bracket", observed=True)["Contract ID"].count().reset_index()
                kc.columns = ["KM Bracket", "Policies"]
                st.plotly_chart(bar_chart(kc, "KM Bracket", "Policies", "Policies by KM Driven"),
                                use_container_width=True)
            with col2:
                kcc = kdf.groupby(["KM Bracket", "Country"], observed=True)["Contract ID"].count().reset_index()
                kcc.columns = ["KM Bracket", "Country", "Policies"]
                st.plotly_chart(bar_chart(kcc, "KM Bracket", "Policies", "KM Driven by Country", color="Country"),
                                use_container_width=True)
            with col3:
                kavg = kdf.groupby("KM Bracket", observed=True)["Annual Premium"].mean().reset_index()
                kavg.columns = ["KM Bracket", "Avg Premium"]
                kavg["Avg Premium"] = kavg["Avg Premium"].apply(lambda v: convert(v, cur))
                st.plotly_chart(bar_chart(kavg, "KM Bracket", "Avg Premium", f"Avg Premium by KM ({cur})"),
                                use_container_width=True)

        with ev_tab4:
            st.subheader("EV — Health vs KM")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_hkm_c")
            hkdf = ev[ev["Country"].isin(h_country)].copy()
            hkdf["KM Bracket"] = pd.cut(hkdf["KM Driven"], bins=[0, 25000, 50000, 100000, 150000, 250000],
                                         labels=["0-25K", "25-50K", "50-100K", "100-150K", "150K+"])

            c1, c2, c3 = st.columns(3)
            with c1:
                hkc = hkdf.groupby(["KM Bracket", "Health State"], observed=True)["Contract ID"].count().reset_index()
                hkc.columns = ["KM Bracket", "Health", "Policies"]
                st.plotly_chart(bar_chart(hkc, "KM Bracket", "Policies", "Health vs KM", color="Health"),
                                use_container_width=True)
            with c2:
                hka = hkdf.groupby(["KM Bracket", "Health State"], observed=True)["Claims"].sum().reset_index()
                hka.columns = ["KM Bracket", "Health", "Claims"]
                st.plotly_chart(bar_chart(hka, "KM Bracket", "Claims", "Claims vs KM", color="Health"),
                                use_container_width=True)
            with c3:
                hks = hkdf.groupby(["KM Bracket", "Health State"], observed=True)["Claim Amount"].sum().reset_index()
                hks.columns = ["KM Bracket", "Health", "Claim Amount"]
                hks["Claim Amount"] = hks["Claim Amount"].apply(lambda v: convert(v, cur))
                st.plotly_chart(bar_chart(hks, "KM Bracket", "Claim Amount", f"Claim Amount vs KM ({cur})", color="Health"),
                                use_container_width=True)

        with ev_tab5:
            st.subheader("EV — Health vs Age")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_hage_c")
            hadf = ev[ev["Country"].isin(h_country)].copy()
            hadf["Age Bracket"] = pd.cut(hadf["Vehicle Age"], bins=[0, 3, 5, 10, 15],
                                          labels=["1-3 yrs", "4-5 yrs", "6-10 yrs", "11-15 yrs"])

            c1, c2, c3 = st.columns(3)
            with c1:
                hac = hadf.groupby(["Age Bracket", "Health State"], observed=True)["Contract ID"].count().reset_index()
                hac.columns = ["Age Bracket", "Health", "Policies"]
                st.plotly_chart(bar_chart(hac, "Age Bracket", "Policies", "Health vs Age", color="Health"),
                                use_container_width=True)
            with c2:
                haa = hadf.groupby(["Age Bracket", "Health State"], observed=True)["Claims"].sum().reset_index()
                haa.columns = ["Age Bracket", "Health", "Claims"]
                st.plotly_chart(bar_chart(haa, "Age Bracket", "Claims", "Claims vs Age", color="Health"),
                                use_container_width=True)
            with c3:
                has_ = hadf.groupby(["Age Bracket", "Health State"], observed=True)["Claim Amount"].sum().reset_index()
                has_.columns = ["Age Bracket", "Health", "Claim Amount"]
                has_["Claim Amount"] = has_["Claim Amount"].apply(lambda v: convert(v, cur))
                st.plotly_chart(bar_chart(has_, "Age Bracket", "Claim Amount", f"Claim Amount vs Age ({cur})", color="Health"),
                                use_container_width=True)

        with ev_tab6:
            st.subheader("EV — Warranty by Model")
            h_country = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="ev_model_c")
            mdf = ev[ev["Country"].isin(h_country)]

            if "Model" not in mdf.columns:
                st.warning("Model data not available. Clear Streamlit cache and reload.")
                st.cache_data.clear()
                st.rerun()

            c1, c2, c3 = st.columns(3)
            c1.metric("Policies", f"{len(mdf):,}")
            c2.metric("Brands", f"{mdf['Brand'].nunique()}")
            c3.metric("Models", f"{mdf['Model'].nunique()}")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Warranty count by Model
                mc = mdf.groupby("Model").agg(
                    Warranties=("Contract ID", "count"),
                    Avg_Premium=("Annual Premium", "mean"),
                ).reset_index().sort_values("Warranties", ascending=False)
                mc["Avg_Premium"] = mc["Avg_Premium"].apply(lambda v: convert(v, cur))
                fig_mc = bar_chart(mc.rename(columns={"Warranties": "Count"}), "Model", "Count",
                                   "Warranty Count by Model")
                st.plotly_chart(fig_mc, use_container_width=True)

            with col2:
                # Warranty count by Brand & Model
                bm = mdf.groupby(["Brand", "Model"]).agg(
                    Warranties=("Contract ID", "count"),
                ).reset_index().sort_values("Warranties", ascending=False)
                fig_bm = go.Figure()
                for brand in bm["Brand"].unique():
                    bdata = bm[bm["Brand"] == brand]
                    fig_bm.add_trace(go.Bar(
                        x=bdata["Model"], y=bdata["Warranties"], name=brand,
                        text=[f"{int(v):,}" for v in bdata["Warranties"]],
                        textposition="outside", textfont=dict(size=10, color=CHART_TEXT),
                    ))
                _base_layout(fig_bm, 420)
                fig_bm.update_layout(title="Warranties by Brand & Model", barmode="group",
                                     legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig_bm, use_container_width=True)

            with col3:
                # Avg premium by Model
                mp = mdf.groupby("Model")["Annual Premium"].mean().reset_index()
                mp.columns = ["Model", "Avg Premium"]
                mp["Avg Premium"] = mp["Avg Premium"].apply(lambda v: convert(v, cur))
                mp = mp.sort_values("Avg Premium", ascending=False)
                fig_mp = bar_chart(mp, "Model", "Avg Premium", f"Avg Premium by Model ({cur})")
                st.plotly_chart(fig_mp, use_container_width=True)

            st.markdown("---")
            col4, col5 = st.columns(2)

            with col4:
                # Health state by Model
                hm = mdf.groupby(["Model", "Health State"]).agg(
                    Policies=("Contract ID", "count"),
                ).reset_index()
                hm.columns = ["Model", "Health", "Policies"]
                fig_hm = bar_chart(hm, "Model", "Policies", "Health State by Model", color="Health")
                st.plotly_chart(fig_hm, use_container_width=True)

            with col5:
                # Model table with key stats
                stats = mdf.groupby("Model").agg(
                    Policies=("Contract ID", "count"),
                    Avg_Premium=("Annual Premium", "mean"),
                    Total_Claims=("Claims", "sum"),
                    Avg_Age=("Vehicle Age", "mean"),
                    Avg_KM=("KM Driven", "mean"),
                ).reset_index()
                stats["Avg_Premium"] = stats["Avg_Premium"].apply(lambda v: convert(v, cur))
                stats = stats.sort_values("Policies", ascending=False)
                st.dataframe(stats, use_container_width=True, height=300)

# ─────────────────────────────────────────────
# PAGE 6: IPI POLICY ANALYSIS
# ─────────────────────────────────────────────
elif page == "🛡️ IPI Policy Analysis":
    st.title("🛡️ IPI Policy Analysis")
    ipi = df_filtered[df_filtered["Product"] == "Income Protection"].copy()
    if ipi.empty:
        st.warning("No IPI data in selected period.")
    else:
        ipi_tab1, ipi_tab2, ipi_tab3 = st.tabs(["📊 Overview", "🏢 By Insurer", "📋 By Plan"])

        with ipi_tab1:
            st.subheader("IPI Overview")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Policies", f"{len(ipi):,}")
            ipi_unique = ipi.drop_duplicates("Contract ID")
            c2.metric("Total Premium", fmt(convert(true_premium_sum(ipi), cur), cur))
            c3.metric("Avg Premium", fmt(convert(ipi_unique["Annual Premium"].mean(), cur), cur))
            c4.metric("Corporate %",
                       f"{len(ipi[ipi['Type'] == 'Corporate']) / len(ipi) * 100:.1f}%" if len(ipi) > 0 else "—")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                tc = ipi.groupby("Type")["Contract ID"].count().reset_index()
                tc.columns = ["Type", "Policies"]
                st.plotly_chart(bar_chart(tc, "Type", "Policies", "Policies by Type"), use_container_width=True)
            with col2:
                nc = ipi.groupby("Country")["Contract ID"].count().reset_index()
                nc.columns = ["Country", "Policies"]
                st.plotly_chart(bar_chart(nc, "Country", "Policies", "Policies by Country", color_map=COUNTRY_COLORS),
                                use_container_width=True)
            with col3:
                rc = ipi.groupby("Renewed")["Contract ID"].count().reset_index()
                rc.columns = ["Renewed", "Policies"]
                rc["Renewed"] = rc["Renewed"].map({True: "Renewed", False: "Not Renewed"})
                st.plotly_chart(bar_chart(rc, "Renewed", "Policies", "Renewal Status"), use_container_width=True)

        with ipi_tab2:
            st.subheader("IPI by Insurer")
            ins = ipi.groupby("Insurer").agg(
                Policies=("Contract ID", "count"),
            ).reset_index()
            ins_prem = (ipi.drop_duplicates("Contract ID")
                        .groupby("Insurer")
                        .agg(Total_Premium=("Annual Premium", "sum"),
                             Avg_Premium=("Annual Premium", "mean"))
                        .reset_index())
            ins = ins.merge(ins_prem, on="Insurer", how="left").fillna({"Total_Premium": 0, "Avg_Premium": 0})
            ins["Total_Premium"] = ins["Total_Premium"].apply(lambda v: convert(v, cur))
            ins["Avg_Premium"] = ins["Avg_Premium"].apply(lambda v: convert(v, cur))

            c1, c2, c3 = st.columns(3)
            with c1:
                st.plotly_chart(bar_chart(ins.rename(columns={"Policies": "Count"}), "Insurer", "Count",
                                          "Policies by Insurer"), use_container_width=True)
            with c2:
                st.plotly_chart(bar_chart(ins.rename(columns={"Total_Premium": f"Revenue ({cur})"}),
                                          "Insurer", f"Revenue ({cur})", f"Revenue by Insurer ({cur})"),
                                use_container_width=True)
            with c3:
                st.plotly_chart(bar_chart(ins.rename(columns={"Avg_Premium": f"Avg Premium ({cur})"}),
                                          "Insurer", f"Avg Premium ({cur})", f"Avg Premium by Insurer ({cur})"),
                                use_container_width=True)

        with ipi_tab3:
            st.subheader("IPI by Plan")
            plan = ipi.groupby("Plan").agg(
                Policies=("Contract ID", "count"),
                Lives=("Lives Insured", "sum"),
            ).reset_index()
            plan_prem = (ipi.drop_duplicates("Contract ID")
                         .groupby("Plan")
                         .agg(Total_Premium=("Annual Premium", "sum"),
                              Avg_Premium=("Annual Premium", "mean"))
                         .reset_index())
            plan = plan.merge(plan_prem, on="Plan", how="left").fillna({"Total_Premium": 0, "Avg_Premium": 0})
            plan["Total_Premium"] = plan["Total_Premium"].apply(lambda v: convert(v, cur))
            plan["Avg_Premium"] = plan["Avg_Premium"].apply(lambda v: convert(v, cur))

            c1, c2, c3 = st.columns(3)
            with c1:
                st.plotly_chart(bar_chart(plan.rename(columns={"Policies": "Count"}), "Plan", "Count",
                                          "Policies by Plan"), use_container_width=True)
            with c2:
                st.plotly_chart(bar_chart(plan.rename(columns={"Total_Premium": f"Revenue ({cur})"}),
                                          "Plan", f"Revenue ({cur})", f"Revenue by Plan ({cur})"),
                                use_container_width=True)
            with c3:
                st.plotly_chart(bar_chart(plan.rename(columns={"Avg_Premium": f"Avg Premium ({cur})"}),
                                          "Plan", f"Avg Premium ({cur})", f"Avg Premium by Plan ({cur})"),
                                use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 7: RAW DATA
# ─────────────────────────────────────────────
elif page == "📋 Raw Data":
    st.title("📋 Raw Data")
    st.caption(f"Showing {len(df_filtered):,} policies for selected period")

    # Add computed columns
    display_df = df_filtered.copy()
    display_df["Commission"] = (display_df["Annual Premium"] * COMMISSION_RATE).round(2)
    display_df["Active"] = pd.to_datetime(display_df["End Date"]) >= pd.Timestamp.now()

    st.dataframe(display_df, use_container_width=True, height=600)

    # Download
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"policies_{d_start}_{d_end}.csv",
        mime="text/csv",
    )
