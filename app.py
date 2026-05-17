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
st.set_page_config(page_title="Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────
PRODUCTS = {
    "EV / Auto": {
        "label": "Electric Vehicles / Auto",
        "desc": "Service Contracts & Warranties",
        "plans": {
            "India": ["Basic", "Premium", "Enterprise"],
            "Singapore": ["Standard", "Gold", "Platinum"],
            "Thailand": ["Basic", "Plus", "Premium"],
        },
    },
    "Income Protection": {
        "label": "Income Protection Insurance",
        "desc": "Contracts & Premiums",
        "plans": {
            "India": ["Individual", "Family", "Corporate"],
            "Singapore": ["DBS Staff 2000", "DBS Staff 5000", "OCBC GA Mandatory 3M A", "OCBC GA Mandatory 3M B", "OCBC GA Mandatory 3M C", "OCBC GA Mandatory 3M 5", "OCBC GA 12M A", "OCBC GA 12M B", "OCBC GA 12M C", "OCBC GA 12M 5"],
            "Thailand": ["Basic", "Advanced", "Premium"],
        },
        "premiums": {
            "DBS Staff 2000": 200,
            "DBS Staff 5000": 400,
            "OCBC GA Mandatory 3M A": 75,
            "OCBC GA Mandatory 3M B": 100,
            "OCBC GA Mandatory 3M C": 150,
            "OCBC GA Mandatory 3M 5": 150,
            "OCBC GA 12M A": 500,
            "OCBC GA 12M B": 1000,
            "OCBC GA 12M C": 1500,
            "OCBC GA 12M 5": 1500,
        },
        "types": {
            "DBS Staff 2000": "Individual",
            "DBS Staff 5000": "Individual",
            "OCBC GA Mandatory 3M A": "Corporate",
            "OCBC GA Mandatory 3M B": "Corporate",
            "OCBC GA Mandatory 3M C": "Corporate",
            "OCBC GA Mandatory 3M 5": "Corporate",
            "OCBC GA 12M A": "Corporate",
            "OCBC GA 12M B": "Corporate",
            "OCBC GA 12M C": "Corporate",
            "OCBC GA 12M 5": "Corporate",
        },
    },
    "Care Aqua": {
        "label": "Care - Aqua Warranty",
        "desc": "Warranty Contracts & Amounts",
        "plans": {
            "India": ["Standard", "Extended", "Full Cover"],
            "Singapore": ["Basic", "Plus", "Comprehensive"],
            "Thailand": ["Economy", "Standard", "Premium"],
            "Europe": ["Basic", "Standard", "Premium"],
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
        "Singapore": ["Cycle and Carriage", "Porsche", "BYD"],
        "Thailand": ["Porsche", "BYD Forklift", "Subaru", "Hyundai"],
    },
    "Income Protection": {
        "India": ["RQBE"],
        "Singapore": ["OCBC (GE)", "DBS (ECICS)"],
        "Thailand": ["Muang Thai"],
    },
    "Care Aqua": {
        "India": [],
        "Singapore": [],
        "Thailand": [],
        "Europe": ["Airspring"],
    },
}

CLIENTS = list(set(c for p in CLIENTS_BY_PRODUCT_COUNTRY.values() for cs in p.values() for c in cs))
TYPES = ["Individual", "Corporate"]
TRAN_TYPES = ["Inst", "Single"]


def get_plan_premium(prod, plan):
    premiums = PRODUCTS.get(prod, {}).get("premiums", {})
    return premiums.get(plan)

def get_plan_type(prod, plan):
    types = PRODUCTS.get(prod, {}).get("types", {})
    return types.get(plan)

def get_client(product, country):
    clients = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {}).get(country, [])
    if not clients:
        all_pc = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {})
        clients = [c for cs in all_pc.values() for c in cs]
    return random.choice(clients) if clients else "Unknown"

# Monthly premium targets in SGD (converted to USD at 1.35 rate)
SGD_TO_USD = 1.35
MONTHLY_TARGETS_SGD = {
    "Income Protection": 20000,  # ~20k SGD/month across all regions
    "EV / Auto": 15000,          # ~15k SGD/month worldwide
    "Care Aqua": 6000,            # ~6k SGD/month
}
MONTHLY_TARGETS_USD = {k: v / SGD_TO_USD for k, v in MONTHLY_TARGETS_SGD.items()}

