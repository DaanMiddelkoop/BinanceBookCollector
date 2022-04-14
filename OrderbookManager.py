import asyncio

from Orderbook import Orderbook


class OrderbookManager:

    def __init__(self, symbols, api_path, ws_path):
        self.api_path = api_path
        self.ws_path = ws_path
        self.symbols = symbols
        self.order_books = {symbol: Orderbook(symbol, api_path, ws_path) for symbol in symbols}

    async def run(self):
        await asyncio.gather(*[x.run() for x in self.order_books.values()])


