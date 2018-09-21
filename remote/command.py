import asyncio
import pickle as pk


class Receiver:
    def __init__(self, server_url, port):
        self._server_url = server_url
        self._port = port
        self._recv_callback = None

    def set_recv_callback(self, recv_callback):
        if not callable(recv_callback):
            raise ValueError('Callback must be type of function.')
        self._recv_callback = recv_callback

    def connect(self):
        if not self._recv_callback:
            raise ReferenceError('recv_callback is None. Please define with set_recv_callback().')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._io_handle(loop))

    async def _io_handle(self, loop):
        reader, writer = await asyncio.open_connection(self._server_url, self._port, loop=loop)

        while True:
            live_signal = bytearray(1)
            writer.write(live_signal)

            raw = await reader.read(128)
            try:
                command = pk.loads(raw)
            except Exception as e:
                command = []

            self._recv_callback(command)


if __name__ == '__main__':
    receiver = Receiver('localhost', 8888)
    receiver.set_recv_callback(lambda cmd_obj: print(cmd_obj))
    receiver.connect()
