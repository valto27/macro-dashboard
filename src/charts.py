import plotly.graph_objects as go
import pandas as pd

import indicators

def plot_regimes(hidden_states_df, market_df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=market_df.index, y=market_df["S&P 500"], mode="lines", name="S&P 500"))
    regime_colors = {0: "red", 1: "yellow", 2: "green"}

    changes = hidden_states_df["Regime"].ne(hidden_states_df["Regime"].shift())
    change_idx = hidden_states_df.index[changes].tolist()
    change_idx.append(hidden_states_df.index[-1])

    for i in range(len(change_idx) - 1):
        start = change_idx[i]
        end = change_idx[i + 1]
        regime = hidden_states_df.loc[start, "Regime"]
        color = regime_colors[regime]
        fig.add_vrect(x0=start, x1=end, fillcolor=color, opacity=0.2, line_width=0)
    
    return fig

def plot_yield_curve(indicators_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=indicators_df.index, y=indicators_df["yield_curve_slope"], mode="lines", name="Yield Curve Slope"))
    fig.add_hline(y=0, line_dash="dash", line_color="black")

    recessions = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01")]
    for start, end in recessions:
        fig.add_vrect(x0=start, x1=end, fillcolor="grey", opacity=0.3, line_width=0)    
    
    return fig

def plot_fci(indicators_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=indicators_df.index, y=indicators_df["financial_condition_index"], mode="lines", name="Financial Condition Index"))
    fig.add_hline(y=0, line_dash="dash", line_color="black")   

    fci = indicators_df["financial_condition_index"]

    fig.add_trace(go.Scatter(
        x=fci.index, 
        y=fci.clip(lower=0),
        fill="tozeroy", 
        fillcolor="rgba(255,0,0,0.3)", 
        line=dict(width=0),
        name="Restrictive"))

    fig.add_trace(go.Scatter(
        x=fci.index, 
        y=fci.clip(upper=0),
        fill="tozeroy", 
        fillcolor="rgba(0,255,0,0.3)", 
        line=dict(width=0),
        name="Accommodative"))
    
    return fig

def plot_heatmap(fred_df, market_df):
    indicators = [
        "DGS10", 
        "DGS2",
        "BAMLH0A0HYM2",
        "CPIAUCSL", 
        "UNRATE",
        "VIX",
        "S&P 500"]
    
    combined = fred_df.join(market_df, how="outer")
    selected = combined[indicators]
    monthly = selected.resample("ME").last()
    last_24 = monthly.iloc[-24:]
    last_24 = last_24.apply(lambda x: (x - x.mean()) / x.std(), axis=0)

    fig = go.Figure(data=go.Heatmap(z=last_24.values.T, x=last_24.index, y=last_24.columns, colorscale="RdYlGn"))
    return fig
    
if __name__ == "__main__":
    from macro_data import fetch_fred_data, fetch_market_data
    from indicators import compute_all_indicators
    from hmm_model import run_hmm_pipeline
    import os
    
    api_key = os.environ.get("FRED_API_KEY")
    fred_df = fetch_fred_data(api_key)
    market_df = fetch_market_data()
    
    indicators_df = compute_all_indicators(market_df, fred_df)
    hidden_states_df = run_hmm_pipeline(indicators_df, fred_df, market_df)[0]
    
    fig_regimes = plot_regimes(hidden_states_df, market_df)
    fig_yield_curve = plot_yield_curve(indicators_df)
    fig_fci = plot_fci(indicators_df)
    fig_heatmap = plot_heatmap(fred_df, market_df)

    fig_regimes.show()
    fig_yield_curve.show()
    fig_fci.show()
    fig_heatmap.show()