import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Cache for prices (asset: (price, timestamp))
PRICE_CACHE = {}
CACHE_DURATION = 300  # Cache prices for 5 minutes


def fetch_alpha_vantage_price(function, symbol, extra_params=None):
    try:
        base_url = "https://www.alphavantage.co/query"
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        if extra_params:
            params.update(extra_params)

        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data or "Note" in data:
            print(f"Alpha Vantage error for {symbol}: {data.get('Error Message', data.get('Note'))}")
            return None

        if function == "GLOBAL_QUOTE":
            price = data.get("Global Quote", {}).get("05. price")
        elif function == "CURRENCY_EXCHANGE_RATE":
            price = data.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate")
        elif function == "COMMODITY":
            price = data.get("data", [{}])[-1].get("value")  # Latest commodity price
        else:
            return None

        return float(price) if price else None
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching {symbol} price: {e}")
        return None


def get_asset_price(asset):
    asset_map = {
        # Stocks
        "AAPL": ("GLOBAL_QUOTE", "AAPL"),
        "MSFT": ("GLOBAL_QUOTE", "MSFT"),
        "AMZN": ("GLOBAL_QUOTE", "AMZN"),
        "GOOGL": ("GLOBAL_QUOTE", "GOOGL"),
        "META": ("GLOBAL_QUOTE", "META"),
        "TSLA": ("GLOBAL_QUOTE", "TSLA"),
        "NVDA": ("GLOBAL_QUOTE", "NVDA"),
        "JPM": ("GLOBAL_QUOTE", "JPM"),
        "WMT": ("GLOBAL_QUOTE", "WMT"),
        "V": ("GLOBAL_QUOTE", "V"),
        # Cryptocurrencies
        "BTC": ("CURRENCY_EXCHANGE_RATE", "BTC", {"to_currency": "USD"}),
        "ETH": ("CURRENCY_EXCHANGE_RATE", "ETH", {"to_currency": "USD"}),
        "BNB": ("CURRENCY_EXCHANGE_RATE", "BNB", {"to_currency": "USD"}),
        "XRP": ("CURRENCY_EXCHANGE_RATE", "XRP", {"to_currency": "USD"}),
        "ADA": ("CURRENCY_EXCHANGE_RATE", "ADA", {"to_currency": "USD"}),
        "SOL": ("CURRENCY_EXCHANGE_RATE", "SOL", {"to_currency": "USD"}),
        "DOGE": ("CURRENCY_EXCHANGE_RATE", "DOGE", {"to_currency": "USD"}),
        "DOT": ("CURRENCY_EXCHANGE_RATE", "DOT", {"to_currency": "USD"}),
        "AVAX": ("CURRENCY_EXCHANGE_RATE", "AVAX", {"to_currency": "USD"}),
        "SHIB": ("CURRENCY_EXCHANGE_RATE", "SHIB", {"to_currency": "USD"}),
        # Commodities
        "GOLD": ("COMMODITY", "GOLD"),
        "SILVER": ("COMMODITY", "SILVER"),
        "CRUDE_OIL": ("COMMODITY", "WTI"),
        "NAT_GAS": ("COMMODITY", "NATURAL_GAS"),
        "COPPER": ("COMMODITY", "COPPER")
    }

    if asset not in asset_map:
        return None

    # Check cache
    if asset in PRICE_CACHE:
        price, timestamp = PRICE_CACHE[asset]
        if time.time() - timestamp < CACHE_DURATION:
            return price

    # Fetch price
    config = asset_map[asset]
    function = config[0]
    symbol = config[1]
    extra_params = config[2] if len(config) > 2 else None

    price = fetch_alpha_vantage_price(function, symbol, extra_params)

    # Update cache
    if price is not None:
        PRICE_CACHE[asset] = (price, time.time())

    return price