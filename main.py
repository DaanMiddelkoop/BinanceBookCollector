import asyncio

from BinanceConnector import BinanceConnector


async def main():
    connector = BinanceConnector()
    tasks = [connector.run()]

    await asyncio.gather(*tasks)


asyncio.run(main())
