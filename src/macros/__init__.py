from macros import action
import hid.joystick
import usb_hid

joystick = hid.joystick.JoyStick(usb_hid.devices)


async def run(name: str, cycle: bool = False):
    act = _get_action(name)
    if act == None:
        return
    while True:
        while True:
            ret = act.pop()
            # print(ret[0])
            await joystick.do_action(ret[0])
            if ret[1]:
                break
        if not cycle:
            break
        act.do_cycle()


def _get_action(name: str) -> action.Action:
    act = action.Action(name)
    if act._head == None:
        return None
    return act
