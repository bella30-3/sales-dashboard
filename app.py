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
# DARK THEME
# ─────────────────────────────────────────────
ACCENT = "#3360F0"
PAID_COLOR = "#3360F0"
OUTSTANDING_COLOR = "#E04050"
TARGET_COLOR = "#60B0A0"
BG_COLOR = "#0E1117"
CARD_BG = "#1A1F2E"
CARD_BORDER = "#2A3040"
SIDEBAR_BG = "#0E1117"
TEXT_PRIMARY = "#E8ECF1"
TEXT_SECONDARY = "#8899AA"
GRID_COLOR = "rgba(255,255,255,0.06)"
HEADING_COLOR = "#E8ECF1"

PRODUCT_COLORS = {
    "Income Protection": "#3360F0",
    "Automotive": "#60B0A0",
    "Care - Aqua": "#F0B020",
}
PRODUCT_DEFAULT_COLOR = ACCENT

COUNTRY_COLORS = {
    "Singapore": "#E04050",
    "Thailand": "#3050F0",
    "India": "#F0B020",
    "Europe": "#60B0A0",
}
COUNTRY_DEFAULT_COLOR = "#3360F0"

# Gauge colours for semicircle meters
GAUGE_GREEN = "#00D68F"
GAUGE_AMBER = "#FFB020"
GAUGE_RED = "#FF4D4F"

# Commission rate (15% of annual premium)
COMMISSION_RATE = 0.15

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Dark app background */
.stApp {
    font-family: 'Inter', sans-serif;
    background: #0E1117;
    color: #E8ECF1;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0E1117;
    border-right: 1px solid #2A3040;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {
    color: #C8D0D8 !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    color: #E8ECF1 !important;
}
section[data-testid="stSidebar"] .stDateInput label {
    color: #D0D8E0 !important;
    font-weight: 500 !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #E8ECF1 !important;
    font-weight: 700 !important;
}
h1 { font-size: 1.5rem !important; }
h2 { font-size: 1.25rem !important; }
h3 { font-size: 1.1rem !important; }

/* General text */
p, li, span, label, .stMarkdown {
    color: #C8D0D8;
}

/* Metric cards — dark glass look */
.stMetric > div {
    background: #1A1F2E;
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid #2A3040;
}
.stMetric label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #8899AA !important;
}
.stMetric [data-testid="stMetricValue"] {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: #E8ECF1 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    padding: 4px;
    background: #1A1F2E;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 500;
    color: #8899AA;
}
.stTabs [aria-selected="true"] {
    background: #3360F0;
    color: #FFFFFF !important;
    font-weight: 700;
}

