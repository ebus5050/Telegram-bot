import requests
import time
import schedule
from telegram import Bot

# === Configuration ===
BOT_TOKEN = 'your_telegram_bot_token'
CHAT_ID = 'your_telegram_chat_id'
bot = Bot(token=BOT_TOKEN)

# Replace with actual free or paid API that supports 12-min candles and volume
PAIRS = ['US30', 'BTCUSD', 'XAUUSD']
API_URL = 'https://api.example.com/marketdata'

# === Signal Logic Functions ===

def get_candles(pair):
    response = requests.get(f"{API_URL}/{pair}?interval=12min&limit=30")
    data = response.json()
    return data['candles']

def sma(values, period=30):
    return sum(values[-period:]) / period if len(values) >= period else None

def detect_signal(pair):
    candles = get_candles(pair)
    if not candles or len(candles) < 6:
        return None

    # Extract OHLCV
    closes = [c['close'] for c in candles]
    volumes = [c['volume'] for c in candles]
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]

    # === Volume Filter ===
    if volumes[-1] < 500:
        return None

    # === MA Direction Support Logic ===
    ma30 = sma(closes)
    trend_up = closes[-1] > ma30
    trend_down = closes[-1] < ma30

    # === Detect Pattern: 3 Candle Force Break Logic ===
    last3 = closes[-4:-1]
    current = closes[-1]
    prior_zone = closes[-7:-4]

    # Check if last 3 candles broke opposite MA zone
    broke_up = all(c < ma30 for c in last3) and current > last3[-1]
    broke_down = all(c > ma30 for c in last3) and current < last3[-1]

    # Then price pulls back 50-100% without breaking rejection zone
    retracement_ok = abs(current - prior_zone[-1]) / abs(prior_zone[-1]) >= 0.5

    # Now wait for price to come close (10 pips) to last level that started the earlier move
    key_level = prior_zone[-1]
    if trend_up and broke_down and retracement_ok and abs(current - key_level) <= 0.0010:
        return f"🔔 BUY SETUP on {pair}: Approaching breakout 🔼"

    if trend_down and broke_up and retracement_ok and abs(current - key_level) <= 0.0010:
        return f"🔔 SELL SETUP on {pair}: Approaching breakout 🔽"

    return None

# === Bot Dispatcher ===
def check_signals():
    for pair in PAIRS:
        try:
            signal = detect_signal(pair)
            if signal:
                bot.send_message(chat_id=CHAT_ID, text=signal)
        except Exception as e:
            print(f"Error checking {pair}: {e}")

# === Scheduler ===
schedule.every(12).minutes.do(check_signals)

print("Bot running... Press Ctrl+C to exit")
while True:
    schedule.run_pending()
    time.sleep(1)
