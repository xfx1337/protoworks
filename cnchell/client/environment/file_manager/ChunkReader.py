import os

class ChunkReader(object):
    def __init__(self, file_name, chunk_size, progress=None):
        size = os.path.getsize(file_name)
        self.remaining = size
        self.f = open(file_name, "rb")
        self.chunk_size = chunk_size
        self.progress = progress
        if self.progress != None:
            self.progress.full = size

    @property
    def len(self):
        return self.remaining

    def read(self, length):
        data = self.f.read(min(self.remaining, length))
        self.remaining -= len(data)
        if self.progress != None:
                self.progress.signals.add.emit(len(data))
        return data
            
    def close_file_handler(self):
        self.f.close()