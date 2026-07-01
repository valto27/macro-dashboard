import yaml
from fredapi import Fred
import pandas as pd
import os
import yfinance as yf
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

data_path = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_path, exist_ok=True)
API = os.environ.get("FRED_API_KEY")

def load_config(path="config/indicators.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config

def fetch_fred_data(api_key):
    config = load_config()
    fred_indicators = config.get("fred", [])
    data = {}
    fred = Fred(api_key=api_key)
    for indicator in fred_indicators:
        id = indicator.get("id")
        name = indicator.get("name")
        frequency = indicator.get("frequency")
        category = indicator.get("category")
        data[id] = fred.get_series(id, observation_start="2000-01-01")
    
    data_df = pd.DataFrame(data)
    return data_df

def save_fred_data_to_csv(data_df, filename="fred_data.csv"):
    data_df.to_csv(os.path.join(data_path, filename), index=True)

def fetch_market_data():
    config = load_config()
    market_indicators = config.get("yfinance", [])
    data = {}
    for indicator in market_indicators:
        Name = indicator.get("ticker")
        name = indicator.get("name")
        category = indicator.get("category")
        data[name] = yf.download(Name, start="2000-01-01", end=datetime.datetime.now())['Close'].squeeze()
    
    data_df = pd.DataFrame(data)
    return data_df

def save_market_data_to_csv(data_df, filename="market_data.csv"):
    data_df.to_csv(os.path.join(data_path, filename), index=True)

if __name__ == "__main__":
    api_key = API
    
    print("Testing load_config...")
    config = load_config()
    print(f"Chiavi config: {list(config.keys())}")
    print(f"Serie FRED: {len(config['fred'])}")
    print(f"Serie yfinance: {len(config['yfinance'])}")

    print("\nTesting fetch_fred_data...")
    print(f"API key letta: {api_key}")
    fred_df = fetch_fred_data(api_key)
    print(f"Shape: {fred_df.shape}")
    print(f"Colonne: {list(fred_df.columns)}")
    print(f"Date: {fred_df.index[0]} → {fred_df.index[-1]}")
    print(f"NaN totali: {fred_df.isna().sum().sum()}")
    save_fred_data_to_csv(fred_df)
    print("CSV salvato.")

    print("\nTesting fetch_market_data...")
    market_df = fetch_market_data()
    print(f"Shape: {market_df.shape}")
    print(f"Colonne: {list(market_df.columns)}")
    print(f"Date: {market_df.index[0]} → {market_df.index[-1]}")
    print(f"NaN totali: {market_df.isna().sum().sum()}")
    save_market_data_to_csv(market_df)
    print("CSV salvato.")