import queue
import datetime as dt


# ##################################################################
# MONITOR CLASS
# ##################################################################

class WebsocketMonitor(object):

    def __init__(self):
        self.__intervals = queue.Queue(maxsize=10000)
        self.__timestamp = dt.datetime.utcnow()

    def received(self, message, *args, **kwargs):
        ts = dt.datetime.utcnow()
        self.__intervals.put((ts - self.__timestamp).microseconds)
        self.__timestamp = ts
        return message

    def failed(self, *args, **kwargs):
        pass

