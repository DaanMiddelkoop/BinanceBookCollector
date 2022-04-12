import time
from queue import Queue
from collections import OrderedDict


class Orderbook:
    def __init__(self, symbol):
        self.symbol = symbol
        self.latest_update = None
        self.last_update_id = None
        self.a = None
        self.b = None
        self.last_u = None
        self.buffer = Queue()

    def update(self, message):
        self.buffer.put(message)

        if not self.validState():
            return

        while not self.buffer.empty():
            data = self.buffer.get()['data']

            # Drop any event where u is < lastUpdateId in the snapshot.
            if data['u'] < self.last_update_id:
                continue

            # The first processed event should have U <= lastUpdateId AND u >= lastUpdateId
            if data['U'] > self.last_update_id or data['u'] < self.last_update_id:
                continue

            # While listening to the stream, each new event's pu should be equal to the previous event's u, otherwise initialize the process from step 3.
            if data['pu'] != self.last_u:
                self.a, self.b = None, None
                continue

            self.process_data(data)
            self.last_u = data['u']

    def process_data(self, data):
        for bid in data['bids']:
            if bid[1] == 0:
                del self.b[bid[0]]
            else:
                self.b[bid[0]] = bid[1]

        for ask in data['asks']:
            if ask[1] == 0:
                del self.a[ask[0]]
            else:
                self.a[ask[0]] = ask[1]

    def set_snapshot(self, snapshot):
        self.b = dict()
        self.a = dict()

        for bid in snapshot['bids']:
            self.b[bid[0]] = bid[1]

        for ask in snapshot['asks']:
            self.a[ask[0]] = ask[1]

        self.last_update_id = snapshot['lastUpdateId']

    def validState(self):
        return self.a is not None and self.b is not None


