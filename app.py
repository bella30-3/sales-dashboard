import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import numpy as np

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
            "Singapore": ["Essential", "Comprehensive", "Elite"],
            "Thailand": ["Basic", "Advanced", "Premium"],
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

# Flatten for backward compatibility
CLIENTS = list(set(c for p in CLIENTS_BY_PRODUCT_COUNTRY.values() for cs in p.values() for c in cs))
TYPES = ["Individual", "Corporate"]
TRAN_TYPES = ["Inst", "Single"]


def get_client(product, country):
    """Pick a random client for the given product+country."""
    clients = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {}).get(country, [])
    if not clients:
        # Fallback: pick from any country for that product
        all_pc = CLIENTS_BY_PRODUCT_COUNTRY.get(product, {})
        clients = [c for cs in all_pc.values() for c in cs]
    return random.choice(clients) if clients else "Unknown"


def generate_data(n=800):
    """Generate dummy contract data."""
    rows = []
    for i in range(n):
        prod = random.choice(list(PRODUCTS.keys()))
        # Care Aqua can also be Europe
        if prod == "Care Aqua" and random.random() < 0.2:
            country = "Europe"
        else:
            country = random.choice([c for c in COUNTRIES.keys() if c != "Europe"])
        region = COUNTRIES[country]
        plan = random.choice(PRODUCTS[prod]["plans"].get(country, PRODUCTS[prod]["plans"][list(PRODUCTS[prod]["plans"].keys())[0]]))
        ctype = random.choice(TYPES)
        client = get_client(prod, country)
        trantype = random.choice(TRAN_TYPES)
        annual_premium = random.randint(500, 25000)
        paid = random.randint(0, annual_premium)
        outstanding = annual_premium - paid
        inst_count = random.randint(1, 12) if trantype == "Inst" else 1
        start = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 500))
        end = start + timedelta(days=365)
        target = annual_premium * random.uniform(1.1, 1.5)

        rows.append({
            "Contract ID": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(10000,99999)}",
            "Type": ctype,
            "Client": client,
            "Product": prod,
            "Product Label": PRODUCTS[prod]["label"],
            "Plan": plan,
            "Region": region,
            "Country": country,
            "Annual Premium": annual_premium,
            "Paid": paid,
            "Outstanding": outstanding,
            "Target": round(target),
            "Trantype": trantype,
            "Installment Count": inst_count,
            "Start Date": start.strftime("%Y-%m-%d"),
            "End Date": end.strftime("%Y-%m-%d"),
        })
    return pd.DataFrame(rows)


@st.cache_data
def load_data():
    return generate_data(800)


df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("📊 Sales Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🌍 Overall Product (World)",
    "🗺️ Region Drill Down",
    "🏳️ Country Drill Down",
    "📦 Product Drill Down",
    "📋 Raw Data",
])

