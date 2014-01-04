import BotClass
from BotClass import *

class Bot(BotClass):
    def __init__(self):
        BotClass.__init__(self)

    def connect(self):
        super(Bot,self).connect()

if __name__ == "__main__":
    b = Bot()
    try:
        b.connect()
    except NicknameInUseError as e:
        print e.value
    
