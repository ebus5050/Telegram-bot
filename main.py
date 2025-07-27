from flask import Flask
import threading
from bot_logic import run_bot  # Import the logic from another file

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    # Start Flask server (to keep Render alive)
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 10000}).start()
    
    # Start your trading bot in background
    run_bot()
