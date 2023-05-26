# standard libs
import os, sys
import time

# todo good code also on this command:
# path = os.environ["PROJ_DATA"]
# logger.dbug("PROJ data found in package: path=%r.", path)
# see D:\PROJECTS\PY-ENV\Lib\site-packages\fiona\env.py

# app modules
from system_modules.message_logger import logger


class Messenger(dict):

    def __init__(self):
        self._message = {}

    def __repr__(self) -> str:
        pass       
    
    def __getattr__(self, attr):
        while True:
            msgs = self[attr]
            for msg in msgs:
                if not msg:
                    time.sleep(0.1)
                    continue
                yield msg
        return msg

    def __setattr__(self, attr, value):
        if attr in self:
            self[attr].append(value)
        else:  
            self[attr] = value

    def clear_messages(self):
        self.clear()


def start():
    msg = "Starting Messenger\n"
    logger.info(msg)
    global msgr
    msgr = Messenger()
    msgr['msgr'] = msg

    return msgr