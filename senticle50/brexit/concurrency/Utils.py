import asyncio
from threading import Thread


class Utils:
    @staticmethod
    def start_worker_loop(loop):
        """Switch to new event loop and run forever"""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @staticmethod
    def get_worker_loop():
        worker_loop = asyncio.new_event_loop()
        worker = Thread(target=Utils.start_worker_loop, args=(worker_loop,))
        worker.start()
        return worker_loop
