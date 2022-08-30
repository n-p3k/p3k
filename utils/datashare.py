import os
import sys

"""
DataShare - sharing data among processes and app

mmap       : https://www.pythoncentral.io/memory-mapped-mmap-file-support-in-python/
ShareMemory: https://docs.python.org/3/library/multiprocessing.shared_memory.html

"""

class DataShare:
    def __init__(self, name, mode='r'):
        self.name = name
        self.mode = mode
        self.data = {}

    def load(self):
        """Load share file from json"""
        pass

    def save(self):
        pass

    def read(self, key):
        """Save share file."""
        self.check('r') 

    def write(self, key, val):
        self.check('w')
        self.data[key] = val

    def check(self, cond):
        violation = True
        for allowed in self.mode:
            if cond == allowed:
                violation = False
                break
        if violation:
            raise RuntimeError('unsafe - access mode is not allowed')

def test():
    share = DataShare('/tmp/debug', mode='rw')
    im = share.read('image')
    share.write('image', im)

