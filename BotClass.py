import sys
import socket
import string
import errno
import threading

from configs.config import CONN, USER

class BotClass(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def __init__(self):
        self.conn = (CONN['host'], CONN['port'])
        self.isConnected = False
        
    def parsemsg(self,msg):
        complete=msg[1:].split(':',1) #Parse the message into useful data
        info=complete[0].split(' ')
        msgpart=complete[1]
        sender=info[0].split('!')
        # using '.' as the command trigger
        if msgpart[0] == '.' and sender[0] == USER['owner']: 
            cmd = msgpart[1:].split(' ')

    def connect(self):
        try:
            self.sock.connect(self.conn) #connects to the server
            
            while True:
     
                try:
                    line = self.sock.recv(1024) #receives server messages
                    self.isConnected = True
                    if line: # only print meaningful stuff
                        print line #server message output
                        if line.find('Found your hostname')!= -1:
                            print 'Sending IDENT'    
                            self.sock.send('NICK ' + USER['nick'] + '\n') #sends nick to the server
                            self.sock.send('USER %s 0 0 :%s\n' % (USER['ident'], USER['realname'])) #identify with the server
                        elif line.find('PING :')!= -1:
                            print 'Sending PONG'
                            self.parsemsg(line)
                            line=line.rstrip() #removes trailing 'rn'
                            line=line.split()
                            if(line[0] == 'PING'): #if server pings then pong
                                self.sock.send('PONG '+line[1]+'\r\n')
                        elif line.find('Nickname is already in use') != -1:
                            raise NicknameInUseException("The Nickname you chose is already in use.")
                        elif line.find('ERROR')!= -1:
                            print "That's an error"
                            self.sock.close()
                            sys.exit() #Die on errors                        
                        elif line.find('PRIVMSG') != -1: #channel joined now parse messages
                            self.parsemsg(line)
                            line=line.rstrip() #removes trailing 'rn'
                            line=line.split()
                            print line
    
                except socket.timeout:
                    self.isConnected = False
                    raise TimeoutException
        except socket.gaierror:
            print "Address-related error. Make sure the host is connectible"

    def ChangeNick(self,newNick):
        if self.isConnected == True:
            print "Changing Nickname to " + newNick
            self.sock.send('NICK ' + newNick + '\n')
        
        
class NicknameInUseException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class TimeoutException(Exception):
    pass

