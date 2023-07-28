def get_rom_info():
    import os
    statvfs_fields = ['bsize', 'frsize', 'blocks',
                      'bfree', 'bavail', 'files', 'ffree', ]
    info = dict(zip(statvfs_fields, os.statvfs('/')))
    return info['bsize'] * info['bfree'] / 1024 / 1024, info['bsize'] * info['blocks'] / 1024 / 1024


def mem_free():
    import gc
    m = gc.mem_free() / 1024
    return m

def cpu_temperature():
    import microcontroller
    try:
        return microcontroller.cpu.temperature
    except:
        return 0