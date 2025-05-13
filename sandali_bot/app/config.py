import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
METALS_API_KEY = os.getenv("METALS_API_KEY")
