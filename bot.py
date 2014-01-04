import sys
import socket
import string
import errno
import threading

from configs.config import CONN, USER

class NicknameInUseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
def parsemsg(msg):
    complete=msg[1:].split(':',1) #Pase the message into useful data
    info=complete[0].split(' ')
    msgpart=complete[1]
    sender=info[0].split('!')
    # using '.' as the command trigger
    if msgpart[0] == '.' and sender[0] == USER['owner']: 
        cmd = msgpart[1:].split(' ')

def run(conn):
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates a socket
    irc.connect(conn) #connects to the server
    
    while 1:
        line = irc.recv(1024) #recieves server messages
        if line: # only print meaningful stuff
            print line #server message output
            if line.find('Found your hostname')!= -1:
                print 'Sending IDENT'    
                irc.send('NICK ' + USER['nick'] + '\n') #sends nick to the server
                irc.send('USER %s 0 0 :%s\n' % (USER['ident'], USER['realname'])) #identify with the server
            elif line.find('PING :')!= -1:
                print 'Sending PONG'
                parsemsg(line)
                line=line.rstrip() #removes trailing 'rn'
                line=line.split()
                if(line[0] == 'PING'): #if server pings then pong
                    irc.send('PONG '+line[1]+'\r\n')
            elif line.find('Nickname is already in use') != -1:
                raise NicknameInUseError("The Nickname you chose is already in use.")
            elif line.find('ERROR')!= -1:
                print "That's an error"
                irc.close()
                sys.exit() #Die on errors                        
            elif line.find('PRIVMSG') != -1: #channel joined now parse messages
                parsemsg(line)
                line=line.rstrip() #removes trailing 'rn'
                line=line.split()
                print line
                

if __name__ == "__main__":
    conn = (CONN['host'], CONN['port'])
    run(conn)
