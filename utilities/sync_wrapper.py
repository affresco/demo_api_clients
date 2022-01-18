import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ######################################################################
# ENDPOINTS
# ######################################################################

def grab_event_loop(loop=None):

    if not loop:
        try:
            loop.safe_close()
        except:
            pass
        finally:
            return __grab_new_event_loop()

    if loop.is_closed():
        return __grab_new_event_loop()

    elif not loop.is_running():
        __close_event_loop(loop=loop)
        return __grab_new_event_loop()

    while loop.is_running():
        asyncio.wait(loop=loop, fs=asyncio.Task.all_tasks())
    if not loop.is_closed():
        __close_event_loop(loop=loop)
    return __grab_new_event_loop()


def __close_event_loop(loop):
    try:
        loop.safe_close()
    except:
        logging.warning("Trying to close existing event loop failed.")


def __grab_new_event_loop():
    try:
        return asyncio.new_event_loop()
    except:
        raise Exception("Unable to create an event loop.")


def sync_wrapper(delegate, **kwargs):
    loop = grab_event_loop()
    result = loop.run_until_complete(delegate(**kwargs))
    loop.close()
    return result
