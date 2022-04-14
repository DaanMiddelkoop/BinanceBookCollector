import asyncio
from datetime import datetime, timezone
import time
from math import floor

import psycopg2

from BinanceConnector import BinanceConnector

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="barisendaan")


async def collectData(books):
    last_update = time.time()
    while True:
        now = time.time()
        while now < floor(last_update) + 1:
            await asyncio.sleep(0.1)
            now = time.time()
        last_update = now
        print("Collecting update", now)
        await collectBooks(books)


async def collectBooks(books):
    for book in books:
        if book.bids is None or book.asks is None:
            print("Warning empty book", book.symbol)
            continue

        cursor = conn.cursor()
        dt = datetime.now(timezone.utc)
        cursor.execute(f"INSERT INTO updates (ts, symbol) values ('{dt}', '{book.symbol}') RETURNING id")
        row_id = cursor.fetchone()[0]
        for bid in book.bids.items():
            cursor.execute(f"INSERT INTO bids (update, price, amount) values ({row_id}, {float(bid[0])}, {float(bid[1])})")
        for ask in book.asks.items():
            cursor.execute(f"INSERT INTO asks (update, price, amount) values ({row_id}, {float(ask[0])}, {float(ask[1])})")
    conn.commit()


async def main():
    connector = BinanceConnector()
    books = await connector.getOrderbooks()
    tasks = [connector.run(), collectData(books)]

    await asyncio.gather(*tasks)


asyncio.run(main())
