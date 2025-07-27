import requests
import time
import schedule
from telegram import Bot

# === CONFIGURATION ===
BOT_TOKEN = '8378883407:AAG73uU1ko1KEIZtwmo_STyGQG6zCtMx0gI'
CHAT_ID = '2139103263'
bot = Bot(token=BOT_TOKEN)

PAIRS = ['US30', 'BTC/USD', 'XAU/USD']
API_URL = 'https://api.twelvedata.com/time_series'
API_KEY = 'e95129d2d4af4ddaa2fcce553a24804d'

# === HELPER FUNCTIONS ===

def get_candles(pair, interval='12min'):
    symbol = pair.replace("/", "")
    try:
        response = requests.get(f"{API_URL}?symbol={symbol}&interval={interval}&outputsize=30&apikey={API_KEY}")
        data = response.json()
        if 'values' in data:
            candles = [
                {
                    'close': float(c['close']),
                    'open': float(c['open']),
                    'high': float(c['high']),
                    'low': float(c['low']),
                    'volume': float(c.get('volume', 1000))  # Use dummy volume if not present
                }
                for c in reversed(data['values'])
            ]
            return candles
    except Exception as e:
        print(f"Error fetching {pair}: {e}")
    return []

def sma(values, period=30):
    return sum(values[-period:]) / period if len(values) >= period else None

def detect_signal(pair):
    candles = get_candles(pair)
    if not candles or len(candles) < 10:
        return None

    closes = [c['close'] for c in candles]
    volumes = [c['volume'] for c in candles]
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]

    # === 30 SMA CALC ===
    ma30 = sma(closes)
    if not ma30:
        return None

    # === VOLUME FILTER ===
    if volumes[-1] < 500:
        return None

    # === 3-CANDLE BREAKOUT STRUCTURE ===
    last3 = closes[-4:-1]
    current = closes[-1]
    prior_zone = closes[-7:-4]
    key_level = prior_zone[-1]

    broke_up = all(c < ma30 for c in last3) and current > last3[-1]
    broke_down = all(c > ma30 for c in last3) and current < last3[-1]

    retracement_ok = abs(current - key_level) / abs(key_level) >= 0.5

    if broke_down and current > key_level and retracement_ok:
        return f"🔔 BUY SETUP on {pair} approaching breakout 🔼"

    if broke_up and current < key_level and retracement_ok:
        return f"🔔 SELL SETUP on {pair} approaching breakout 🔽"

    return None

def check_signals():
    for pair in PAIRS:
        try:
            signal = detect_signal(pair)
            if signal:
                bot.send_message(chat_id=CHAT_ID, text=signal)
        except Exception as e:
            print(f"Error checking {pair}: {e}")

def run_bot():
    print("Trading bot running...")
    schedule.every(12).minutes.do(check_signals)
    while True:
        schedule.run_pending()
        time.sleep(1)
