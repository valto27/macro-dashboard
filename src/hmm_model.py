import pandas as pd
from hmmlearn import hmm

def prepare_features(indicators_df, fred_df, market_df):
    features = pd.DataFrame(index=indicators_df.index)
    
    features["yield_curve_slope"] = indicators_df["yield_curve_slope"]
    features["real_interest_rate"] = indicators_df["real_interest_rate"]
    features["financial_condition_index"] = indicators_df["financial_condition_index"]
    
    features["VIX"] = market_df.get("VIX", pd.Series(index=market_df.index))

    features = features.reindex(market_df.index)
    
    features.ffill(inplace=True)
    print(f"Shape prima di dropna: {features.shape}")
    print(f"NaN per colonna:\n{features.isna().sum()}")
    features.dropna(inplace=True)
    
    features_df = pd.DataFrame(features)
    return features_df

def train_hmm(features_df, n_states=3):
    model = hmm.GaussianHMM(n_components=n_states, covariance_type="diag", n_iter=1000)
    model.fit(features_df)
    
    
    return model

def predict_regimes(model, features_df):
    hidden_states = model.predict(features_df)
    probabilities = model.predict_proba(features_df)

    hidden_states_df = pd.DataFrame(hidden_states, index=features_df.index, columns=["Regime"])
    probabilities_df = pd.DataFrame(probabilities, index=features_df.index, columns=[f"Prob_State_{i}" for i in range(model.n_components)])

    return hidden_states_df, probabilities_df

def run_hmm_pipeline(indicators_df, fred_df, market_df, n_states=3):
    features_df = prepare_features(indicators_df, fred_df, market_df)
    model = train_hmm(features_df, n_states)
    hidden_states_df, probabilities_df = predict_regimes(model, features_df)
    
    return hidden_states_df, probabilities_df, model, features_df

if __name__ == "__main__":
    from macro_data import fetch_fred_data, fetch_market_data
    from indicators import compute_all_indicators
    import os
    
    api_key = os.environ.get("FRED_API_KEY")
    fred_df = fetch_fred_data(api_key)
    market_df = fetch_market_data()
    
    indicators_df = compute_all_indicators(market_df, fred_df)
    
    hidden_states_df, probabilities_df, model, features_df = run_hmm_pipeline(indicators_df, fred_df, market_df)
    
    print(f"Hidden States Shape: {hidden_states_df.shape}")
    print(f"Probabilities Shape: {probabilities_df.shape}")
    print(hidden_states_df["Regime"].value_counts())
    print(hidden_states_df.tail(10))
