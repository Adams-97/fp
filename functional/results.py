class ResultWriter:
    pass


class ResultHandler:
    def __init__(self, buffer_size: int, writer):
        self.buffer_size = buffer_size
        self.writer = writer

    def add_result(self, result):
        pass