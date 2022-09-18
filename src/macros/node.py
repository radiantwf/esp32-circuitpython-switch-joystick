class Node(object):
    def __init__(self, action_line: str):
        self._head: Node = self
        self._next: Node = None
        self._action_line: str = action_line

    def append(self, action_line: str):
        node = self
        while True:
            if node._next == None:
                break
            else:
                node = node._next
        node._next = Node(action_line)
        node._next._head = node._head
        return node._next

    @property
    def head(self):
        return self._head

    @property
    def next(self):
        return self._next

    @property
    def action(self):
        return self._action_line
