import os
import requests
import yfinance as yf

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Extended Watchlist of High-Liquidity NSE Stocks
WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "TATAMOTORS.NS",
    "SBIN.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "ITC.NS",
    "AXISBANK.NS",
    "LT.NS",
    "SUNPHARMA.NS",
    "BAJFINANCE.NS",
    "MARUTI.NS",
    "TITAN.NS",
    "NTPC.NS",
    "WIPRO.NS",
    "HCLTECH.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "TATASTEEL.NS",
]


def send_telegram_message(message):
  if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)


def get_top_signals():
  signals = []

  for stock in WATCHLIST:
    try:
      # Fetch intraday data (15 minutes interval)
      data = yf.download(stock, period="1d", interval="15m", progress=False)

      if len(data) >= 2:
        # Multi-index or single index protection for pandas dataframe
        highs = data["High"].iloc
        lows = data["Low"].iloc
        closes = data["Close"].iloc
        volumes = data["Volume"].iloc

        first_candle_high = float(highs[0])
        first_candle_low = float(lows[0])
        current_price = float(closes[-1])
        current_volume = float(volumes[-1])
        avg_volume = float(data["Volume"].mean()) if "Volume" in data else 1.0

        # Momentum calculation: Price moving above first candle high
        if current_price >= first_candle_high:
          risk = first_candle_high - first_candle_low
          if risk <= 0:
            risk = current_price * 0.005  # fallback risk

          target_price = first_candle_high + (2 * risk)
          # Score based on volume momentum
          score = (
              (current_price - first_candle_high) / first_candle_high
          ) * (current_volume / avg_volume)

          signals.append({
              "stock": stock.replace(".NS", ""),
              "price": current_price,
              "sl": first_candle_low,
              "target": target_price,
              "score": score,
          })
    except Exception as e:
      print(f"Error checking {stock}: {e}")

  # Sort by top momentum/score
  signals = sorted(signals, key=lambda x: x["score"], reverse=True)

  # Even if market is slow, ensure we grab the top available movements (up to 5)
  top_signals = signals[:5]

  msg_lines = [
      "🚀 *DAILY TOP 5 PRO INTRADAY SIGNALS* 🚀",
      "----------------------------------------",
  ]

  if top_signals:
    for i, sig in enumerate(top_signals, 1):
      s_text = (
          f"{i}. *{sig['stock']}* (BUY)\n"
          f"   • Entry Price: ₹{sig['price']:.2f}\n"
          f"   • Stop Loss: ₹{sig['sl']:.2f}\n"
          f"   • Target (1:2): ₹{sig['target']:.2f}\n"
      )
      msg_lines.append(s_text)
  else:
    msg_lines.append(
        "⚠️ Market is completely flat right now. Monitoring next moves..."
    )

  final_message = "\n".join(msg_lines)
  send_telegram_message(final_message)


if __name__ == "__main__":
  get_top_signals()
          
