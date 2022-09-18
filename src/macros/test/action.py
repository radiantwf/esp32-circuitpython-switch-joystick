from node import *


class Action(object):
    def __init__(self, name: str, rows):
        self._name = name
        self._current = None

    @property
    def name(self):
        return self._name

    def dequeue(self) -> Node:
        node = self._current
        if self._current._loop_start_node != None:
            if self._current._current_loop_times < 0 or self._current._current_loop_times > 1:
                self._current = self._current._loop_start_node
                self._current._current_loop_times = self._current._current_loop_times - 1
                return node
        self._current = self._current._next
        return node


class Sets(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Sets, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._sets = dict()

    def load_file(self, filename):
        try:
            f = open(filename, "rt")
            rows = []
            while True:
                row = f.readline()
                if row == "":
                    break
                row = row.strip()
                if row.startswith("--") or row.startswith("#"):
                    continue
                row = row.replace(" ", "", -1).replace("\t", "", -1)
            f.close()
        except:
            pass
