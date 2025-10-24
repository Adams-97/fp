from queue import Queue

class ResultWriter:
    pass


class ResultHandler:
    def __init__(self, size: int, writer):
        self._queue: Queue = Queue(maxsize=size)
        self.writer = writer

    def add_result(self, result):
        self.buffer