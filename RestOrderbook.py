import requests
import time

while True:
    time.sleep(1)
    book = requests.get("https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=1000")
    print(book)
