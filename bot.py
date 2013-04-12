import sys
import socket
import string

from configs.config import CONN, USER

def parsemsg(msg):
    complete=msg[1:].split(':',1) #Pase the message into useful data
    info=complete[0].split(' ')
    msgpart=complete[1]
    sender=info[0].split('!')
    # using '.' as the command trigger
    if msgpart[0] == '.' and sender[0] == USER['owner']: 
        cmd = msgpart[1:].split(' ')

def run(conn):
    s = socket.socket() #creates a socket
    s.connect(conn) #connects to the server
    s.send('NICK ' + USER['nick']) #sends nick to the server
    s.send('USER %s 0 0 :%s' % (USER['ident'], USER['realname'])) #identify with the server

    while 1:
        line = s.recv(500) #recieves server messages
        print line #server message output
        if line.find('Welcome')!= -1: #need a better way of doing this
            s.send('JOIN '+CHANNELDEF+'n') #Joins default channel
        if line.find('PRIVMSG') != -1: #channel joined now parse messages
            parsemsg(line)
            line=line.rstrip() #removes trailing 'rn'
            line=line.split()
            if(line[0] == 'PING'): #if server pings then pong
                s.send('PONG '+line[1]+'n')

if __name__ == "__main__":
    conn = (CONN['host'], CONN['port'])
    run(conn)