/* Plotly charts — dark card with border & shadow */
.stPlotlyChart {
    border-radius: 12px;
    background: #1A253F;
    padding: 6px;
    border: 1px solid #2A3555;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), 0 1px 4px rgba(0, 0, 0, 0.2);
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* Selectbox / multiselect dropdowns */
div[data-baseweb="select"] > div {
    background: #1A253F;
    border-color: #2A3555;
    color: #E8ECF1;
}

/* Date input */
div[data-testid="stDateInput"] input {
    color: #E8ECF1;
}

/* Horizontal rule */
hr {
    border-color: #2A3040 !important;
}

/* Caption / small text */
.stMarkdown small, .stCaption, figcaption {
    color: #6B7B8D !important;
}
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
                        "Health State": health, "Brand": brand,
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

# ─────────────────────────────────────────────
# MONTHLY BUDGET & PROJECTION INPUTS
# ─────────────────────────────────────────────
MONTHS_LIST = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Default budget & projection values (in thousands USD) for each month
if "budget_data" not in st.session_state:
    st.session_state.budget_data = [
        180, 165, 195, 210, 225, 240, 255, 260, 270, 290, 310, 330
    ]
if "projection_data" not in st.session_state:
    st.session_state.projection_data = [
        190, 175, 210, 230, 250, 265, 280, 290, 300, 320, 345, 370
    ]

with st.sidebar.expander("📊 Budget & Projection (Monthly, $k USD)", expanded=False):
    st.caption("Edit monthly targets. These appear on the Actuals vs Budget vs Projection gauge.")
    cols_input = st.columns(2)
    with cols_input[0]:
        st.markdown("**Budget**")
        for i, m in enumerate(MONTHS_LIST):
            st.session_state.budget_data[i] = st.number_input(
                f"{m}", value=float(st.session_state.budget_data[i]),
                step=10.0, key=f"budget_{i}", label_visibility="visible",
            )
    with cols_input[1]:
        st.markdown("**Projection**")
        for i, m in enumerate(MONTHS_LIST):
            st.session_state.projection_data[i] = st.number_input(
                f"{m}", value=float(st.session_state.projection_data[i]),
                step=10.0, key=f"projection_{i}", label_visibility="visible",
            )

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
st.sidebar.caption(f"Premium: **{fmt(convert(df_filtered['Annual Premium'].sum(), cur), cur)}**")

# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
PALETTE = ["#3360F0"]


CHART_BG = "#1A253F"


def _base_layout(fig, height=420):
    fig.update_layout(
        height=height,
        title_font_size=16,
        title_font_color="#E8ECF1",
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(family="Inter, sans-serif", color="#8899AA", size=13),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, color="#8899AA"),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, color="#8899AA"),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(color="#8899AA")),
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
            showarrow=False, font=dict(size=16, color="#8899AA"),
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
            font=dict(size=12, color="#8899AA"), align="center",
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
        number={"suffix": suffix, "font": {"size": 28, "color": TEXT_PRIMARY, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#8899AA",
                     "tickfont": {"size": 11, "color": "#8899AA"}},
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": "#2A3040",
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

def make_concentric_actuals_budget_projection(actual_val, budget_val, projection_val, currency):
    """Concentric semicircle gauge: Actuals (inner), Budget (middle), Projection (outer)."""
    max_val = max(actual_val, budget_val, projection_val) * 1.2
    if max_val == 0:
        max_val = 100

    # Build arcs from 0° (left) to 180° (right) — top semicircle
    theta_arc = [i * 180 / 100 for i in range(101)]

    # Normalize each value to a fraction of max_val for the radial axis
    r_actual = actual_val / max_val * 100
    r_budget = budget_val / max_val * 100
    r_projection = projection_val / max_val * 100

    # Clamp arcs to actual value
    theta_actual = [t for t in theta_arc if t <= (actual_val / max_val) * 180]
    theta_budget = [t for t in theta_arc if t <= (budget_val / max_val) * 180]
    theta_proj = [t for t in theta_arc if t <= (projection_val / max_val) * 180]

    fig = go.Figure()

    # Outer arc — Projection (amber)
    fig.add_trace(go.Scatterpolar(
        r=[r_projection] * len(theta_proj),
        theta=theta_proj,
        mode="lines",
        line=dict(color="#FFB020", width=18, shape="spline"),
        name=f"Projection: {fmt(projection_val, currency)}",
        opacity=0.85,
        hoverinfo="name",
    ))
    # Middle arc — Budget (blue)
    fig.add_trace(go.Scatterpolar(
        r=[r_budget] * len(theta_budget),
        theta=theta_budget,
        mode="lines",
        line=dict(color="#3360F0", width=18, shape="spline"),
        name=f"Budget: {fmt(budget_val, currency)}",
        opacity=0.85,
        hoverinfo="name",
    ))
    # Inner arc — Actuals (green)
    fig.add_trace(go.Scatterpolar(
        r=[r_actual] * len(theta_actual),
        theta=theta_actual,
        mode="lines",
        line=dict(color="#00D68F", width=18, shape="spline"),
        name=f"Actuals: {fmt(actual_val, currency)}",
        opacity=0.95,
        hoverinfo="name",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 105]),
            angularaxis=dict(visible=False, range=[0, 180]),
            bgcolor=CHART_BG,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=TEXT_PRIMARY),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(
            text="Actuals vs Budget vs Projection",
            font=dict(size=14, color="#8899AA", family="Inter"),
        ),
        height=320,
        margin=dict(t=60, b=40, l=40, r=40),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter, sans-serif", color="#8899AA"),
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

    # Average premium in USD
    avg_premium = df_curr["Annual Premium"].mean() if n_policies > 0 else 0

    # Commission
    df_curr_copy = df_curr.copy()
    df_curr_copy["Commission"] = df_curr_copy["Annual Premium"] * COMMISSION_RATE
    total_commission = df_curr_copy["Commission"].sum()
    avg_commission = df_curr_copy["Commission"].mean() if n_policies > 0 else 0

    # Total premium
    total_premium = df_curr["Annual Premium"].sum()

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


