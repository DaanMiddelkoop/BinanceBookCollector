class Symbol:

    def __init__(self, symbol_message):
        self.symbol = symbol_message['pair']
        self.type = symbol_message['contractType']
        self.expiry = symbol_message['deliveryDate']