def generate_data():
    """Generate monthly contract data from Jan 2023 to today.
    Monthly premium targets (SGD):
      - IPI: ~20,000 SGD/mo
      - EV/Auto: ~15,000 SGD/mo
      - Care Aqua: ~6,000 SGD/mo
    """
    rows = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    current = start_date

    while current <= end_date:
        year, month = current.year, current.month
        # Seasonal variation: Q4 tends to be stronger, Q1 weaker
        seasonal = 1.0
        if month in (10, 11, 12):
            seasonal = random.uniform(1.1, 1.35)  # Q4 boost
        elif month in (1, 2):
            seasonal = random.uniform(0.75, 0.9)   # Q1 dip
        elif month in (4, 5):
            seasonal = random.uniform(0.95, 1.1)   # mid-year pickup
        else:
            seasonal = random.uniform(0.9, 1.1)

        # Year-over-year growth factor (~8-15% per year)
        years_elapsed = (current - start_date).days / 365.25
        growth = (1.0 + 0.10) ** years_elapsed  # 10% CAGR

        # Some months have anomalies (good/bad months)
        anomaly = 1.0
        if random.random() < 0.1:  # 10% chance of a bad month
            anomaly = random.uniform(0.5, 0.75)
        elif random.random() < 0.08:  # 8% chance of a great month
            anomaly = random.uniform(1.3, 1.6)

        for prod, base_target_usd in MONTHLY_TARGETS_USD.items():
            monthly_budget = base_target_usd * seasonal * growth * anomaly

            # Determine number of contracts for this month
            avg_contract = {"Income Protection": 800, "EV / Auto": 1200, "Care Aqua": 600}[prod]
            n_contracts = max(3, int(monthly_budget / avg_contract * random.uniform(0.6, 1.4)))

            # Distribute budget across contracts with some skew
            weights = np.random.dirichlet(np.ones(n_contracts) * 0.5)  # skewed distribution
            contract_premiums = weights * monthly_budget

            for i, premium in enumerate(contract_premiums):
                premium = max(50, round(premium))

                # Country distribution
                if prod == "Care Aqua":
                    if random.random() < 0.15:
                        country = "Europe"
                    else:
                        country = random.choice(["India", "Singapore", "Thailand"])
                else:
                    country = random.choice([c for c in COUNTRIES.keys() if c != "Europe"])
                region = COUNTRIES[country]

                plan = random.choice(PRODUCTS[prod]["plans"].get(country, PRODUCTS[prod]["plans"][list(PRODUCTS[prod]["plans"].keys())[0]]))
                plan_type = get_plan_type(prod, plan)
                ctype = plan_type if plan_type else random.choice(TYPES)
                client = get_client(prod, country)
                trantype = random.choice(TRAN_TYPES)

                # Paid/outstanding split — more realistic: most contracts partially paid
                paid_pct = random.uniform(0.3, 1.0)
                paid = round(premium * paid_pct)
                outstanding = premium - paid

                inst_count = random.randint(1, 12) if trantype == "Inst" else 1

                # Contract start date within the month
                days_in_month = (current.replace(month=month % 12 + 1, day=1) - timedelta(days=1)).day if month < 12 else 31
                start_day = random.randint(1, min(days_in_month, 28))
                start = datetime(year, month, start_day)
                end = start + timedelta(days=365)
                target = premium * random.uniform(1.1, 1.5)

                rows.append({
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
                })

        # Move to next month
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

page = st.sidebar.radio("Navigate", [
    "🌍 Overall Product (World)",
    "🗺️ Region Drill Down",
    "🏳️ Country Drill Down",
    "📦 Product Drill Down",
    "📋 Raw Data",
])

