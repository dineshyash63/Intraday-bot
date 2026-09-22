import os
import requests
import yfinance as yf

# Telegram Bot Credentials (GitHub Secrets-ல் இருந்து எடுக்கும்)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# உங்கள் வாட்ச் லிஸ்ட் பங்குகள் (Top Volume / Gainers)
WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "TATAMOTORS.NS", "SBIN.NS"]


def send_telegram_message(message):
  if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)


def check_market():
  messages = []
  for stock in WATCHLIST:
    try:
      # 15 நிமிட இடைவெளி கொண்ட நேரலைத் தரவு
      data = yf.download(stock, period="1d", interval="15m", progress=False)

      if len(data) >= 2:
        # முதல் கேண்டிலின் உயர் விலை (First Candle High)
        first_candle_high = float(data["High"].iloc[0])
        current_price = float(data["Close"].iloc[-1])

        # பிரேக்அவுட் நிபந்தனை (Breakout Rule)
        if current_price > first_candle_high:
          msg = (
              f"🚀 BUY SIGNAL: {stock}\nCurrent Price: {current_price}\nBroke"
              f" First Candle High: {first_candle_high}"
          )
          messages.append(msg)
    except Exception as e:
      print(f"Error fetching {stock}: {e}")

  if messages:
    send_telegram_message("\n\n".join(messages))
  else:
    print("No breakout signals found yet.")


if __name__ == "__main__":
  check_market()
    
