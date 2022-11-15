from . import macro,paras


class Action(object):
    def __init__(self, macro_name: str,in_paras:dict = dict()):
        self._macro = macro.Macro()
        n = self._macro.get_node(macro_name)
        self._head = n[0]
        self._paras = paras.Paras(n[1],in_paras)
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
        if splits[1].startswith("?"):
            if self._paras.get_bool(splits[1][1:]):
                times = 1
        elif splits[1].startswith("*"):
            times = self._paras.get_int(splits[1][1:])
        else:
            times = 1
        n = self._macro.get_node(key)
        node = n[0]
        if node.action != macro._FINISHED_LINE and times >= 1:
            self._waiting_node.append(
                [self._current.next, self._current_node_link_cycle_times])
            self._current = node
            self._current_node_link_cycle_times = times
            return True
        elif self._current != macro._FINISHED_LINE and times < 1:
            self._current = self._current.next
            return True
        return False

    def _return_jump(self):
        if self._current.action != macro._FINISHED_LINE:
            return
        if self._current_node_link_cycle_times > 1:
            self._current = self._current.head
            self._current_node_link_cycle_times -= 1
            return
        elif len(self._waiting_node) > 0:
            ret = self._waiting_node.pop()
            self._current = ret[0]
            self._current_node_link_cycle_times = ret[1]
            
            if self._current.action == macro._FINISHED_LINE:
                self._return_jump()

    def pop(self):
        line: str = None
        is_finish = False
        if self._current == None or self._current.action == macro._FINISHED_LINE:
            return None, True
        while True:
            while self._jump_node():
                pass
            line = self._current.action
            if line == "body:":
                self._current = self._current.next
                self._return_jump()
                if self._current.action == macro._FINISHED_LINE:
                    return None, True
                line = self._current.action
                self._body = self._current
                self._body_current_node_link_cycle_times = self._current_node_link_cycle_times
                self._body_waiting_node = []
                for row in self._waiting_node:
                    self._body_waiting_node.append(row)
                continue
            elif line.startswith("EXEC>"):
                self._paras.exec_str(line[5:])
                self._current = self._current.next
                self._return_jump()
                if self._current.action == macro._FINISHED_LINE:
                    return None, True
                line = self._current.action
                continue
            else:
                break
        if self._current.action == macro._FINISHED_LINE:
            is_finish = True
            line = None
        else:
            self._current = self._current.next
            self._return_jump()
        return line, is_finish

    def reset(self):
        self._current = self._head
        self._current_node_link_cycle_times = 1
        self._waiting_node = []

    def cycle_reset(self):
        self._current = self._body
        self._current_node_link_cycle_times = self._body_current_node_link_cycle_times
        self._waiting_node = []
        for row in self._body_waiting_node:
            self._waiting_node.append(row)
