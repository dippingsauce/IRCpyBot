import BotClass
import Queue
from BotClass import *
from BotUI import *

        
class Bot(BotClass):
    def __init__(self):
        BotClass.__init__(self)
        try:
           IRC_THREAD = threading.Thread(target=self.connect)
           IRC_THREAD.daemon = True
           IRC_THREAD.start()
        except NicknameInUseError as e:
            print e.value
        except KeyboardInterrupt:
            print "Closing"
        ui = BotUI(super(Bot,self).ui_console_queue)

    def connect(self):
        super(Bot,self).connect()

if __name__ == "__main__":
    irc = Bot()
    
