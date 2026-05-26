"""
Atelier 1 — Squelette de dashboard FinOps showback.
À compléter durant l'exercice 5.

Lancer : streamlit run app/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="FinOps Showback", layout="wide", page_icon="💰")

CUR_PATH = Path(__file__).parent.parent.parent / "ressources" / "datasets" / "cur_sample.csv"

ACCOUNT_LABELS = {
    "111111111111": "prod",
    "222222222222": "staging",
    "333333333333": "dev",
    "444444444444": "sandbox",
}


@st.cache_data
def load_data():
    df = pd.read_csv(CUR_PATH, parse_dates=["usage_date"])
    df["account_id"] = df["account_id"].astype(str)
    df["account_name"] = df["account_id"].map(ACCOUNT_LABELS)
    for col in [c for c in df.columns if c.startswith("tag_")]:
        df[col] = df[col].fillna("").astype(str)
    return df


df = load_data()

# ─── Header ─────────────────────────────────────────────────────────
st.title("💰 FinOps Showback Dashboard")
st.caption("Atelier 1 — données synthétiques, période de 90 jours")

# ─── Filtres ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    date_range = st.date_input(
        "Période",
        value=(df.usage_date.min().date(), df.usage_date.max().date()),
        min_value=df.usage_date.min().date(),
        max_value=df.usage_date.max().date(),
    )

with col2:
    teams = ["(toutes)"] + sorted(df.tag_team.replace("", "(non-taggé)").unique().tolist())
    team = st.selectbox("Équipe", teams)

with col3:
    accounts = ["(tous)"] + sorted(df.account_name.unique().tolist())
    account = st.selectbox("Compte", accounts)

# Appliquer les filtres
mask = (df.usage_date.dt.date >= date_range[0]) & (df.usage_date.dt.date <= date_range[1])
if team != "(toutes)":
    team_filter = "" if team == "(non-taggé)" else team
    mask &= df.tag_team == team_filter
if account != "(tous)":
    mask &= df.account_name == account
filtered = df[mask]

# ─── KPIs ───────────────────────────────────────────────────────────
st.markdown("### 📊 Indicateurs clés")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Coût total", f"${filtered.unblended_cost.sum():,.0f}")
k2.metric("Coût moyen / jour", f"${filtered.groupby('usage_date').unblended_cost.sum().mean():,.0f}")
k3.metric("Nombre de services", filtered.service.nunique())
k4.metric("Couverture tagging (équipe)", f"{(filtered.tag_team != '').mean() * 100:.1f}%")
# TODO Exercice 5 : ajouter un KPI "% couverture tagging" sophistiqué

# ─── Graphique tendance ─────────────────────────────────────────────
st.markdown("### 📈 Tendance journalière")
daily = filtered.groupby("usage_date").unblended_cost.sum().reset_index()
fig = px.line(daily, x="usage_date", y="unblended_cost",
              labels={"unblended_cost": "Coût ($)", "usage_date": "Date"})
st.plotly_chart(fig, use_container_width=True)

# ─── Tableau top usages ─────────────────────────────────────────────
st.markdown("### 🏆 Top 10 usages les plus coûteux")
top = (
    filtered.groupby(["service", "usage_type"]).unblended_cost.sum()
    .sort_values(ascending=False).head(10).reset_index()
)
st.dataframe(top, use_container_width=True)

# ─── TODO Exercice 5 ────────────────────────────────────────────────
st.markdown("---")
st.info(
    "🎯 **Exercice 5 — à compléter** :\n"
    "1. KPI de couverture tagging plus avancé (multi-dimensions)\n"
    "2. Comparaison budget vs réel (charger `budgets.json`)\n"
    "3. Alerte visuelle quand une équipe > 110% de son budget\n"
    "4. Bonus : forecast linéaire sur 30 jours"
)