def render_metrics(currency):
    """Render the top-row KPI metrics for executive summary with YoY deltas."""
    kpis = compute_kpis(df_filtered, currency)

    # Last year comparison — same date range shifted back 1 year
    ly_start = d_start.replace(year=d_start.year - 1)
    ly_end = d_end.replace(year=d_end.year - 1)
    df_ly = df[(pd.to_datetime(df["Start Date"]).dt.date >= ly_start) &
               (pd.to_datetime(df["Start Date"]).dt.date <= ly_end)]
    kpis_ly = compute_kpis(df_ly, currency)

    # Delta helpers
    def _delta(curr, prev, as_pct=False):
        if prev == 0:
            return None
        diff = curr - prev
        if as_pct:
            return f"{diff:+.1f}pp"
        pct = (diff / prev) * 100
        return f"{pct:+.1f}%"

    def _delta_color(curr, prev):
        if curr >= prev:
            return "normal"  # green for positive
        return "inverse"    # red for negative

    # Top row: Policies, Premium, Avg Premium, Total Commission
    c1, c2, c3, c4 = st.columns(4)
    d1 = _delta(kpis["n_policies"], kpis_ly["n_policies"])
    c1.metric("📋 Policies Sold (YTD)", f"{kpis['n_policies']:,}",
              delta=d1, delta_color=_delta_color(kpis["n_policies"], kpis_ly["n_policies"]))
    d2 = _delta(kpis["total_premium"], kpis_ly["total_premium"])
    c2.metric("💰 Total Premium", fmt(convert(kpis["total_premium"], currency), currency),
              delta=d2, delta_color=_delta_color(kpis["total_premium"], kpis_ly["total_premium"]))
    c3.metric("📊 Avg Premium", fmt2(convert(kpis["avg_premium"], currency), currency))
    d4 = _delta(kpis["total_commission"], kpis_ly["total_commission"])
    c4.metric("💵 Total Commission", fmt(convert(kpis["total_commission"], currency), currency),
              delta=d4, delta_color=_delta_color(kpis["total_commission"], kpis_ly["total_commission"]))

    # Bottom row: Avg Commission, Active %, Renewal %, Lapse Rate
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📈 Avg Commission", fmt2(convert(kpis["avg_commission"], currency), currency))
    c6.metric("✅ Active %", f"{kpis['active_pct']:.1f}%")
    d7 = _delta(kpis["renewal_pct"], kpis_ly["renewal_pct"], as_pct=True)
    c7.metric("🔄 Renewal %", f"{kpis['renewal_pct']:.1f}%",
              delta=d7, delta_color=_delta_color(kpis["renewal_pct"], kpis_ly["renewal_pct"]))
    c8.metric("⚠️ Lapse Rate", f"{kpis['lapse_pct']:.1f}%")


