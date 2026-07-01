import pandas as pd
import os

data_path = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_path, exist_ok=True)

def yield_curve_slope(fred_df):
    return fred_df["DGS10"] - fred_df["DGS2"]

def real_interest_rate(fred_df):
    return fred_df["DGS10"] - fred_df["T10YIE"]


def excess_equity_returns(market_df, fred_df):
    sp500_return = market_df["S&P 500"].pct_change(252)
    excess = sp500_return - fred_df["FEDFUNDS"] / 100
    return excess

def rolling_correlation(market_df, fred_df, window=60):
    return market_df["S&P 500"].rolling(window).corr(fred_df["BAMLH0A0HYM2"])

def zscore(series):
    return (series - series.mean()) / series.std()

def financial_condition_index(market_df, fred_df):
    components = {"vix": zscore(market_df["VIX"]),
                  "slope": zscore(yield_curve_slope(fred_df)),
                  "hy_spread": zscore(fred_df["BAMLH0A0HYM2"]),
                  "sp500_return": zscore(market_df["S&P 500"].pct_change(60)),
                  "real_rate": zscore(real_interest_rate(fred_df))}
    
    components_df = pd.DataFrame(components)
    fci = components_df.mean(axis=1)
    
    return fci

def compute_all_indicators(market_df, fred_df):
    indicators = {}
    indicators["yield_curve_slope"] = yield_curve_slope(fred_df)
    indicators["real_interest_rate"] = real_interest_rate(fred_df)
    indicators["excess_equity_returns"] = excess_equity_returns(market_df, fred_df)
    indicators["rolling_correlation"] = rolling_correlation(market_df, fred_df)
    indicators["financial_condition_index"] = financial_condition_index(market_df, fred_df)

    indicators_df = pd.concat(indicators, axis=1)
    indicators_df.to_csv(os.path.join(data_path, "indicators.csv"), index=True)


    return indicators_df

if __name__ == "__main__":
    from macro_data import fetch_fred_data, fetch_market_data
    import os
    
    api_key = os.environ.get("FRED_API_KEY")
    fred_df = fetch_fred_data(api_key)
    market_df = fetch_market_data()
    
    indicators_df = compute_all_indicators(market_df, fred_df)
    print(f"Shape: {indicators_df.shape}")
    print(f"Colonne: {list(indicators_df.columns)}")
    print(f"NaN totali: {indicators_df.isna().sum().sum()}")
    print(indicators_df.tail())