import asyncio

from OrderbookManager import OrderbookManager


class BinanceConnector:

    def __init__(self):
        futures = [
            # 'btcusdt',
            # 'btcusdt_220624',
            # 'ETHUSDT',
            # 'ethusdt_220624'
        ]

        spots = [
            'btcusdc',
            'btcusdt',
            'ethusdc',
            'ethusdt',
        ]

        self.book_managers = [
            OrderbookManager(spots, 'https://api.binance.com/api/v3', 'wss://stream.binance.com:9443/ws/'),
            OrderbookManager(futures, 'https://fapi.binance.com/fapi/v1', 'wss://fstream.binance.com/stream?streams=')
        ]

    pass

    async def run(self):
        tasks = [x.run() for x in self.book_managers]
        await asyncio.gather(*tasks)

    async def getOrderbooks(self):
        books = []
        for manager in self.book_managers:
            for book in manager.order_books.values():
                books.append(book)
        return books