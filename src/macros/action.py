from macros import macro, config


class Action(object):
    def __init__(self, macro_name: str):
        self._macro = macro.Macro()
        self._config = config.Config()
        self._head = self._macro.get_node(macro_name)
        self._current = self._head
        self._current_node_link_cycle_times = 1
        self._waiting_node = []
        self._body = self._head
        self._body_current_node_link_cycle_times = 1
        self._body_waiting_node = []

    def _jump_node(self):
        action_line = self._current.action
        if not action_line.startswith("["):
            return False
        splits = action_line.split("]")
        key = splits[0][1:]
        times = 0

        s1 = splits[1].split("?")
        if len(s1) == 2:
            if self._config.check(s1[1]):
                times = 1
        else:
            s2 = splits[1].split("*")
            try:
                times = int(s2[1])
            except:
                times = 1
        node = self._macro.get_node(key)
        if node != None and times >= 1:
            self._waiting_node.append(
                [self._current.next, self._current_node_link_cycle_times])
            self._current = node
            self._current_node_link_cycle_times = times
            return True
        return False

    def _return_jump(self):
        if self._current != None:
            return
        if self._current_node_link_cycle_times > 1:
            self._current = self._current.head
            self._current_node_link_cycle_times -= 1
            return
        elif len(self._waiting_node) > 0:
            ret = self._waiting_node.pop()
            self._current = ret[0]
            self._current_node_link_cycle_times = ret[1]
            if self._current == None:
                self._return_jump()

    def pop(self):
        line: str = None
        is_finish = False
        if self._current == None:
            return None, True
        while self._jump_node():
            pass
        line = self._current.action
        if line == "body:":
            self._current = self._current.next
            self._return_jump()
            if self._current == None:
                return None, True
            line = self._current.action
            self._body = self._current
            self._body_current_node_link_cycle_times = self._current_node_link_cycle_times
            self._body_waiting_node = []
            for row in self._waiting_node:
                self._body_waiting_node.append(row)
        self._current = self._current.next
        self._return_jump()
        if self._current == None:
            is_finish = True
        return line, is_finish

    def reset(self):
        self._current = self._head
        self._current_node_link_cycle_times = 1
        self._waiting_node = []

    def do_cycle(self):
        self._current = self._body
        self._current_node_link_cycle_times = self._body_current_node_link_cycle_times
        self._waiting_node = []
        for row in self._body_waiting_node:
            self._waiting_node.append(row)
