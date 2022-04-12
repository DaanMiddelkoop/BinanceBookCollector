import time

from binance.websocket.futures.websocket_client import FuturesWebsocketClient as WebsocketClient
from binance.futures import Futures as HttpClient

from Orderbook import Orderbook
from Symbol import Symbol


class Binance:

    def __init__(self):
        # self.httpManager = HttpClient(base_url=)
        self.order_books = {}
        self.ws_client = WebsocketClient()
        self.ws_client.start()

        self.httpClient = HttpClient()
        self.symbols = self.get_symbols()
        self.subscribe_symbols(self.symbols)

    def get_symbols(self):
        all_symbols = self.httpClient.exchange_info()['symbols']
        return {x['pair']: Symbol(x) for x in all_symbols if x['baseAsset'] == 'BTC' and x['quoteAsset'] == 'USDT'}

    def subscribe_symbols(self, symbols):
        endpoints = [x + '@depth' for x in symbols.keys()]
        self.order_books = {x: Orderbook(self, x) for x in symbols.keys()}
        self.ws_client.instant_subscribe(
            stream=endpoints,
            callback=self.handle_orderbook,
        )

    def handle_orderbook(self, message):
        self.order_books[message['data']['s']].update(message)

    def run(self):
        for symbol, book in self.order_books.items():
            if not book.isValid():
                book.set_snapshot(self.httpClient.depth(symbol))
        time.sleep(1)
