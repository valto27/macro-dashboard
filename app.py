import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

st.set_page_config(
    page_title="Macro Regime Dashboard",
    layout="wide")

from macro_data import fetch_fred_data, fetch_market_data
from indicators import compute_all_indicators
from hmm_model import run_hmm_pipeline
from charts import plot_regimes, plot_yield_curve, plot_fci, plot_heatmap

api_key = st.secrets.get("FRED_API_KEY", os.environ.get("FRED_API_KEY"))

@st.cache_data(ttl=3600)
def load_fred_data(api_key):
    fred_df = fetch_fred_data(api_key)
    return fred_df


@st.cache_data(ttl=3600)
def load_market_data():
    market_df = fetch_market_data()
    return market_df

@st.cache_data(ttl=86400)
def load_indicators(fred_df, market_df):
    indicators_df = compute_all_indicators(market_df, fred_df)
    return indicators_df

@st.cache_data(ttl=86400)
def load_regimes(indicators_df, fred_df, market_df):
    hidden_states_df, probabilities_df, model, features_df = run_hmm_pipeline(indicators_df, fred_df, market_df)
    return hidden_states_df, probabilities_df

fred_df = load_fred_data(api_key)
market_df = load_market_data()
indicators_df = load_indicators(fred_df, market_df)
hidden_states_df, probabilities_df = load_regimes(indicators_df, fred_df, market_df)

st.sidebar.title("Navigazione")
sezione = st.sidebar.radio("Section", [
    "Current Regime",
    "Yield Curve",
    "Financial Conditions",
    "Credit",
    "Markets",
    "Heatmap"])

if sezione == "Current Regime":
    st.title("Current Regime")
    fig = plot_regimes(hidden_states_df, market_df)
    st.plotly_chart(fig, use_container_width=True)

elif sezione == "Yield Curve":
    st.title("Yield Curve")
    fig = plot_yield_curve(indicators_df)
    st.plotly_chart(fig, use_container_width=True)

elif sezione == "Financial Conditions":
    st.title("Financial Conditions Index")
    fig = plot_fci(indicators_df)
    st.plotly_chart(fig, use_container_width=True)

elif sezione == "Credit":
    st.title("Credit & Liquidity")
    st.write("Coming soon")

elif sezione == "Markets":
    st.title("Financial Markets")
    st.write("Coming soon")

elif sezione == "Heatmap":
    st.title("Macro Heatmap")
    fig = plot_heatmap(fred_df, market_df)
    st.plotly_chart(fig, use_container_width=True)