st.sidebar.markdown("---")
st.sidebar.caption(f"Total Contracts: **{len(df):,}**")
st.sidebar.caption(f"Total Premium: **{fmt(convert(df['Annual Premium'].sum(), cur), cur)}**")
st.sidebar.caption(f"Date Range: **{df['Start Date'].min()}** to **{df['Start Date'].max()}**")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def bar_chart(data, x, y, title, color=None, barmode="group"):
    fig = px.bar(data, x=x, y=y, color=color, title=title, barmode=barmode,
                 text_auto=".2s", color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=450, title_font_size=16, xaxis_title="", yaxis_title="",
                      legend_title="", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_traces(textposition="outside")
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

def melt_premiums(agg, id_col):
    return agg.melt(id_vars=[id_col, "Contracts"],
                    value_vars=["Total_Premium", "Paid", "Outstanding", "Target"],
                    var_name="Metric", value_name="Amount")

# ─────────────────────────────────────────────
# PAGE 1: OVERALL PRODUCT (WORLD)
# ─────────────────────────────────────────────
if page == "🌍 Overall Product (World)":
    st.title("🌍 Overall Product Performance — Worldwide")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Contracts", f"{len(df):,}")
    col2.metric("Total Premium", fmt(convert(df['Annual Premium'].sum(), cur), cur))
    col3.metric("Total Paid", fmt(convert(df['Paid'].sum(), cur), cur))
    col4.metric("Outstanding", fmt(convert(df['Outstanding'].sum(), cur), cur))
    st.markdown("---")

    # Contracts by product
    pc = df.groupby("Product Label")["Contract ID"].count().reset_index()
    pc.columns = ["Product", "Contracts"]
    st.plotly_chart(bar_chart(pc, "Product", "Contracts", "Contract Count by Product"), use_container_width=True)

    # Premium by product
    agg = make_summary(df, "Product Label")
    agg.rename(columns={"Product Label": "Product"}, inplace=True)
    agg = convert_cols(agg, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
    st.plotly_chart(bar_chart(melt_premiums(agg, "Product"), "Product", "Amount",
                              f"Premium Breakdown by Product ({cur})", color="Metric"), use_container_width=True)

    # Contracts by Product + Region
    pr = df.groupby(["Product Label", "Region"])["Contract ID"].count().reset_index()
    pr.columns = ["Product", "Region", "Contracts"]
    st.plotly_chart(bar_chart(pr, "Product", "Contracts", "Contract Count by Product & Region", color="Region"), use_container_width=True)

    # Premium by Product + Region
    pr2 = df.groupby(["Product Label", "Region"]).agg(
        Total_Premium=("Annual Premium", "sum"), Paid=("Paid", "sum"),
        Outstanding=("Outstanding", "sum"), Target=("Target", "sum"),
    ).reset_index()
    pr2.rename(columns={"Product Label": "Product"}, inplace=True)
    pr2 = convert_cols(pr2, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
    pr2m = pr2.melt(id_vars=["Product", "Region"], value_vars=["Total_Premium", "Paid", "Outstanding", "Target"],
                    var_name="Metric", value_name="Amount")
    fig = px.bar(pr2m, x="Product", y="Amount", color="Metric", barmode="group",
                 facet_row="Region", text_auto=".2s",
                 title=f"Premium Breakdown by Product & Region ({cur})",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=600, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 2: REGION DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🗺️ Region Drill Down":
    st.title("🗺️ Region Drill Down")
    region_sel = st.selectbox("Select Region", REGIONS)
    rdf = df[df["Region"] == region_sel]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Contracts", f"{len(rdf):,}")
    col2.metric("Total Premium", fmt(convert(rdf['Annual Premium'].sum(), cur), cur))
    col3.metric("Paid", fmt(convert(rdf['Paid'].sum(), cur), cur))
    col4.metric("Outstanding", fmt(convert(rdf['Outstanding'].sum(), cur), cur))
    st.markdown("---")

    # Contracts by Product
    rp = rdf.groupby("Product Label")["Contract ID"].count().reset_index()
    rp.columns = ["Product", "Contracts"]
    st.plotly_chart(bar_chart(rp, "Product", "Contracts", f"Contract Count — {region_sel}"), use_container_width=True)

    # Premium by Product
    agg = make_summary(rdf, "Product Label")
    agg.rename(columns={"Product Label": "Product"}, inplace=True)
    agg = convert_cols(agg, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
    st.plotly_chart(bar_chart(melt_premiums(agg, "Product"), "Product", "Amount",
                              f"Premium Breakdown — {region_sel} ({cur})", color="Metric"), use_container_width=True)

    # Premium by Country
    rc = rdf.groupby("Country").agg(
        Contracts=("Contract ID", "count"), Total_Premium=("Annual Premium", "sum"),
        Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"), Target=("Target", "sum"),
    ).reset_index()
    rc = convert_cols(rc, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
    rcm = rc.melt(id_vars=["Country", "Contracts"], value_vars=["Total_Premium", "Paid", "Outstanding", "Target"],
                  var_name="Metric", value_name="Amount")
    st.plotly_chart(bar_chart(rcm, "Country", "Amount", f"Premium by Country — {region_sel} ({cur})", color="Metric"), use_container_width=True)

    # Contracts by Country + Product
    cp = rdf.groupby(["Country", "Product Label"])["Contract ID"].count().reset_index()
    cp.columns = ["Country", "Product", "Contracts"]
    st.plotly_chart(bar_chart(cp, "Country", "Contracts", f"Contracts by Country & Product — {region_sel}", color="Product"), use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 3: COUNTRY DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🏳️ Country Drill Down":
    st.title("🏳️ Country Drill Down")
    country_sel = st.selectbox("Select Country", list(COUNTRIES.keys()))
    cdf = df[df["Country"] == country_sel]

    tab1, tab2 = st.tabs(["📊 All Products", "📋 Plan Level"])

    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Contracts", f"{len(cdf):,}")
        col2.metric("Total Premium", fmt(convert(cdf['Annual Premium'].sum(), cur), cur))
        col3.metric("Paid", fmt(convert(cdf['Paid'].sum(), cur), cur))
        col4.metric("Outstanding", fmt(convert(cdf['Outstanding'].sum(), cur), cur))
        st.markdown("---")

        cp = cdf.groupby("Product Label")["Contract ID"].count().reset_index()
        cp.columns = ["Product", "Contracts"]
        st.plotly_chart(bar_chart(cp, "Product", "Contracts", f"Contracts by Product — {country_sel}"), use_container_width=True)

        agg = make_summary(cdf, "Product Label")
        agg.rename(columns={"Product Label": "Product"}, inplace=True)
        agg = convert_cols(agg, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
        st.plotly_chart(bar_chart(melt_premiums(agg, "Product"), "Product", "Amount",
                                  f"Premium Breakdown — {country_sel} ({cur})", color="Metric"), use_container_width=True)

        cl = cdf.groupby("Client").agg(Contracts=("Contract ID", "count"), Total_Premium=("Annual Premium", "sum")).reset_index()
        cl = convert_cols(cl, ["Total_Premium"], cur)
        cl = cl.sort_values("Total_Premium", ascending=False).head(15)
        st.plotly_chart(bar_chart(cl, "Client", "Total_Premium", f"Top Clients — {country_sel} ({cur})"), use_container_width=True)

    with tab2:
        st.subheader(f"Plan Level — {country_sel}")
        prod_for_plan = st.selectbox("Select Product", list(PRODUCTS.keys()), key="plan_prod")
        pdf = cdf[cdf["Product"] == prod_for_plan]

        if pdf.empty:
            st.warning(f"No data for {prod_for_plan} in {country_sel}")
        else:
            pl = pdf.groupby("Plan")["Contract ID"].count().reset_index()
            pl.columns = ["Plan", "Contracts"]
            st.plotly_chart(bar_chart(pl, "Plan", "Contracts", f"Contracts by Plan — {prod_for_plan} ({country_sel})"), use_container_width=True)

            agg = make_summary(pdf, "Plan")
            agg = convert_cols(agg, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
            st.plotly_chart(bar_chart(melt_premiums(agg, "Plan"), "Plan", "Amount",
                                      f"Premium by Plan — {prod_for_plan} ({cur})", color="Metric"), use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 4: PRODUCT DRILL DOWN
# ─────────────────────────────────────────────
elif page == "📦 Product Drill Down":
    st.title("📦 Product Drill Down")
    prod_sel = st.selectbox("Select Product", list(PRODUCTS.keys()))
    pdf = df[df["Product"] == prod_sel]

    tab1, tab2 = st.tabs(["📊 Country Level (India & Singapore)", "📋 Plan Level"])

    with tab1:
        st.subheader(f"{PRODUCTS[prod_sel]['label']} — India & Singapore")
        isdf = pdf[pdf["Country"].isin(["India", "Singapore"])]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Contracts", f"{len(isdf):,}")
        col2.metric("Total Premium", fmt(convert(isdf['Annual Premium'].sum(), cur), cur))
        col3.metric("Paid", fmt(convert(isdf['Paid'].sum(), cur), cur))
        col4.metric("Outstanding", fmt(convert(isdf['Outstanding'].sum(), cur), cur))
        st.markdown("---")

        cc = isdf.groupby("Country")["Contract ID"].count().reset_index()
        cc.columns = ["Country", "Contracts"]
        st.plotly_chart(bar_chart(cc, "Country", "Contracts", f"Contracts — {prod_sel} (IN & SG)"), use_container_width=True)

        agg = make_summary(isdf, "Country")
        agg = convert_cols(agg, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
        st.plotly_chart(bar_chart(melt_premiums(agg, "Country"), "Country", "Amount",
                                  f"Premium — {prod_sel} ({cur})", color="Metric"), use_container_width=True)

        cl = isdf.groupby(["Country", "Client"]).agg(Contracts=("Contract ID", "count"), Total_Premium=("Annual Premium", "sum")).reset_index()
        cl = convert_cols(cl, ["Total_Premium"], cur)
        cl = cl.sort_values("Total_Premium", ascending=False).head(15)
        st.plotly_chart(bar_chart(cl, "Client", "Total_Premium", f"Top Clients — {prod_sel} ({cur})", color="Country"), use_container_width=True)

    with tab2:
        st.subheader(f"{PRODUCTS[prod_sel]['label']} — Plan Level")
        isdf = pdf[pdf["Country"].isin(["India", "Singapore"])]
        if isdf.empty:
            st.warning(f"No data for {prod_sel} in India/Singapore")
        else:
            cp = isdf.groupby(["Country", "Plan"]).agg(
                Contracts=("Contract ID", "count"), Total_Premium=("Annual Premium", "sum"),
                Paid=("Paid", "sum"), Outstanding=("Outstanding", "sum"), Target=("Target", "sum"),
            ).reset_index()
            cp = convert_cols(cp, ["Total_Premium", "Paid", "Outstanding", "Target"], cur)
            cpm = cp.melt(id_vars=["Country", "Plan", "Contracts"],
                          value_vars=["Total_Premium", "Paid", "Outstanding", "Target"],
                          var_name="Metric", value_name="Amount")
            fig = px.bar(cpm, x="Plan", y="Amount", color="Metric", barmode="group",
                         facet_col="Country", text_auto=".2s",
                         title=f"Premium by Plan — {prod_sel} ({cur})",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

            cpc = isdf.groupby(["Country", "Plan"])["Contract ID"].count().reset_index()
            cpc.columns = ["Country", "Plan", "Contracts"]
            st.plotly_chart(bar_chart(cpc, "Plan", "Contracts", f"Contracts by Plan — {prod_sel}", color="Country"), use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 5: RAW DATA
# ─────────────────────────────────────────────
elif page == "📋 Raw Data":
    st.title("📋 Contract Data")
    col1, col2, col3 = st.columns(3)
    f_product = col1.multiselect("Product", df["Product"].unique(), default=df["Product"].unique())
    f_country = col2.multiselect("Country", df["Country"].unique(), default=df["Country"].unique())
    f_type = col3.multiselect("Type", df["Type"].unique(), default=df["Type"].unique())

    filtered = df[(df["Product"].isin(f_product)) & (df["Country"].isin(f_country)) & (df["Type"].isin(f_type))]
    st.dataframe(filtered, use_container_width=True, height=600)
    st.caption(f"Showing {len(filtered):,} of {len(df):,} contracts")
    st.download_button("📥 Download CSV", filtered.to_csv(index=False), "contracts.csv", "text/csv")