def render_gauge_row(currency):
    """Render concentric gauge (Actuals vs Budget vs Projection) + Renewal & Lapse meters."""
    kpis = compute_kpis(df_filtered, currency)

    # Compute YTD actuals in thousands
    actual_ytd = convert(kpis["total_premium"], currency) / 1000

    # Sum budget & projection for months within the selected date range
    current_month = datetime.now().month  # 1-indexed
    budget_ytd = sum(st.session_state.budget_data[:current_month])
    projection_ytd = sum(st.session_state.projection_data[:current_month])

    g1, g2, g3 = st.columns(3)
    with g1:
        fig_concentric = make_concentric_actuals_budget_projection(
            actual_ytd, budget_ytd, projection_ytd, currency
        )
        st.plotly_chart(fig_concentric, use_container_width=True)
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
                font=dict(family="Inter, sans-serif", color="#8899AA"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                            font=dict(color="#8899AA")),
                margin=dict(t=60, b=60, l=30, r=30),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.plotly_chart(empty_state("Policies Sold by Product"), use_container_width=True)

    with c2:
        # Revenue by Product
        rev = df_filtered.groupby("Product Label")["Annual Premium"].sum().reset_index()
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
            Premium=("Annual Premium", "sum"), Contracts=("Contract ID", "count"),
        ).reset_index().sort_values("YearMonth")
        ma["Premium"] = ma["Premium"].apply(lambda v: convert(v, cur))
        ma["Month"] = ma["YearMonth"].apply(lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%b %Y"))

        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(
            x=ma["Month"], y=ma["Premium"], name="Revenue",
            marker_color=PAID_COLOR,
            hovertemplate="%{x}<br>Revenue: %{y:,.2f}<extra></extra>",
        ))
        for xm, ym, cm in zip(ma["Month"], ma["Premium"], ma["Contracts"]):
            fig_m.add_annotation(
                x=xm, y=ym, text=f"<b>{_fmt_val(ym)}</b><br>{cm:,} policies",
                showarrow=False, yshift=15,
                font=dict(size=9, color="#8899AA"), align="center",
            )
        _base_layout(fig_m, 420)
        fig_m.update_layout(title=f"Monthly Revenue ({cur})", xaxis=dict(tickangle=-45, gridcolor=GRID_COLOR),
                            margin=dict(t=50, b=70))
        st.plotly_chart(fig_m, use_container_width=True)

    with c5:
        # Monthly revenue by product (line)
        mp = df_filtered.groupby(["YearMonth", "Product Label"]).agg(
            Premium=("Annual Premium", "sum"), Contracts=("Contract ID", "count"),
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
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
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
            textposition="outside", textfont=dict(size=11, color="#8899AA"),
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
    c2.metric("💰 Total Premium", fmt(convert(rdf["Annual Premium"].sum(), cur), cur))
    c3.metric("📊 Avg Premium", fmt(convert(rdf["Annual Premium"].mean(), cur) if len(rdf) > 0 else 0, cur))
    c4.metric("💵 Total Commission", fmt(convert(rdf["Annual Premium"].sum() * COMMISSION_RATE, cur), cur))
    st.markdown("---")

    # 3-column charts
    c1, c2, c3 = st.columns(3)

    with c1:
        rp = rdf.groupby("Product Label").agg(
            Contracts=("Contract ID", "count"), Revenue=("Annual Premium", "sum"),
        ).reset_index()
        rp.columns = ["Product", "Policies Sold"]
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
        cl = rdf.groupby(["Country", "Client"]).agg(
            Revenue=("Annual Premium", "sum"),
        ).reset_index()
        cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
        cl = cl.sort_values("Revenue", ascending=False).head(10)
        fig_tc = go.Figure()
        for country in cl["Country"].unique():
            cdata = cl[cl["Country"] == country]
            fig_tc.add_trace(go.Bar(
                y=cdata["Client"], x=cdata["Revenue"], name=country, orientation="h",
                marker_color=COUNTRY_COLORS.get(country, COUNTRY_DEFAULT_COLOR),
                text=[fmt(v, cur) for v in cdata["Revenue"]],
                textposition="outside", textfont=dict(size=10, color="#8899AA"),
            ))
        _base_layout(fig_tc, max(350, len(cl) * 30))
        fig_tc.update_layout(title=f"Top Clients — {region_sel} ({cur})", barmode="group",
                             margin=dict(t=50, b=50, l=150))
        st.plotly_chart(fig_tc, use_container_width=True)

    with c6:
        # Commission by country
        rdf_c = rdf.copy()
        rdf_c["Commission"] = rdf_c["Annual Premium"] * COMMISSION_RATE
        comm = rdf_c.groupby("Country")["Commission"].sum().reset_index()
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
    c2.metric("💰 Total Premium", fmt(convert(cdf["Annual Premium"].sum(), cur), cur))
    c3.metric("📊 Avg Premium", fmt(convert(cdf["Annual Premium"].mean(), cur) if len(cdf) > 0 else 0, cur))
    c4.metric("💵 Total Commission", fmt(convert(cdf["Annual Premium"].sum() * COMMISSION_RATE, cur), cur))
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
                textposition="outside", textfont=dict(size=10, color="#8899AA"),
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
                                    textposition="outside", textfont=dict(size=10, color="#8899AA")))
            fig_cr.add_trace(go.Bar(x=pdata["Country"], y=pdata["Outstanding"], name=f"Pending — {prod_name}",
                                    marker_color=OUTSTANDING_COLOR,
                                    text=[fmt(v, cur) for v in pdata["Outstanding"]],
                                    textposition="outside", textfont=dict(size=10, color="#8899AA")))
        _base_layout(fig_cr, 420)
        fig_cr.update_layout(title=f"Revenue — {sel_label} ({cur})", barmode="group",
                             xaxis=dict(gridcolor=GRID_COLOR))
        st.plotly_chart(fig_cr, use_container_width=True)

    with c3:
        cl = cdf.groupby(["Country", "Client"]).agg(
            Revenue=("Annual Premium", "sum"),
        ).reset_index()
        cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
        cl = cl.sort_values("Revenue", ascending=False).head(15)
        fig_tc = go.Figure()
        for country in cl["Country"].unique():
            cdata = cl[cl["Country"] == country]
            fig_tc.add_trace(go.Bar(
                y=cdata["Client"], x=cdata["Revenue"], name=country, orientation="h",
                marker_color=COUNTRY_COLORS.get(country, COUNTRY_DEFAULT_COLOR),
                text=[fmt(v, cur) for v in cdata["Revenue"]],
                textposition="outside", textfont=dict(size=10, color="#8899AA"),
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
        c2.metric("💰 Total Premium", fmt(convert(pdf["Annual Premium"].sum(), cur), cur))
        c3.metric("📊 Avg Premium", fmt(convert(pdf["Annual Premium"].mean(), cur), cur))
        c4.metric("💵 Total Commission", fmt(convert(pdf["Annual Premium"].sum() * COMMISSION_RATE, cur), cur))
        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        with c1:
            cp = pdf.groupby("Country").agg(
                Revenue=("Annual Premium", "sum"), Contracts=("Contract ID", "count"),
            ).reset_index()
            cp["Revenue"] = cp["Revenue"].apply(lambda v: convert(v, cur))
            bar_colors = [COUNTRY_COLORS.get(c, COUNTRY_DEFAULT_COLOR) for c in cp["Country"]]
            fig_prc = go.Figure(go.Bar(
                y=cp["Country"], x=cp["Revenue"], orientation="h",
                marker_color=bar_colors,
                text=[fmt(v, cur) for v in cp["Revenue"]],
                textposition="outside", textfont=dict(size=11, color="#8899AA"),
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
                            textposition="outside", textfont=dict(size=10, color="#8899AA"),
                        ))
                        fig_plan.add_trace(go.Bar(
                            y=cdata["Plan"], x=cdata["Outstanding"], name=f"Pending — {country}",
                            orientation="h", marker_color=OUTSTANDING_COLOR,
                            text=[fmt(v, cur) for v in cdata["Outstanding"]],
                            textposition="outside", textfont=dict(size=10, color="#8899AA"),
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
                Revenue=("Annual Premium", "sum"), Contracts=("Contract ID", "count"),
            ).reset_index()
            cl["Revenue"] = cl["Revenue"].apply(lambda v: convert(v, cur))
            cl = cl.sort_values("Revenue", ascending=False).head(10)
            fig_ptc = go.Figure()
            for country in cl["Country"].unique():
                cdata = cl[cl["Country"] == country]
                fig_ptc.add_trace(go.Bar(
                    y=cdata["Client"], x=cdata["Revenue"], name=country, orientation="h",
                    marker_color=COUNTRY_COLORS.get(country, COUNTRY_DEFAULT_COLOR),
                    text=[fmt(v, cur) for v in cdata["Revenue"]],
                    textposition="outside", textfont=dict(size=10, color="#8899AA"),
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
        ev_tab1, ev_tab2, ev_tab3, ev_tab4, ev_tab5 = st.tabs([
            "🩺 State of Health", "📅 By Age", "🛣️ By KM", "🔄 Health vs KM", "🔄 Health vs Age"])

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
            c2.metric("Total Premium", fmt(convert(ipi["Annual Premium"].sum(), cur), cur))
            c3.metric("Avg Premium", fmt(convert(ipi["Annual Premium"].mean(), cur), cur))
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
                Total_Premium=("Annual Premium", "sum"),
                Avg_Premium=("Annual Premium", "mean"),
            ).reset_index()
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
                Total_Premium=("Annual Premium", "sum"),
                Avg_Premium=("Annual Premium", "mean"),
                Lives=("Lives Insured", "sum"),
            ).reset_index()
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
