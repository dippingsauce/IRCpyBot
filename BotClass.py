import sys
import socket
import string
import errno
import os
import threading
import time
import datetime
import Queue
import pickle

from random import choice
from configs.config import CONN, USER, FLOOD, STAT

class BotClass(object):

    masters = [USER['owner']]
    insults = ['fuck you', 'you are a cum guzzling slut', 'is a fishbot', 'takes it in the ass']
    ignore  = ['drew86']
    attacks = ['slaps with fish']
    confirm_messages = ['Of course master!', 'Your will is my command master!', 'I shall obey, master!']
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_messages = Queue.Queue(0)
    irc_print_queue = Queue.Queue(0)
    irc_notice_queue = Queue.Queue(0)
    irc_raw_queue = Queue.Queue(0)
    irc_flood_timeout_queue = Queue.Queue(0)
    ui_console_queue = Queue.Queue(0)
    ui_status_queue = Queue.Queue(0)
    warned_users = []
    cautioned_users = []
    waiting_for_response = False;
    channel_count=0
    names_list = ""
    silent     = False
    nice       = True
    annoying   = False
    nasty      = False
    vindictive = False
    display_result = True
    random_kick = False
    verbose_console = True
    site = { 'status': "blah",
             'eta'   : "blah",
             'reason': "blah"
             }

    def __init__(self):
        irc_print_commit = threading.Thread(target=self.irc_print_commit)
        irc_print_commit.daemon = True
        irc_print_commit.start()

        try:
          masters_db=open('masters','r')
          self.masters=pickle.load(masters_db)
          masters_db.close()
        except IOError:
          masters_db=open('masters','w')
          pickle.dump(self.masters, masters_db)
          masters_db.close()

        try:
          insults_db=open('insults','r')
          self.insults=pickle.load(insults_db)
          insults_db.close()
        except IOError:
          insults_db=open('insults','w')
          pickle.dump(self.insults, insults_db)
          insults_db.close()

        try:
          ignore_db=open('ignore','r')
          self.ignore=pickle.load(ignore_db)
          ignore_db.close()
        except IOError:
          ignore_db=open('ignore','w')
          pickle.dump(self.ignore, ignore_db)
          ignore_db.close()

        try:
          status_db=open('status','r')
          self.site=pickle.load(status_db)
          status_db.close()
        except IOError:
          status_db=open('status','w')
          pickle.dump(self.site, status_db)
          status_db.close()

        self.ui_console_queue.put("Bot starting")
        self.conn = (CONN['host'], CONN['port'])

    def parsemsg(self,msg):
        complete=msg[1:].split(':',1) #Parse the message into useful data
        info=complete[0].split(' ')
        msgpart=complete[1]
        sender=info[0].split('!')
        # using '.' as the command trigger
        if msgpart[0] == '.' and sender[0] == USER['owner']:
            cmd = msgpart[1:].split(' ')

    def join(self):
        time.sleep(10)
        self.ui_console_queue.put("Joining " + CONN['channel'])
        self.sock.send('JOIN ' + CONN['channel'] + '\n') #Joins default channel
#        while True:
            # try:
#                time.sleep(10) #wait for 10secs
#                self.ui_console_queue.put("Checking I'm in the channel")
#                self.sock.send('JOIN ' + CONN['channel'] + '\n') #Joins default channel
#                time.sleep(10) #wait for another 10secs
            # finally:
                # self.sock.send('QUIT I got killed\n') #Joins default channel
                # exit()

    def irc_print(self,line):
      if not self.silent:
        self.irc_print_queue.put(line)

    def irc_notice(self,line):
      self.irc_notice_queue.put(line)

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

          if self.irc_notice_queue.empty() == False:
            line = self.irc_notice_queue.get()
#            if self.irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
#              timeout=((self.get_flood_timeout()-self.now_ms())/1000)
#              if timeout < 0:
#                self.ui_console_queue.put('Invalid timeout: ' + str(int(timeout)))
#                break
#              self.ui_console_queue.put("anti flood triggered")
#              self.ui_console_queue.put("message queue size: " + str(self.irc_print_queue.qsize() + self.irc_notice_queue.qsize()))
#              self.ui_console_queue.put("waiting for " + str(timeout) +"s")
#              time.sleep(timeout)
#             else:
            IRC_MESSAGES+=1
            self.ui_status_queue.put((STAT['irc_messages'],IRC_MESSAGES))
            self.sock.send("NOTICE " + line + "\n")
