import sys
import socket
import string
import errno
import threading
import time
import datetime
import Queue

from configs.config import CONN, USER, FLOOD, STAT

class BotClass(object):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_print_queue = Queue.Queue(0)
    irc_flood_timeout_queue = Queue.Queue(0)
    ui_console_queue = Queue.Queue(0)
    ui_status_queue = Queue.Queue(0)

    def __init__(self):
        irc_print_commit = threading.Thread(target=self.irc_print_commit)
        irc_print_commit.daemon = True
        irc_print_commit.start()
        self.ui_console_queue.put("Bot starting")
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
        self.ui_console_queue.put("Joining " + CONN['channel'])
        self.sock.send('JOIN ' + CONN['channel'] + '\n') #Joins default channel

    def irc_print(self,line):
        self.irc_print_queue.put(line)

    def now_ms(self):
        return int(round(time.time() * 1000))

    def get_flood_timeout(self):
        return (float(FLOOD['flood_time'] + self.now_ms()))

    def irc_print_commit(self):
        IRC_MESSAGES=0
        try:
            while True:
                if self.irc_flood_timeout_queue.empty() == False:
                    timeout=self.irc_flood_timeout_queue.queue[0]
                    if self.now_ms() >= timeout:
                        timeout = self.irc_flood_timeout_queue.get()
                        #self.ui_console_queue.put("Timeout expired: " + str(int(timeout)))
                        continue

                if self.irc_print_queue.empty() == False:
                    line = self.irc_print_queue.get()
                    if self.irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
                        timeout=((self.get_flood_timeout()-self.now_ms())/1000)
                        if timeout < 0:
                            self.ui_console_queue.put('Invalid timeout: ' + str(int(timeout)))
                            break
                        self.ui_console_queue.put("anti flood triggered")
                        self.ui_console_queue.put("message queue size: " + str(self.irc_print_queue.qsize()))
                        self.ui_console_queue.put("waiting for " + str(timeout) +"s")
                        time.sleep(timeout)                    
                    else:
                        IRC_MESSAGES+=1
                        self.ui_status_queue.put((STAT['irc_messages'],IRC_MESSAGES))
                        self.sock.send("PRIVMSG " + CONN['channel'] + " :" + line + "\n")
                        self.irc_flood_timeout_queue.put(self.get_flood_timeout())
        except KeyboardInterrupt:
            exit()

    def connect(self):
        self.ui_console_queue.put("Connecting to " + str(self.conn))
        self.sock.connect(self.conn) #connects to the server
        PINGS=0
        

        while 1:
            line = self.sock.recv(1024) #recieves server messages
            if line: # only print meaningful stuff
                # msg=line.rstrip() #removes trailing 'rn'
                # self.ui_console_queue.put(msg) #server message output
                # print msg
                if line.find('Found your hostname')!= -1:
                    self.ui_console_queue.put('Sending IDENT')
                    self.sock.send('NICK ' + USER['nick'] + '\n') #sends nick to the server
                    self.sock.send('USER %s 0 0 :%s\n' % (USER['ident'], USER['realname'])) #identify with the server
                    JoinThread = threading.Thread(target=self.join)
                    JoinThread.daemon = True
                    JoinThread.start()
                elif line.find('PING :')!= -1:
                    self.ui_console_queue.put('Got PING')
                    self.parsemsg(line)
                    line=line.rstrip() #removes trailing 'rn'
                    line=line.split()
                    if(line[0] == 'PING'): #if server pings then pong
                        PINGS+=1
                        self.ui_status_queue.put((STAT['ping'],PINGS))
                        self.ui_status_queue.put((STAT['ping_time'],datetime.datetime.now()))
                        self.ui_console_queue.put('Sending PONG')
                        self.sock.send('PONG '+line[1]+'\r\n')
                elif line.find('Nickname is already in use') != -1:
                    raise NicknameInUseError("The Nickname you chose is already in use.")
                elif line.find('ERROR')!= -1:
                    self.ui_console_queue.put("That's an error")
                    self.sock.close()
                    sys.exit() #Die on errors
                elif line.find('PRIVMSG') != -1: #channel joined now parse messages
                    self.parsemsg(line)
                    line=line.rstrip() #removes trailing 'rn'
                    line=line.split()
                    command=line[3][1:]
                    if command == 'DaxBot!'!= -1:
                        self.ui_console_queue.put("Got Command: " + command)
                        if line[0].find('ValliusDax')!= -1:
                            self.irc_print("Yes, Master?")
                        else:
                            self.irc_print("You're not the Master!")

class NicknameInUseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

