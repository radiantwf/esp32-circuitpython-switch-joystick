import macros
import time
import asyncio
print("hello hori")


async def task_pokemon():
    await macros.run("pokemon.swsh.regirock.regirock", True)


def main():
    print('准备中，5s后运行')
    time.sleep(5)
    print('开始运行')

    import device_info
    print("剩余内存:{:.2f}KB".format(device_info.mem_free()))
    rom = device_info.get_rom_info()
    print("剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1]))

    loop = asyncio.get_event_loop()
    task1 = loop.create_task(task_pokemon())
    loop.run_until_complete(task1)
    loop.close()


if __name__ == '__main__':
    main()