#                self.irc_flood_timeout_queue.put(self.get_flood_timeout())

          if self.irc_print_queue.empty() == False:
            line = self.irc_print_queue.get()
            if self.irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
              timeout=((self.get_flood_timeout()-self.now_ms())/1000)
              if timeout < 0:
                self.ui_console_queue.put('Invalid timeout: ' + str(int(timeout)))
                break
              self.ui_console_queue.put("anti flood triggered")
              self.ui_console_queue.put("message queue size: " + str(self.irc_print_queue.qsize() + self.irc_notice_queue.qsize()))
              self.ui_console_queue.put("waiting for " + str(timeout) +"s")
              time.sleep(timeout)
            else:
              IRC_MESSAGES+=1
              self.ui_status_queue.put((STAT['irc_messages'],IRC_MESSAGES))
              self.sock.send("PRIVMSG " + CONN['channel'] + " :" + line + "\n")
              self.irc_flood_timeout_queue.put(self.get_flood_timeout())

          if self.irc_raw_queue.empty() == False:
            line = self.irc_raw_queue.get()
            self.sock.send(line + '\n')

      except KeyboardInterrupt:
        exit()

    def confirm(self):
      self.irc_print(choice(self.confirm_messages))

    def listen(self):
      while 1:
        line = self.sock.recv(8192)
        self.irc_messages.put(line)

    def connect(self):
      self.ui_console_queue.put("Connecting to " + str(self.conn))
      self.sock.connect(self.conn) #connects to the server
      PINGS=0
      ME=USER['nick']+'!'

      ListenThread = threading.Thread(target=self.listen)
      ListenThread.daemon = True
      ListenThread.start()

      while 1:
        msg = self.irc_messages.get() # recieves server messages
        msg=msg.split('\n')
        for line in msg:
          line=line.rstrip() # removes trailing 'rn'
          if line: # only print meaningful stuff
            if self.verbose_console:
              self.ui_console_queue.put(line) #server message output
            if line.find('PRIVMSG') == -1:
              if line.find('Found your hostname')!= -1:
                self.ui_console_queue.put('Sending IDENT')
                self.irc_raw_queue.put('NICK ' + USER['nick'] + '\n') #sends nick to the server
                self.irc_raw_queue.put('USER %s 0 0 :%s\n' % (USER['ident'], USER['realname'])) #identify with the server
                JoinThread = threading.Thread(target=self.join)
                JoinThread.daemon = True
                JoinThread.start()
              elif line.find('identify to your nickname')!= -1:
                self.irc_raw_queue.put('IDENTIFY %s\n' % (USER['password'],))
              elif line.find('PING')!= -1:
 #               if self.verbose_console:
                self.ui_console_queue.put('Got PING')
                PINGS = PINGS + 1
                self.ui_status_queue.put((STAT['ping'],PINGS))
                self.ui_status_queue.put((STAT['ping_time'],datetime.datetime.now()))
#                if self.verbose_console:
                self.ui_console_queue.put('Sending PONG')
                self.sock.send('PONG '+line[1]+'\r\n')
              elif line.find('Nickname is already in use') != -1:
                self.irc_raw_queue.put('GHOST %s %s\n' % (USER['nick'],USER['password']))#doesn't work :(
                self.irc_raw_queue.put('NICK ' + USER['nick'] + '\n')
              elif line.find('ERROR')!= -1:
                self.ui_console_queue.put("That's an error")
                rline=line.rstrip()
                self.ui_console_queue.put(rline)
#                self.sock.close()
#                sys.exit() #Die on errors
              elif line.find('KICK') != -1:
                line=line.rstrip() #removes trailing 'rn'
                line=line.split()
                msg = line[3] + " got kicked"
                self.ui_console_queue.put(msg)
#                self.ui_console_queue.put(line)
                if line[3] == USER['nick']:
                    self.ui_console_queue.put("Hey, That's me!")
