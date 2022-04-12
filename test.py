import time

from binance import ThreadedDepthCacheManager
from binance.client import Client
client = Client("", "")
import sqlite3


def main():
    futures = [
        'BTCUSDT',
        'btcusdt_220624'
        'ETHUSDT',
        'ethusdt_220624'
    ]

    spots = [
        'BTCUSDC',
        'BTCUSDT',
        'ETHUSDC',
        'ETHUSDT',
    ]

    dcm = ThreadedDepthCacheManager()
    # start is required to initialise its internal loop
    dcm.start()

    last_books = dict()

    def future(depth_cache):
        last_books['f' + depth_cache.symbol] = (depth_cache.get_bids()[:10], depth_cache.get_asks()[:10])

    def spot(depth_cache):
        last_books['s' + depth_cache.symbol] = (depth_cache.get_bids()[:10], depth_cache.get_asks()[:10])

    for symbol in futures:
        dcm.start_futures_depth_socket(future, symbol=symbol)

    for symbol in spots:
        dcm.start_depth_cache(spot, symbol=symbol)

    # multiple depth caches can be started
    # dcm_name = dcm.start_futures_depth_socket(handle_depth_cache, symbol='ETHBTC')

    while True:
        current_time = time.time()
        for key, data in list(last_books.items()):
            store(current_time, key, data[0], data[1])
        time.sleep(1)


    dcm.join()


conn = sqlite3.connect('DatabaseName.db')


def store(current_time, symbol, bids, asks):
    bid_string = '[' + ','.join(['[' + str(x[0]) + ',' + str(x[1]) + ']' for x in bids]) + ']'
    ask_string = '[' + ','.join(['[' + str(x[0]) + ',' + str(x[1]) + ']' for x in asks]) + ']'

    print(bid_string, ask_string)

    sql = f"INSERT INTO books(time, symbol, bids ,asks) VALUES({current_time.__round__()},'{symbol}','{bid_string}', '{ask_string}')"
    cur = conn.execute(sql)
    conn.commit()
    return cur.lastrowid


if __name__ == "__main__":
   main()
