import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import numpy as np
from currency import convert, fmt, currency_selector

st.set_page_config(page_title="Policy Analysis", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
# EV POLICY DATA
# ─────────────────────────────────────────────
EV_HEALTH_STATES = ["Healthy", "Fair", "Poor"]
EV_BRANDS = ["Mahindra", "BYD", "Porsche", "Subaru", "Hyundai", "Cycle & Carriage"]
EV_COUNTRIES = ["India", "Singapore", "Thailand"]


SGD_TO_USD = 1.35
EV_MONTHLY_TARGET_USD = 15000 / SGD_TO_USD  # ~15k SGD/month
IPI_MONTHLY_TARGET_USD = 20000 / SGD_TO_USD  # ~20k SGD/month

def generate_ev_policies():
    """Generate monthly EV policy data from Jan 2023 to today.
    Target: ~15k SGD/month in premiums.
    """
    rows = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    current = start_date

    while current <= end_date:
        year, month = current.year, current.month
        # Seasonal variation
        seasonal = 1.0
        if month in (10, 11, 12):
            seasonal = random.uniform(1.1, 1.3)
        elif month in (1, 2):
            seasonal = random.uniform(0.75, 0.9)
        else:
            seasonal = random.uniform(0.9, 1.1)

        years_elapsed = (current - datetime(2023, 1, 1)).days / 365.25
        growth = (1.0 + 0.10) ** years_elapsed
        anomaly = 1.0
        if random.random() < 0.1:
            anomaly = random.uniform(0.5, 0.75)
        elif random.random() < 0.08:
            anomaly = random.uniform(1.3, 1.5)

        monthly_budget = EV_MONTHLY_TARGET_USD * seasonal * growth * anomaly
        n_policies = max(3, int(monthly_budget / 1000 * random.uniform(0.6, 1.4)))
        weights = np.random.dirichlet(np.ones(n_policies) * 0.5)
        premiums = weights * monthly_budget

        days_in_month = 28 if month == 2 else (30 if month in (4, 6, 9, 11) else 31)

        for i, premium in enumerate(premiums):
            premium = max(200, round(premium))
            country = random.choice(EV_COUNTRIES)
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

            start_day = random.randint(1, min(days_in_month, 28))
            start = datetime(year, month, start_day)
            end = start + timedelta(days=365)

            rows.append({
                "Policy ID": f"EV-{random.randint(10000,99999)}",
                "Country": country,
                "Brand": brand,
                "Health State": health,
                "Vehicle Age (Years)": age,
                "KM Driven": km,
                "Annual Premium": premium,
                "Claims": claim_count,
                "Claim Amount": claim_amount,
                "Year": year, "Month": month,
                "YearMonth": f"{year}-{month:02d}",
                "Start Date": start.strftime("%Y-%m-%d"),
                "End Date": end.strftime("%Y-%m-%d"),
            })

        if month == 12:
            current = datetime(year + 1, 1, 1)
        else:
            current = datetime(year, month + 1, 1)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# IPI POLICY DATA
# ─────────────────────────────────────────────
IPI_PLANS = {
    "DBS Staff 2000": {"premium": 200, "type": "Individual", "insurer": "DBS", "sum_insured": 2000},
    "DBS Staff 5000": {"premium": 400, "type": "Individual", "insurer": "DBS", "sum_insured": 5000},
    "OCBC GA Mandatory 3M A": {"premium": 75, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 15000},
    "OCBC GA Mandatory 3M B": {"premium": 100, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 25000},
    "OCBC GA Mandatory 3M C": {"premium": 150, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 40000},
    "OCBC GA Mandatory 3M 5": {"premium": 150, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 50000},
    "OCBC GA 12M A": {"premium": 500, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 50000},
    "OCBC GA 12M B": {"premium": 1000, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 100000},
    "OCBC GA 12M C": {"premium": 1500, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 150000},
    "OCBC GA 12M 5": {"premium": 1500, "type": "Corporate", "insurer": "OCBC (GE)", "sum_insured": 200000},
}


def generate_ipi_policies():
    """Generate monthly IPI policy data from Jan 2023 to today.
    Target: ~20k SGD/month in premiums.
    """
    rows = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    current = start_date

    while current <= end_date:
        year, month = current.year, current.month
        # Seasonal variation
        seasonal = 1.0
        if month in (10, 11, 12):
            seasonal = random.uniform(1.1, 1.3)
        elif month in (1, 2):
            seasonal = random.uniform(0.75, 0.9)
        else:
            seasonal = random.uniform(0.9, 1.1)

        years_elapsed = (current - datetime(2023, 1, 1)).days / 365.25
        growth = (1.0 + 0.10) ** years_elapsed
        anomaly = 1.0
        if random.random() < 0.1:
            anomaly = random.uniform(0.5, 0.75)
        elif random.random() < 0.08:
            anomaly = random.uniform(1.3, 1.5)

        monthly_budget = IPI_MONTHLY_TARGET_USD * seasonal * growth * anomaly
        n_policies = max(3, int(monthly_budget / 500 * random.uniform(0.6, 1.4)))
        weights = np.random.dirichlet(np.ones(n_policies) * 0.5)
        premiums = weights * monthly_budget

        days_in_month = 28 if month == 2 else (30 if month in (4, 6, 9, 11) else 31)

        for i, premium in enumerate(premiums):
            premium = max(50, round(premium))
            plan_name = random.choice(list(IPI_PLANS.keys()))
            plan = IPI_PLANS[plan_name]
            country = random.choice(["India", "Singapore", "Thailand"])
            renewed = random.random() < (0.85 if plan["type"] == "Corporate" else 0.65)
            lives = random.randint(5, 500) if plan["type"] == "Corporate" else 1

            start_day = random.randint(1, min(days_in_month, 28))
            start = datetime(year, month, start_day)
            end = start + timedelta(days=365)

            rows.append({
                "Policy ID": f"IPI-{random.randint(10000,99999)}",
                "Country": country,
                "Plan": plan_name,
                "Type": plan["type"],
                "Insurer": plan["insurer"],
                "Premium": round(premium),
                "Sum Insured": plan["sum_insured"],
                "Renewed": renewed,
                "Lives Insured": lives,
                "Year": year, "Month": month,
                "YearMonth": f"{year}-{month:02d}",
                "Start Date": start.strftime("%Y-%m-%d"),
                "End Date": end.strftime("%Y-%m-%d"),
            })

        if month == 12:
            current = datetime(year + 1, 1, 1)
        else:
            current = datetime(year, month + 1, 1)

    return pd.DataFrame(rows)


@st.cache_data
def load_data():
    return generate_ev_policies(), generate_ipi_policies()


ev_df, ipi_df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("📋 Policy Analysis")
st.sidebar.markdown("---")

cur = currency_selector("Display Currency", "pa_currency")

page = st.sidebar.radio("Navigate", [
    "🚗 EV — State of Health",
    "🚗 EV — Age Analysis",
    "🚗 EV — KM Analysis",
    "🔄 EV — Health vs KM",
    "🔄 EV — Health vs Age",
    "🛡️ IPI — Sum Insured by Plan",
    "🛡️ IPI — Renewal Rate",
    "🛡️ IPI — Lives Insured",
])

st.sidebar.markdown("---")
st.sidebar.caption(f"EV Policies: **{len(ev_df):,}**")
st.sidebar.caption(f"IPI Policies: **{len(ipi_df):,}**")


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
def bar(data, x, y, title, color=None, barmode="group", text_auto=True):
    fig = px.bar(data, x=x, y=y, color=color, title=title, barmode=barmode,
                 text_auto=".2s" if text_auto else True,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=450, title_font_size=16, xaxis_title="", yaxis_title="",
                      legend_title="", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_traces(textposition="outside")
    return fig


# ─────────────────────────────────────────────
# EV — STATE OF HEALTH
# ─────────────────────────────────────────────
if page == "🚗 EV — State of Health":
    st.title("🚗 EV Policies — State of Health")

    country_filter = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="health_c")
    df = ev_df[ev_df["Country"].isin(country_filter)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Policies", f"{len(df):,}")
    col2.metric("Healthy", f"{len(df[df['Health State']=='Healthy']):,}")
    col3.metric("Poor", f"{len(df[df['Health State']=='Poor']):,}")

    st.markdown("---")

    # Count by health state
    hc = df.groupby("Health State")["Policy ID"].count().reset_index()
    hc.columns = ["Health State", "Policies"]
    fig1 = bar(hc, "Health State", "Policies", "Policy Count by State of Health")
    st.plotly_chart(fig1, use_container_width=True)

    # By health state + country
    hcc = df.groupby(["Health State", "Country"])["Policy ID"].count().reset_index()
    hcc.columns = ["Health State", "Country", "Policies"]
    fig2 = bar(hcc, "Health State", "Policies", "Health State by Country", color="Country")
    st.plotly_chart(fig2, use_container_width=True)

    # Avg premium by health state
    hp = df.groupby("Health State")["Annual Premium"].mean().reset_index()
    hp.columns = ["Health State", "Avg Premium"]
    hp["Avg Premium"] = hp["Avg Premium"].apply(lambda v: convert(v, cur))
    fig3 = bar(hp, "Health State", "Avg Premium", f"Average Premium by Health State ({cur})")
    st.plotly_chart(fig3, use_container_width=True)

    # Claims by health state
    hc_claims = df.groupby("Health State").agg(Claims=("Claims", "sum"), Amount=("Claim Amount", "sum")).reset_index()
    hc_claims["Amount"] = hc_claims["Amount"].apply(lambda v: convert(v, cur))
    hc_melted = hc_claims.melt(id_vars="Health State", var_name="Metric", value_name="Value")
    fig4 = bar(hc_melted, "Health State", "Value", f"Claims by Health State ({cur})", color="Metric")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# EV — AGE ANALYSIS
# ─────────────────────────────────────────────
elif page == "🚗 EV — Age Analysis":
    st.title("🚗 EV Policies — Vehicle Age")

    country_filter = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="age_c")
    df = ev_df[ev_df["Country"].isin(country_filter)]

    # Age brackets
    df = df.copy()
    df["Age Bracket"] = pd.cut(df["Vehicle Age (Years)"], bins=[0, 3, 5, 10, 15],
                                labels=["1-3 yrs", "4-5 yrs", "6-10 yrs", "11-15 yrs"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Policies", f"{len(df):,}")
    col2.metric("Avg Vehicle Age", f"{df['Vehicle Age (Years)'].mean():.1f} yrs")
    col3.metric("Avg KM", f"{df['KM Driven'].mean():,.0f}")

    st.markdown("---")

    # Count by age bracket
    ac = df.groupby("Age Bracket", observed=True)["Policy ID"].count().reset_index()
    ac.columns = ["Age Bracket", "Policies"]
    fig1 = bar(ac, "Age Bracket", "Policies", "Policy Count by Vehicle Age")
    st.plotly_chart(fig1, use_container_width=True)

    # By age + country
    acc = df.groupby(["Age Bracket", "Country"], observed=True)["Policy ID"].count().reset_index()
    acc.columns = ["Age Bracket", "Country", "Policies"]
    fig2 = bar(acc, "Age Bracket", "Policies", "Vehicle Age by Country", color="Country")
    st.plotly_chart(fig2, use_container_width=True)

    # Avg premium by age
    ap = df.groupby("Age Bracket", observed=True)["Annual Premium"].mean().reset_index()
    ap.columns = ["Age Bracket", "Avg Premium"]
    ap["Avg Premium"] = ap["Avg Premium"].apply(lambda v: convert(v, cur))
    fig3 = bar(ap, "Age Bracket", "Avg Premium", f"Average Premium by Vehicle Age ({cur})")
    st.plotly_chart(fig3, use_container_width=True)

    # Claims by age
    ac_claims = df.groupby("Age Bracket", observed=True).agg(Claims=("Claims", "sum"), Amount=("Claim Amount", "sum")).reset_index()
    ac_claims["Amount"] = ac_claims["Amount"].apply(lambda v: convert(v, cur))
    ac_melted = ac_claims.melt(id_vars="Age Bracket", var_name="Metric", value_name="Value")
    fig4 = bar(ac_melted, "Age Bracket", "Value", f"Claims by Vehicle Age ({cur})", color="Metric")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# EV — KM ANALYSIS
# ─────────────────────────────────────────────
elif page == "🚗 EV — KM Analysis":
    st.title("🚗 EV Policies — KM Driven")

    country_filter = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="km_c")
    df = ev_df[ev_df["Country"].isin(country_filter)].copy()

    df["KM Bracket"] = pd.cut(df["KM Driven"], bins=[0, 25000, 50000, 100000, 150000, 250000],
                               labels=["0-25K", "25-50K", "50-100K", "100-150K", "150K+"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Policies", f"{len(df):,}")
    col2.metric("Avg KM", f"{df['KM Driven'].mean():,.0f}")
    col3.metric("Max KM", f"{df['KM Driven'].max():,.0f}")

    st.markdown("---")

    # Count by KM bracket
    kc = df.groupby("KM Bracket", observed=True)["Policy ID"].count().reset_index()
    kc.columns = ["KM Bracket", "Policies"]
    fig1 = bar(kc, "KM Bracket", "Policies", "Policy Count by KM Driven")
    st.plotly_chart(fig1, use_container_width=True)

    # By KM + country
    kcc = df.groupby(["KM Bracket", "Country"], observed=True)["Policy ID"].count().reset_index()
    kcc.columns = ["KM Bracket", "Country", "Policies"]
    fig2 = bar(kcc, "KM Bracket", "Policies", "KM Driven by Country", color="Country")
    st.plotly_chart(fig2, use_container_width=True)

    # Avg premium by KM
    kp = df.groupby("KM Bracket", observed=True)["Annual Premium"].mean().reset_index()
    kp.columns = ["KM Bracket", "Avg Premium"]
    kp["Avg Premium"] = kp["Avg Premium"].apply(lambda v: convert(v, cur))
    fig3 = bar(kp, "KM Bracket", "Avg Premium", f"Average Premium by KM Driven ({cur})")
    st.plotly_chart(fig3, use_container_width=True)

    # Health distribution by KM
    kh = df.groupby(["KM Bracket", "Health State"], observed=True)["Policy ID"].count().reset_index()
    kh.columns = ["KM Bracket", "Health State", "Policies"]
    fig4 = bar(kh, "KM Bracket", "Policies", "Health State by KM Driven", color="Health State")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# EV — HEALTH vs KM
# ─────────────────────────────────────────────
elif page == "🔄 EV — Health vs KM":
    st.title("🔄 EV — State of Health vs KM Driven")

    country_filter = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="hkm_c")
    df = ev_df[ev_df["Country"].isin(country_filter)].copy()

    df["KM Bracket"] = pd.cut(df["KM Driven"], bins=[0, 25000, 50000, 100000, 150000, 250000],
                               labels=["0-25K", "25-50K", "50-100K", "100-150K", "150K+"])

    st.markdown("---")

    # Grouped bar: Health State vs KM Bracket
    cross = df.groupby(["KM Bracket", "Health State"], observed=True)["Policy ID"].count().reset_index()
    cross.columns = ["KM Bracket", "Health State", "Policies"]
    fig1 = bar(cross, "KM Bracket", "Policies", "Health State Distribution by KM Bracket", color="Health State")
    st.plotly_chart(fig1, use_container_width=True)

    # 100% stacked
    cross_pct = cross.copy()
    totals = cross_pct.groupby("KM Bracket")["Policies"].transform("sum")
    cross_pct["Percentage"] = cross_pct["Policies"] / totals * 100
    fig2 = px.bar(cross_pct, x="KM Bracket", y="Percentage", color="Health State",
                  title="Health State % by KM Bracket", barmode="stack",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_layout(height=450, plot_bgcolor="rgba(0,0,0,0)", yaxis_title="%")
    st.plotly_chart(fig2, use_container_width=True)

    # Scatter: KM vs Premium colored by Health
    fig3 = px.scatter(df, x="KM Driven", y="Annual Premium", color="Health State",
                      title=f"KM vs Premium by Health State ({cur})", opacity=0.6,
                      color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

    # Avg claims by Health + KM
    claims = df.groupby(["KM Bracket", "Health State"], observed=True)["Claim Amount"].mean().reset_index()
    claims.columns = ["KM Bracket", "Health State", "Avg Claim"]
    claims["Avg Claim"] = claims["Avg Claim"].apply(lambda v: convert(v, cur))
    fig4 = bar(claims, "KM Bracket", "Avg Claim", f"Average Claim Amount by KM & Health ({cur})", color="Health State")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# EV — HEALTH vs AGE
# ─────────────────────────────────────────────
elif page == "🔄 EV — Health vs Age":
    st.title("🔄 EV — State of Health vs Vehicle Age")

    country_filter = st.multiselect("Country", EV_COUNTRIES, default=EV_COUNTRIES, key="hage_c")
    df = ev_df[ev_df["Country"].isin(country_filter)].copy()

    df["Age Bracket"] = pd.cut(df["Vehicle Age (Years)"], bins=[0, 3, 5, 10, 15],
                                labels=["1-3 yrs", "4-5 yrs", "6-10 yrs", "11-15 yrs"])

    st.markdown("---")

    # Grouped bar: Health State vs Age Bracket
    cross = df.groupby(["Age Bracket", "Health State"], observed=True)["Policy ID"].count().reset_index()
    cross.columns = ["Age Bracket", "Health State", "Policies"]
    fig1 = bar(cross, "Age Bracket", "Policies", "Health State Distribution by Vehicle Age", color="Health State")
    st.plotly_chart(fig1, use_container_width=True)

    # 100% stacked
    cross_pct = cross.copy()
    totals = cross_pct.groupby("Age Bracket")["Policies"].transform("sum")
    cross_pct["Percentage"] = cross_pct["Policies"] / totals * 100
    fig2 = px.bar(cross_pct, x="Age Bracket", y="Percentage", color="Health State",
                  title="Health State % by Vehicle Age", barmode="stack",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_layout(height=450, plot_bgcolor="rgba(0,0,0,0)", yaxis_title="%")
    st.plotly_chart(fig2, use_container_width=True)

    # Scatter: Age vs Premium colored by Health
    fig3 = px.scatter(df, x="Vehicle Age (Years)", y="Annual Premium", color="Health State",
                      title=f"Vehicle Age vs Premium by Health State ({cur})", opacity=0.6,
                      color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

    # Avg claims by Health + Age
    claims = df.groupby(["Age Bracket", "Health State"], observed=True)["Claim Amount"].mean().reset_index()
    claims.columns = ["Age Bracket", "Health State", "Avg Claim"]
    claims["Avg Claim"] = claims["Avg Claim"].apply(lambda v: convert(v, cur))
    fig4 = bar(claims, "Age Bracket", "Avg Claim", f"Average Claim Amount by Age & Health ({cur})", color="Health State")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# IPI — SUM INSURED BY PLAN
# ─────────────────────────────────────────────
elif page == "🛡️ IPI — Sum Insured by Plan":
    st.title("🛡️ IPI — Sum Insured by Plan Type")

    country_filter = st.multiselect("Country", ["India", "Singapore", "Thailand"], default=["India", "Singapore", "Thailand"], key="si_c")
    df = ipi_df[ipi_df["Country"].isin(country_filter)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Policies", f"{len(df):,}")
    col2.metric("Total Sum Insured", fmt(convert(df['Sum Insured'].sum(), cur), cur))
    col3.metric("Avg Sum Insured", fmt(convert(df['Sum Insured'].mean(), cur), cur))

    st.markdown("---")

    # Sum insured by plan
    si = df.groupby("Plan").agg(
        Policies=("Policy ID", "count"),
        Sum_Insured=("Sum Insured", "sum"),
    ).reset_index().sort_values("Sum_Insured", ascending=False)
    si["Sum_Insured"] = si["Sum_Insured"].apply(lambda v: convert(v, cur))
    fig1 = bar(si, "Plan", "Sum_Insured", f"Total Sum Insured by Plan ({cur})")
    st.plotly_chart(fig1, use_container_width=True)

    # Sum insured by plan + country
    sic = df.groupby(["Plan", "Country"]).agg(Sum_Insured=("Sum Insured", "sum")).reset_index()
    sic["Sum_Insured"] = sic["Sum_Insured"].apply(lambda v: convert(v, cur))
    fig2 = px.bar(sic, x="Plan", y="Sum_Insured", color="Country", barmode="group",
                  title=f"Sum Insured by Plan & Country ({cur})", text_auto=".2s",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_layout(height=450, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

    # Avg sum insured by type (Individual vs Corporate)
    typ = df.groupby("Type")["Sum Insured"].mean().reset_index()
    typ.columns = ["Type", "Avg Sum Insured"]
    typ["Avg Sum Insured"] = typ["Avg Sum Insured"].apply(lambda v: convert(v, cur))
    fig3 = bar(typ, "Type", "Avg Sum Insured", f"Average Sum Insured by Type ({cur})")
    st.plotly_chart(fig3, use_container_width=True)

    # Policy count by plan
    pc = df.groupby("Plan")["Policy ID"].count().reset_index()
    pc.columns = ["Plan", "Policies"]
    fig4 = bar(pc, "Plan", "Policies", "Policy Count by Plan")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# IPI — RENEWAL RATE
# ─────────────────────────────────────────────
elif page == "🛡️ IPI — Renewal Rate":
    st.title("🛡️ IPI — Renewal Rate")

    country_filter = st.multiselect("Country", ["India", "Singapore", "Thailand"], default=["India", "Singapore", "Thailand"], key="rr_c")
    df = ipi_df[ipi_df["Country"].isin(country_filter)]

    col1, col2, col3 = st.columns(3)
    overall_rate = df["Renewed"].mean() * 100
    col1.metric("Overall Renewal Rate", f"{overall_rate:.1f}%")
    col2.metric("Renewed", f"{df['Renewed'].sum():,}")
    col3.metric("Not Renewed", f"{(~df['Renewed']).sum():,}")

    st.markdown("---")

    # By plan
    rr = df.groupby("Plan")["Renewed"].mean().reset_index()
    rr["Renewal Rate %"] = rr["Renewed"] * 100
    fig1 = bar(rr, "Plan", "Renewal Rate %", "Renewal Rate by Plan")
    st.plotly_chart(fig1, use_container_width=True)

    # By type
    rt = df.groupby("Type")["Renewed"].mean().reset_index()
    rt["Renewal Rate %"] = rt["Renewed"] * 100
    fig2 = bar(rt, "Type", "Renewal Rate %", "Renewal Rate by Type (Individual vs Corporate)")
    st.plotly_chart(fig2, use_container_width=True)

    # By country
    rc = df.groupby("Country")["Renewed"].mean().reset_index()
    rc["Renewal Rate %"] = rc["Renewed"] * 100
    fig3 = bar(rc, "Country", "Renewal Rate %", "Renewal Rate by Country")
    st.plotly_chart(fig3, use_container_width=True)

    # By plan + country
    rpc = df.groupby(["Plan", "Country"])["Renewed"].mean().reset_index()
    rpc["Renewal Rate %"] = rpc["Renewed"] * 100
    fig4 = px.bar(rpc, x="Plan", y="Renewal Rate %", color="Country", barmode="group",
                  title="Renewal Rate by Plan & Country", text_auto=".1f",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig4.update_layout(height=450, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# IPI — LIVES INSURED
# ─────────────────────────────────────────────
elif page == "🛡️ IPI — Lives Insured":
    st.title("🛡️ IPI — Number of Lives Insured")

    country_filter = st.multiselect("Country", ["India", "Singapore", "Thailand"], default=["India", "Singapore", "Thailand"], key="li_c")
    df = ipi_df[ipi_df["Country"].isin(country_filter)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Policies", f"{len(df):,}")
    col2.metric("Total Lives", f"{df['Lives Insured'].sum():,}")
    col3.metric("Avg Lives/Policy", f"{df['Lives Insured'].mean():.0f}")

    st.markdown("---")

    # By plan
    ll = df.groupby("Plan")["Lives Insured"].sum().reset_index().sort_values("Lives Insured", ascending=False)
    fig1 = bar(ll, "Plan", "Lives Insured", "Total Lives Insured by Plan")
    st.plotly_chart(fig1, use_container_width=True)

    # By type
    lt = df.groupby("Type")["Lives Insured"].agg(["sum", "mean"]).reset_index()
    lt.columns = ["Type", "Total Lives", "Avg Lives/Policy"]
    lt_melted = lt.melt(id_vars="Type", var_name="Metric", value_name="Value")
    fig2 = bar(lt_melted, "Type", "Value", "Lives Insured by Type", color="Metric")
    st.plotly_chart(fig2, use_container_width=True)

    # By country
    lc = df.groupby("Country")["Lives Insured"].sum().reset_index()
    fig3 = bar(lc, "Country", "Lives Insured", "Total Lives Insured by Country")
    st.plotly_chart(fig3, use_container_width=True)

    # By plan + country
    lpc = df.groupby(["Plan", "Country"])["Lives Insured"].sum().reset_index()
    fig4 = px.bar(lpc, x="Plan", y="Lives Insured", color="Country", barmode="group",
                  title="Lives Insured by Plan & Country", text_auto=".2s",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig4.update_layout(height=450, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)
