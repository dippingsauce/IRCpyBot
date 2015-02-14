import BotClass
from BotClass import *

class Bot(BotClass):
    def __init__(self):
        BotClass.__init__(self)

    def connect(self):
        super(Bot,self).connect()
        
    def changeNick(self,newNick):
        super(Bot,self).ChangeNick(newNick)

if __name__ == "__main__":
    b = Bot()
    try:
        b.connect()
    except NicknameInUseException:
        b.changeNick('Mandark')
    except TimeoutException:
        print "This shit timed out"