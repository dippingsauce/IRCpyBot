import sys
import socket
import string


HOST='irc.digitalwizardry.org' #server for irc
PORT=6667 #port to connect to...no need for ssl its just a bot
NICK='BroBotpy' #bot nick
IDENT='BroBotpy'
SERVERNAME='bawt'
REALNAME='BroBot' #bot real name for whois
OWNER='dippingsauce' #bot owner nick
CHANNELDEF='#thezoo' #default channel for the bot to join
readbuffer= '' #Storage for messages


s=socket.socket( ) #creates a socket
s.connect((HOST, PORT)) #connects to the server
s.send('NICK '+NICK) #sends nick to the server
s.send('USER %s 0 0 :%s' % (IDENT, REALNAME)) #identify with the server

while 1:
    line=s.recv(500) #recieves server messages
    print line #server message output
    if line.find('Welcome')!= -1: #need a better way of doing this
        s.send('JOIN '+CHANNELDEF+'n') #Joins default channel
    if line.find('PRIVMSG') != -1: #channel joined now parse messages
        parsemsg(line)
        line=line.rstrip() #removes trailing 'rn'
        line=line.split()
        if(line[0] == 'PING'): #if server pings then pong
            s.send('PONG '+line[1]+'n')


def parsemsg(msg):
    complete=msg[1:].split(':',1) #Pase the message into useful data
    info=complete[0].split(' ')
    msgpart=complete[1]
    sender=info[0].split('!')
    if msgpart[0] =='.' and sender[0] == OWNER: #using '.' as the command trigger
        cmd=msgpart[1:].split(' ')
