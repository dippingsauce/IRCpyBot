import sys
import socket
import string
import errno
import threading
import time
import Queue

from configs.config import CONN, USER, FLOOD

class BotClass(object):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_print_queue = Queue.Queue(maxsize=0)
    irc_flood_timeout_queue = Queue.Queue(maxsize=0)
    
    def __init__(self):
        irc_print_commit = threading.Thread(target=self.irc_print_commit)
        irc_print_commit.daemon = True
        irc_print_commit.start()
        self.conn = (CONN['host'], CONN['port'])
        
    def parsemsg(self,msg):
        complete=msg[1:].split(':',1) #Pase the message into useful data
        info=complete[0].split(' ')
        msgpart=complete[1]
        sender=info[0].split('!')
        # using '.' as the command trigger
        if msgpart[0] == '.' and sender[0] == USER['owner']: 
            cmd = msgpart[1:].split(' ')

    def join(self):
        time.sleep(10) #wait for 10secs
        self.sock.send('JOIN ' + CONN['channel'] + '\n') #Joins default channel
        
    def irc_print(self,line):
        self.irc_print_queue.put(line)

    def now_ms(self):
        return int(round(time.time() * 1000))

    def get_flood_timeout(self):
        return (float(FLOOD['flood_time'] + self.now_ms()))
        
    def irc_print_commit(self):
        while True:
            line = self.irc_print_queue.get()
            if self.irc_flood_timeout_queue.empty() == False:        
                timeout=self.irc_flood_timeout_queue.queue[0]
                if self.now_ms() >= timeout:
                    timeout = self.irc_flood_timeout_queue.get()
                    #print "Timeout expired: " + str(int(timeout))
                    continue
                    
            if self.irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
                timeout=((self.get_flood_timeout()-self.now_ms())/1000)
                if timeout < 0:
                    print 'Invalid timeout: ' + str(int(timeout))
                    break
                print "anti flood triggered"
                print "message queue size: " + str(self.irc_print_queue.qsize())
                print "waiting for " + str(timeout) +"s"
                time.sleep(timeout)

            self.sock.send("PRIVMSG " + CONN['channel'] + " :" + line + "\n")
            self.irc_flood_timeout_queue.put(self.get_flood_timeout())
            
    def connect(self):
        self.sock.connect(self.conn) #connects to the server

        while 1:
            line = self.sock.recv(1024) #recieves server messages
            if line: # only print meaningful stuff
                msg=line.rstrip() #removes trailing 'rn'
                print msg #server message output
                if line.find('Found your hostname')!= -1:
                    print 'Sending IDENT'    
                    self.sock.send('NICK ' + USER['nick'] + '\n') #sends nick to the server
                    self.sock.send('USER %s 0 0 :%s\n' % (USER['ident'], USER['realname'])) #identify with the server
                    JoinThread = threading.Thread(target=self.join)
                    JoinThread.daemon = True
                    JoinThread.start()
                elif line.find('PING :')!= -1:
                    print 'Sending PONG'
                    self.parsemsg(line)
                    line=line.rstrip() #removes trailing 'rn'
                    line=line.split()
                    if(line[0] == 'PING'): #if server pings then pong
                        self.sock.send('PONG '+line[1]+'\r\n')
                elif line.find('Nickname is already in use') != -1:
                    raise NicknameInUseError("The Nickname you chose is already in use.")
                elif line.find('ERROR')!= -1:
                    print "That's an error"
                    self.sock.close()
                    sys.exit() #Die on errors                        
                elif line.find('PRIVMSG') != -1: #channel joined now parse messages
                    self.parsemsg(line)
                    line=line.rstrip() #removes trailing 'rn'
                    line=line.split()
                    if line[3].find(':DaxBot!')!= -1:
                        print 'That\'s a command'
                        if line[0].find('ValliusDax')!= -1:
                            self.irc_print("Yes, Master?")
                        else:
                            self.irc_print("You're not the Master!")

class NicknameInUseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

