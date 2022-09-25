# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019-2020 Damien P. George
#
# This code comes from MicroPython, and has not been run through black or pylint there.
# Altering these files significantly would make merging difficult, so we will not use
# pylint or black.
# pylint: skip-file
# fmt: off
"""
Functions
=========
"""


from . import core


async def wait_for(aw, timeout, sleep=core.sleep):
    """Wait for the *aw* awaitable to complete, but cancel if it takes longer
    than *timeout* seconds. If *aw* is not a task then a task will be created
    from it.

    If a timeout occurs, it cancels the task and raises ``asyncio.TimeoutError``:
    this should be trapped by the caller.

    Returns the return value of *aw*.

    This is a coroutine.
    """

    aw = core._promote_to_task(aw)
    if timeout is None:
        return await aw

    async def runner(waiter, aw):
        nonlocal status, result
        try:
            result = await aw
            s = True
        except BaseException as er:
            s = er
        if status is None:
            # The waiter is still waiting, set status for it and cancel it.
            status = s
            waiter.cancel()

    # Run aw in a separate runner task that manages its exceptions.
    status = None
    result = None
    runner_task = core.create_task(runner(core.cur_task, aw))

    try:
        # Wait for the timeout to elapse.
        await sleep(timeout)
    except core.CancelledError as er:
        if status is True:
            # aw completed successfully and cancelled the sleep, so return aw's result.
            return result
        elif status is None:
            # This wait_for was cancelled externally, so cancel aw and re-raise.
            status = True
            runner_task.cancel()
            raise er
        else:
            # aw raised an exception, propagate it out to the caller.
            raise status

    # The sleep finished before aw, so cancel aw and raise TimeoutError.
    status = True
    runner_task.cancel()
    await runner_task
    raise core.TimeoutError


def wait_for_ms(aw, timeout):
    """Similar to `wait_for` but *timeout* is an integer in milliseconds.

    This is a coroutine, and a MicroPython extension.
    """

    return wait_for(aw, timeout, core.sleep_ms)


async def gather(*aws, return_exceptions=False):
    """Run all *aws* awaitables concurrently. Any *aws* that are not tasks
    are promoted to tasks.

    Returns a list of return values of all *aws*

    This is a coroutine.
    """

    ts = [core._promote_to_task(aw) for aw in aws]
    for i in range(len(ts)):
        try:
            # TODO handle cancel of gather itself
            # if ts[i].coro:
            #    iter(ts[i]).waiting.push_head(cur_task)
            #    try:
            #        yield
            #    except CancelledError as er:
            #        # cancel all waiting tasks
            #        raise er
            ts[i] = await ts[i]
        except Exception as er:
            if return_exceptions:
                ts[i] = er
            else:
                raise er
    return ts
