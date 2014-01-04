import curses
import Queue
import threading
import datetime
import sys

from configs.config import FLOOD

class BotUI(object):

    loadDateTime = datetime.datetime.now()

    def main(self,screen,ui_print_queue, irc_flood_timeout_queue):
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)


            screen.bkgd(curses.color_pair(1))
            screen.refresh()

            win_size = screen.getmaxyx()
            con_win = curses.newwin(win_size[0], (((win_size[1]/2)+(win_size[1]/4))), 0, 0)
            stat_win = curses.newwin((win_size[0]/2), (win_size[1]-(((win_size[1]/2)+(win_size[1]/4)))), 0, (((win_size[1]/2)+(win_size[1]/4))))
            con_win.bkgd(curses.color_pair(2))
            con_win.move(1,1)
            con_line = 1
            con_lines = con_line
            con_max_line_len = (((win_size[1]/2)+(win_size[1]/4))-4)
            con_max_lines = (win_size[0]-2)

            while True:
                con_win.box()
                con_win.addstr(0, ((win_size[1]/3)-6), "Bot Console")
                if ui_print_queue.empty() == False:
                    line=ui_print_queue.get()
                    line=line.strip()
                    line=line.rstrip() #removes trailing 'rn'
                    line=line+' '
                    line_len=len(line)
                    start=0
                    end=0

                    while (end < line_len):
                        # print 'line start: '+str(start)
                        # print 'line end: '+str(end)
                        # print 'message length: '+str(line_len)
                        end=line.rfind(' ',start,(end+con_max_line_len))
                        if end <= start:
                            end=(start+con_max_line_len)

                        if con_line >= con_max_lines:
                            con_win.move(1,2)
                            con_win.insdelln(-1)
                            con_win.move(con_line,1)
                            con_win.clrtoeol()
                            con_win.refresh()

                        else:
                            con_line+=1

                        if line[start:end].isspace():
                            con_line-=1
                        else:
                            con_win.move((con_line-1),2)
                            con_win.clrtoeol()
                            con_win.addstr((con_line-1), 2, ('#'+line[start:end]))
                            start = end
                            con_win.move(con_line,2)

                uptime = (datetime.datetime.now() - self.loadDateTime)
                stat_win.move(1,2)
                stat_win.clrtoeol()
                stat_win.insstr(1,2, ("LoadTime:  " + self.loadDateTime.strftime('%d/%m/%Y %H:%M:%S')))
                stat_win.move(2,2)
                stat_win.clrtoeol()
                stat_win.insstr(2,2, ("Uptime:    " + str(uptime)))
                stat_win.move(3,2)
                stat_win.clrtoeol()
                stat_win.insstr(3,2,  "IRC Flood: ")
                stat_win.move(3,13)
                for x in range(0,irc_flood_timeout_queue.qsize()):
                    if irc_flood_timeout_queue.qsize() >= FLOOD['flood_messages']:
                        stat_win.addch(' ',curses.color_pair(5))
                    elif irc_flood_timeout_queue.qsize() >= (FLOOD['flood_messages']/2):
                        stat_win.addch(' ',curses.color_pair(4))
                    else:
                        stat_win.addch(' ',curses.color_pair(3))
                        
                stat_win.insstr(3,(13+FLOOD['flood_messages']), (" : " + str(irc_flood_timeout_queue.qsize())))

                stat_win.box()
                stat_win.addstr(0, ((win_size[1]/8)-5), "Bot Stats")
                con_win.box()
                con_win.addstr(0, ((win_size[1]/3)-6), "Bot Console")
                con_win.refresh()
                stat_win.refresh()
        except Exception as e:
            print e
            exit()


    def __init__(self,ui_print_queue,irc_flood_timeout_queue):
        try:
            curses.wrapper(self.main,ui_print_queue,irc_flood_timeout_queue)
        except KeyboardInterrupt:
            print "Closing"
            exit()