st.sidebar.markdown("---")
st.sidebar.caption(f"Total Contracts: **{len(df):,}**")
st.sidebar.caption(f"Total Premium: **${df['Annual Premium'].sum():,.0f}**")

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
def metric_bar(df_grouped, x, y, title, color=None, barmode="group"):
    """Create a bar chart with consistent styling."""
    fig = px.bar(
        df_grouped, x=x, y=y, color=color,
        title=title, barmode=barmode,
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(
        height=450,
        title_font_size=16,
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(textposition="outside")
    return fig


def make_summary(df_in, group_col, label_col=None):
    """Aggregate contracts count + premium metrics."""
    agg = df_in.groupby(group_col).agg(
        Contracts=("Contract ID", "count"),
        Total_Premium=("Annual Premium", "sum"),
        Paid=("Paid", "sum"),
        Outstanding=("Outstanding", "sum"),
        Target=("Target", "sum"),
    ).reset_index()
    return agg


def melt_premiums(agg, id_col):
    """Melt premium columns for grouped bar chart."""
    return agg.melt(
        id_vars=[id_col, "Contracts"],
        value_vars=["Total_Premium", "Paid", "Outstanding", "Target"],
        var_name="Metric",
        value_name="Amount",
    )

# ─────────────────────────────────────────────
# PAGE 1: OVERALL PRODUCT (WORLD)
# ─────────────────────────────────────────────
if page == "🌍 Overall Product (World)":
    st.title("🌍 Overall Product Performance — Worldwide")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Contracts", f"{len(df):,}")
    col2.metric("Total Premium", f"${df['Annual Premium'].sum():,.0f}")
    col3.metric("Total Paid", f"${df['Paid'].sum():,.0f}")
    col4.metric("Outstanding", f"${df['Outstanding'].sum():,.0f}")

    st.markdown("---")

    # Contracts count by product
    prod_counts = df.groupby("Product Label")["Contract ID"].count().reset_index()
    prod_counts.columns = ["Product", "Contracts"]
    fig1 = metric_bar(prod_counts, "Product", "Contracts", "Contract Count by Product")
    st.plotly_chart(fig1, use_container_width=True)

    # Premium breakdown by product
    agg = make_summary(df, "Product Label", "Product Label")
    agg.rename(columns={"Product Label": "Product"}, inplace=True)
    melted = melt_premiums(agg, "Product")
    fig2 = metric_bar(melted, "Product", "Amount", "Premium Breakdown by Product", color="Metric")
    st.plotly_chart(fig2, use_container_width=True)

    # Contracts count by Product + Region
    prod_reg = df.groupby(["Product Label", "Region"])["Contract ID"].count().reset_index()
    prod_reg.columns = ["Product", "Region", "Contracts"]
    fig3 = metric_bar(prod_reg, "Product", "Contracts", "Contract Count by Product & Region", color="Region")
    st.plotly_chart(fig3, use_container_width=True)

    # Premium by Product + Region
    pr = df.groupby(["Product Label", "Region"]).agg(
        Total_Premium=("Annual Premium", "sum"),
        Paid=("Paid", "sum"),
        Outstanding=("Outstanding", "sum"),
        Target=("Target", "sum"),
    ).reset_index()
    pr.rename(columns={"Product Label": "Product"}, inplace=True)
    pr_melted = pr.melt(id_vars=["Product", "Region"], value_vars=["Total_Premium", "Paid", "Outstanding", "Target"], var_name="Metric", value_name="Amount")
    fig4 = px.bar(pr_melted, x="Product", y="Amount", color="Metric", barmode="group",
                  facet_row="Region", text_auto=".2s",
                  title="Premium Breakdown by Product & Region",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig4.update_layout(height=600, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 2: REGION DRILL DOWN
# ─────────────────────────────────────────────
elif page == "🗺️ Region Drill Down":
    st.title("🗺️ Region Drill Down")

    region_sel = st.selectbox("Select Region", REGIONS)
    rdf = df[df["Region"] == region_sel]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Contracts", f"{len(rdf):,}")
    col2.metric("Total Premium", f"${rdf['Annual Premium'].sum():,.0f}")
    col3.metric("Paid", f"${rdf['Paid'].sum():,.0f}")
    col4.metric("Outstanding", f"${rdf['Outstanding'].sum():,.0f}")

    st.markdown("---")

    # Contracts by Product in Region
    rp = rdf.groupby("Product Label")["Contract ID"].count().reset_index()
    rp.columns = ["Product", "Contracts"]
    fig1 = metric_bar(rp, "Product", "Contracts", f"Contract Count by Product — {region_sel}")
    st.plotly_chart(fig1, use_container_width=True)

    # Premium breakdown by Product in Region
    agg = make_summary(rdf, "Product Label")
    agg.rename(columns={"Product Label": "Product"}, inplace=True)
    melted = melt_premiums(agg, "Product")
    fig2 = metric_bar(melted, "Product", "Amount", f"Premium Breakdown by Product — {region_sel}", color="Metric")
    st.plotly_chart(fig2, use_container_width=True)

    # By Country in Region
    rc = rdf.groupby("Country").agg(
        Contracts=("Contract ID", "count"),
        Total_Premium=("Annual Premium", "sum"),
        Paid=("Paid", "sum"),
        Outstanding=("Outstanding", "sum"),
        Target=("Target", "sum"),
    ).reset_index()
    melted_c = rc.melt(id_vars=["Country", "Contracts"], value_vars=["Total_Premium", "Paid", "Outstanding", "Target"], var_name="Metric", value_name="Amount")
    fig3 = metric_bar(melted_c, "Country", "Amount", f"Premium by Country — {region_sel}", color="Metric")
    st.plotly_chart(fig3, use_container_width=True)

    # Contracts by Country + Product
    cp = rdf.groupby(["Country", "Product Label"])["Contract ID"].count().reset_index()
    cp.columns = ["Country", "Product", "Contracts"]
    fig4 = metric_bar(cp, "Country", "Contracts", f"Contract Count by Country & Product — {region_sel}", color="Product")
    st.plotly_chart(fig4, use_container_width=True)

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
        col2.metric("Total Premium", f"${cdf['Annual Premium'].sum():,.0f}")
        col3.metric("Paid", f"${cdf['Paid'].sum():,.0f}")
        col4.metric("Outstanding", f"${cdf['Outstanding'].sum():,.0f}")

        st.markdown("---")

        # Contract count by Product
        cp = cdf.groupby("Product Label")["Contract ID"].count().reset_index()
        cp.columns = ["Product", "Contracts"]
        fig1 = metric_bar(cp, "Product", "Contracts", f"Contract Count by Product — {country_sel}")
        st.plotly_chart(fig1, use_container_width=True)

        # Premium by Product
        agg = make_summary(cdf, "Product Label")
        agg.rename(columns={"Product Label": "Product"}, inplace=True)
        melted = melt_premiums(agg, "Product")
        fig2 = metric_bar(melted, "Product", "Amount", f"Premium Breakdown — {country_sel}", color="Metric")
        st.plotly_chart(fig2, use_container_width=True)

        # By Client
        cl = cdf.groupby("Client").agg(
            Contracts=("Contract ID", "count"),
            Total_Premium=("Annual Premium", "sum"),
        ).reset_index().sort_values("Total_Premium", ascending=False).head(15)
        fig3 = metric_bar(cl, "Client", "Total_Premium", f"Top Clients by Premium — {country_sel}")
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader(f"Plan Level Breakdown — {country_sel}")

        prod_for_plan = st.selectbox("Select Product", list(PRODUCTS.keys()), key="plan_prod")
        pdf = cdf[cdf["Product"] == prod_for_plan]

        if pdf.empty:
            st.warning(f"No data for {prod_for_plan} in {country_sel}")
        else:
            # Contract count by Plan
            pl = pdf.groupby("Plan")["Contract ID"].count().reset_index()
            pl.columns = ["Plan", "Contracts"]
            fig1 = metric_bar(pl, "Plan", "Contracts", f"Contract Count by Plan — {prod_for_plan} ({country_sel})")
            st.plotly_chart(fig1, use_container_width=True)

            # Premium by Plan
            agg = make_summary(pdf, "Plan")
            melted = melt_premiums(agg, "Plan")
            fig2 = metric_bar(melted, "Plan", "Amount", f"Premium Breakdown by Plan — {prod_for_plan} ({country_sel})", color="Metric")
            st.plotly_chart(fig2, use_container_width=True)

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
        col2.metric("Total Premium", f"${isdf['Annual Premium'].sum():,.0f}")
        col3.metric("Paid", f"${isdf['Paid'].sum():,.0f}")
        col4.metric("Outstanding", f"${isdf['Outstanding'].sum():,.0f}")

        st.markdown("---")

        # Contract count by Country
        cc = isdf.groupby("Country")["Contract ID"].count().reset_index()
        cc.columns = ["Country", "Contracts"]
        fig1 = metric_bar(cc, "Country", "Contracts", f"Contract Count — {prod_sel} (India & Singapore)")
        st.plotly_chart(fig1, use_container_width=True)

        # Premium by Country
        agg = make_summary(isdf, "Country")
        melted = melt_premiums(agg, "Country")
        fig2 = metric_bar(melted, "Country", "Amount", f"Premium Breakdown — {prod_sel} (India & Singapore)", color="Metric")
        st.plotly_chart(fig2, use_container_width=True)

        # By Client
        cl = isdf.groupby(["Country", "Client"]).agg(
            Contracts=("Contract ID", "count"),
            Total_Premium=("Annual Premium", "sum"),
        ).reset_index().sort_values("Total_Premium", ascending=False).head(15)
        fig3 = metric_bar(cl, "Client", "Total_Premium", f"Top Clients — {prod_sel}", color="Country")
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader(f"{PRODUCTS[prod_sel]['label']} — Plan Level (India & Singapore)")

        isdf = pdf[pdf["Country"].isin(["India", "Singapore"])]

        if isdf.empty:
            st.warning(f"No data for {prod_sel} in India/Singapore")
        else:
            # By Country + Plan
            cp = isdf.groupby(["Country", "Plan"]).agg(
                Contracts=("Contract ID", "count"),
                Total_Premium=("Annual Premium", "sum"),
                Paid=("Paid", "sum"),
                Outstanding=("Outstanding", "sum"),
                Target=("Target", "sum"),
            ).reset_index()
            melted = cp.melt(id_vars=["Country", "Plan", "Contracts"], value_vars=["Total_Premium", "Paid", "Outstanding", "Target"], var_name="Metric", value_name="Amount")

            fig1 = px.bar(melted, x="Plan", y="Amount", color="Metric", barmode="group",
                          facet_col="Country", text_auto=".2s",
                          title=f"Premium by Plan — {prod_sel} (India & Singapore)",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig1.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

            # Contract count by Plan + Country
            cp_count = isdf.groupby(["Country", "Plan"])["Contract ID"].count().reset_index()
            cp_count.columns = ["Country", "Plan", "Contracts"]
            fig2 = metric_bar(cp_count, "Plan", "Contracts", f"Contract Count by Plan — {prod_sel}", color="Country")
            st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 5: RAW DATA
# ─────────────────────────────────────────────
elif page == "📋 Raw Data":
    st.title("📋 Contract Data")

    col1, col2, col3 = st.columns(3)
    f_product = col1.multiselect("Product", df["Product"].unique(), default=df["Product"].unique())
    f_country = col2.multiselect("Country", df["Country"].unique(), default=df["Country"].unique())
    f_type = col3.multiselect("Type", df["Type"].unique(), default=df["Type"].unique())

    filtered = df[
        (df["Product"].isin(f_product)) &
        (df["Country"].isin(f_country)) &
        (df["Type"].isin(f_type))
    ]

    st.dataframe(filtered, use_container_width=True, height=600)
    st.caption(f"Showing {len(filtered):,} of {len(df):,} contracts")

    # Download
    csv = filtered.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "contracts.csv", "text/csv")