#                    JoinThread = threading.Thread(target=self.join)
#                    JoinThread.daemon = True
#                    JoinThread.start()

                elif line.find("%s = %s" % (USER['nick'], CONN['channel'])) != -1: #channel names
                  if self.waiting_for_response:
                    rline=line.rstrip('\n') #removes trailing 'rn'
                    self.names_list=self.names_list+rline

                    if line.find(':End of /NAMES list.')!= -1:
                      sline=self.names_list.split()
                      kline=self.names_list.split(':')
                      kline=kline[2].split()
                      self.names_list=""
                      self.waiting_for_response = False

                      if self.random_kick:
                        while True:
                          victim = choice(kline[1:])
                          if victim == USER['owner']:
                            continue
                          elif victim == USER['nick']:
                            continue
                          else:
                            break

                        if any(victim[0] == s for s in ['~', '@', '&', '%', '+']):
                          victim = victim[1:]
                          self.irc_raw_queue.put('KICK %s %s dances on your grave\n' % (CONN['channel'],victim))
                          self.random_kick = False
                        else:
                          self.irc_print('No kicking!')


                      if self.display_result:
                        self.channel_count = self.channel_count + len(sline)
                        self.channel_count = self.channel_count + sum(-5 for i in sline if i == '=')

                        self.irc_print("Current users in channel: " + str(self.channel_count-8))
                        self.channel_count = 0


            elif line.find('PRIVMSG') != -1: #channel joined now parse messages
              self.parsemsg(line)
              rline=line.rstrip() #removes trailing 'rn'
              dline=rline.split(':')
              dline=''.join(dline[2:])
              sline=rline.split()
              pline=' '.join(sline[3:])
              pline=pline[1:]
              bline=sline[0][:].split("!")
              user=bline[0][1:]
              command=sline[3][1:]
              if any(user == s for s in self.ignore):
                self.ui_console_queue.put("I am ignoring " + user)
                continue
              if (line.lower().find(USER['nick'].lower()) != -1) and (line.lower().find('bot') != -1):
                self.irc_print('No! I\'m a ballerina')
              if len(sline) >= 4:
                arguments=sline[4:]
              if command == ME != -1:
                self.ui_console_queue.put("Got Command: " + pline + " from " + user)
                if any(user == s for s in self.masters):

                  numargs=len(arguments)
                  if numargs == 0:
                    self.irc_print('Yeeees, ' + user + '?')
                  elif (arguments[0] == 'add' != -1) and (numargs > 1):
                    if (arguments[1] == 'master' != -1) and (numargs > 2):
                      self.masters.append(arguments[2])
                      masters_db=open('masters','w')
                      pickle.dump(self.masters, masters_db)
                      masters_db.close()
                      self.irc_print(arguments[2] + " is now one of my masters")
                    if (arguments[1] == 'insult' != -1) and (numargs > 2):
                      self.insults.append(' '.join(arguments[2:]))
                      insults_db=open('insults','w')
                      pickle.dump(self.insults, insults_db)
                      insults_db.close()
                      self.confirm()
                    if (arguments[1] == 'ignore' != -1) and (numargs > 2):
                      if (arguments[2] != USER['owner']  != -1):
                        self.ignore.append(arguments[2])
                        ignore_db=open('ignore','w')
                        pickle.dump(self.ignore, ignore_db)
                        ignore_db.close()
                        self.confirm()

                  elif (arguments[0] == 'list' != -1) and (numargs > 1):
                    if (arguments[1] == 'masters' != -1) and (numargs > 1):
                      for i , val in enumerate(self.masters):
                        self.irc_notice(user + ' ' + self.masters[i])
                    if (arguments[1] == 'insults' != -1) and (numargs > 1):
                      for i , val in enumerate(self.insults):
                        self.irc_notice(user + ' ' + self.insults[i])
                    if (arguments[1] == 'ignore' != -1) and (numargs > 1):
                      for i , val in enumerate(self.ignore):
                        self.irc_notice(user + ' ' + self.ignore[i])

                  elif (arguments[0] == 'forget' != -1) and (numargs > 1):
                    if (arguments[1] == 'master' != -1) and (numargs > 1):
                      if (arguments[2] != USER['owner']  != -1):
                        if arguments[2] in self.masters:
                          self.masters.remove(arguments[2])
                          masters_db=open('masters','w')
                          pickle.dump(self.masters, masters_db)
                          masters_db.close()
                          self.irc_print(arguments[2] + " is no longer one of my masters")
                    if (arguments[1] == 'insult' != -1) and (numargs > 1):
                      if arguments[2:] in self.insults:
                        self.insults.remove(arguments[2:])
                        insults_db=open('insults','w')
                        pickle.dump(self.insults, insults_db)
                        insults_db.close()
                        self.irc_print(arguments[2:] + " forgotten")
                    if (arguments[1] == 'ignore' != -1) and (numargs > 1):
                      if arguments[2] in self.ignore:
                        self.ignore.remove(arguments[2])
                        ignore_db=open('ignore','w')
                        pickle.dump(self.ignore, ignore_db)
                        ignore_db.close()
                        self.irc_print(arguments[2] + " I'm listening")

                  elif (arguments[0] == 'insult' != -1) and (numargs > 1):
                    if (arguments[1] != USER['owner'] != -1) and (numargs > 1):
                      self.irc_print(arguments[1] + " " + choice(self.insults))

                  elif (arguments[0] == 'attack' != -1) and (numargs > 1):
                    if (arguments[1] != USER['owner'] != -1) and \
                       (arguments[1] != USER['nick']  != -1) and \
                       (numargs > 1) and not self.nice:
                          self.irc_raw_queue.put('KICK %s %s dances on your grave\n' % (CONN['channel'],arguments[1]))

                  elif (arguments[0] == 'tldr' != -1) and (numargs > 1):
                    if (arguments[1] == 'set' != -1) and (numargs > 2):
                      if (arguments[2] == 'status' != -1) and (numargs > 3):
                        self.site['status'] = ' '.join(arguments[3:])
                      elif (arguments[2] == 'eta' != -1) and (numargs > 3):
                        self.site['eta'] = ' '.join(arguments[3:])
                      elif (arguments[2] == 'reason' != -1) and (numargs > 3):
                        self.site['reason'] = ' '.join(arguments[3:])
                      status_db=open('status','w')
                      pickle.dump(self.site, status_db)
                      status_db.close()

                  elif (arguments[0] == 'goto' != -1) and (numargs > 1):
                    self.irc_print('bye bye')
                    old_chan = CONN['channel']
                    CONN['channel']=arguments[1]
                    self.irc_raw_queue.put('PART ' + old_chan + '\n')

                  elif (arguments[0] == 'dance!' != -1):
                    if (user == USER['owner']  != -1):
                      if not self.waiting_for_response:
                        self.display_result = False
                        self.random_kick = True
                        self.waiting_for_response = True
                        self.sock.send('NAMES ' + CONN['channel'] + '\n') #Joins default channel
                    else:
                      self.irc_print('Fuck off ' + user +'!')

                  elif (arguments[0] == 'mood?' != -1):
                    if self.nice:
                      self.irc_notice(user + ' I\'m being nice.')
                    elif self.annoying:
                      self.irc_notice(user + ' I\'m being annoying.')
                    elif self.nasty:
                      self.irc_notice(user + ' I\'m being nasty.')
                    elif self.vindictive:
                      self.irc_notice(user + ' I\'m being vindictive.')
                    else:
                      self.irc_notice(user + ' I\'m being random (aka, mood not known).')

                  elif (arguments[0] == 'shutup!' != -1):
                    self.silent = True

                  elif (arguments[0] == 'sing!' != -1):
                    self.silent = False

                  elif (arguments[0] == 'nice!' != -1):
                    self.nice       = True
                    self.annoying   = False
                    self.nasty      = False
                    self.vindictive = False


                  elif (arguments[0] == 'annoying!' != -1):
                    self.nice       = False
                    self.annoying   = True
                    self.nasty      = False
                    self.vindictive = False


                  elif (arguments[0] == 'nasty!' != -1):
                    self.nice       = False
                    self.annoying   = False
                    self.nasty      = True
                    self.vindictive = False


                  elif (arguments[0] == 'vindictive!' != -1):
                    self.nice       = False
                    self.annoying   = False
                    self.nasty      = False
                    self.vindictive = True

                  elif (arguments[0] == 'commands' != -1):
                      self.irc_notice(user + ' Commands: list {masters|insults|ignore}')
                      self.irc_notice(user + '           add {master|insult|ignore} <username or insult>')
                      self.irc_notice(user + '           forget {master|insult|ignore} <username or insult>')
                      self.irc_notice(user + '           insult <username>')
                      self.irc_notice(user + '           attack <username>')
                      self.irc_notice(user + '           tldr{set} {site|status|eta} <info>')
                      self.irc_notice(user + '           goto <channel>')
                      self.irc_notice(user + '           shutup!')
                      self.irc_notice(user + '           sing!')
                      self.irc_notice(user + '           dance!')
                      self.irc_notice(user + '           nice!')
                      self.irc_notice(user + '           annoying!')
                      self.irc_notice(user + '           nasty!')
                      self.irc_notice(user + '           vindictive!')
                      self.irc_notice(user + '           mood?')
                      self.irc_notice(user + '           commands')

                  else:
                    self.irc_print('Huh?')

                else:
                  self.irc_print("You're not the Master!")

              elif user.find("Digital")!= -1:

                if user in self.cautioned_users and not self.nice:
                  self.ui_console_queue.put('Kicked ' + user)
                  self.irc_raw_queue.put('KICK %s %s dances on your grave\n' % (CONN['channel'],user))
                if not self.vindictive:
                  self.cautioned_users.remove(user);
                elif user in self.warned_users and self.nasty:
                  self.irc_notice(user + ' Hey, ' + user + ' last warning, change your nick! type \"/nick your name\" ')
                  self.cautioned_users.append(user);
                  self.warned_users.remove(user);
                elif self.annoying:
                  self.irc_notice(user + ' Hey, ' + user + ' could you use your empornium username please, just type \"/nick your name\" ')
                  self.warned_users.append(user);

                elif rline.find("prettiest mod")!= -1:
                  self.irc_print('That would be kchase')
                elif rline.find("sexiest mod")!= -1:
                  self.irc_print('NellyFrozen... Hands down!')
                # elif pline.lower() == 'hi'!= -1:
                    # self.irc_print("Well hello there " + user)
                # elif pline.lower() == 'hello'!= -1:
                    # self.irc_print("Well hello there " + user)
                # elif pline.lower() == 'bye'!= -1:
                    # self.irc_print("Come back soon " + user + "!")
                # elif pline.lower() == 'good night'!= -1:
                    # self.irc_print("Sweat dreams " + user + "!")
                # elif pline.lower() == 'night'!= -1:
                    # self.irc_print("Sweat dreams " + user + "!")

                elif pline == '!users'!= -1:
                  if not self.waiting_for_response:
                    self.display_result = True
                    self.waiting_for_response = True
                    self.sock.send('NAMES ' + CONN['channel'] + '\n') #Joins default channel

                elif pline == '!peak'!= -1:
                  if not self.waiting_for_response:
                    self.display_result = True
                    self.waiting_for_response = True
                    self.sock.send('NAMES ' + CONN['channel'] + '\n') #Joins default channel

                elif ((((dline.lower().find('site')    != -1) or \
                        (dline.lower().find('emp')     != -1) or \
                        (dline.lower().find('tracker') != -1))and \
                        (dline.lower().find('?')       != -1))and \
                        (dline.lower().find('child')       == -1)):
                        if (dline.lower().find('what') != -1) or \
                           (dline.lower().find('why')  != -1):
#                                      self.irc_print(self.site['reason'])
                                  self.irc_notice(user + ' ' + self.site['reason'])

                        elif (dline.lower().find('when') != -1) or \
                             (dline.lower().find('long') != -1) or \
                             (dline.lower().find('time') != -1) or \
                             (dline.lower().find('estimate') != -1) or \
                             (dline.lower().find('back') != -1):
#                                      self.irc_print(self.site['eta'])
                                  self.irc_notice(user + ' ' + self.site['eta'])

                        elif (dline.lower().find('up')       != -1) or \
                             (dline.lower().find('down')     != -1) or \
                             (dline.lower().find('broke')    != -1) or \
                             (dline.lower().find('working')  != -1) or \
                             (dline.lower().find('online')   != -1) or \
                             (dline.lower().find('offline')  != -1):
#                                      self.irc_print(self.site['status'])
                                  self.irc_notice(user + ' ' + self.site['status'])

                # else:
                    # self.ui_console_queue.put(pline)


class NicknameInUseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

