import asyncio
from asyncio import Queue

import aiohttp
import websockets
import json


class Orderbook:
    def __init__(self, symbol, api_path, ws_path):
        self.api_path = api_path
        self.ws_path = ws_path
        self.symbol = symbol
        self.bids = None
        self.asks = None
        self.queue = Queue()
        self.lastUpdateId = None
        self.firstMessageProcessed = False
        self.initialMessageUpdateId = None
        self.lastU = None
        print(symbol)

    async def run(self):
        await asyncio.gather(self.run_ws(), self.processQueue())

    async def run_ws(self):
        path = self.ws_path + self.symbol + '@depth'
        async with websockets.connect(path) as websocket:
            while True:
                message = json.loads(await websocket.recv())
                await self.handleWs(message['data'])

    async def handleWs(self, update):
        assert update['e'] == 'depthUpdate'
        await self.queue.put(update)
        print("Put item in queue")

    async def handleQueue(self, data):
        if self.firstMessageProcessed:
            if data['pu'] != self.lastU:
                self.bids = None
                self.asks = None
                self.lastUpdateId = None
                self.firstMessageProcessed = False
                self.lastU = None
                return
            self.lastU = data['u']
        else:
            if data['u'] < self.initialMessageUpdateId:
                return
            else:
                self.firstMessageProcessed = True
                self.lastU = data['u']
                assert data['U'] <= self.initialMessageUpdateId <= data['u']

        print(data)
        for price, amount in data['b']:
            if float(amount) == 0.0:
                if price in self.bids:
                    del self.bids[price]
            else:
                self.bids[price] = amount

        for price, amount in data['a']:
            if float(amount) == 0.0:
                if price in self.asks:
                    del self.asks[price]
            else:
                self.asks[price] = amount

    async def initState(self):
        path = self.api_path + f'/depth?symbol={self.symbol}&limit=1000'
        print("Getting initial state")
        async with aiohttp.ClientSession() as session:
            async with session.get(path) as resp:
                print(await resp.json())
                data = await resp.json()
                self.bids = {}
                self.asks = {}
                for price, amount in data['bids']:
                    self.bids[price] = amount

                for price, amount in data['asks']:
                    self.asks[price] = amount

                self.initialMessageUpdateId = data['lastUpdateId']
                print("Should be initialised now", self.initialMessageUpdateId, len(self.bids), len(self.asks))

    async def processQueue(self):
        while True:
            print("Loop state", self.bids is None, self.asks is None, self.initialMessageUpdateId)
            if self.bids is not None and self.asks is not None:
                print(self.symbol, 'bids', len(self.bids), 'asks', len(self.asks))

            if self.bids is not None and self.asks is not None and self.initialMessageUpdateId is not None:
                await self.handleQueue(await self.queue.get())
            else:
                while self.queue.empty():
                    await asyncio.sleep(0.1)
                print("Queue not empty")
                await self.initState()



