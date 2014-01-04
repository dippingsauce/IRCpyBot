import curses
import Queue
import threading
import sys

class BotUI(object):

    def main(self,screen,ui_print_queue):
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)


            screen.bkgd(curses.color_pair(1))
            screen.refresh()

            win_size = screen.getmaxyx()
            con_win = curses.newwin(win_size[0], (win_size[1]/2), 0, 0)
            con_win.bkgd(curses.color_pair(2))
            con_win.box()
            con_win.addstr(0, ((win_size[1]/4)-6), "Bot Console")
            con_win.move(1,1)
            con_line = 1
            con_lines = con_line
            con_max_line_len = ((win_size[1]/2)-8)
            con_max_lines = (win_size[0]-2)

            while True:
                con_win.box()
                con_win.addstr(0, ((win_size[1]/4)-6), "Bot Console")
                if ui_print_queue.empty() == False:
                    line=ui_print_queue.get()
                    line_len=len(line)
                    start=0

                    for i in range(0,(line_len/con_max_line_len)):
                        end=min(line_len, (con_max_line_len*(i+1)))
                        if con_line >= con_max_lines:
                            con_win.move(1,2)
                            con_win.insdelln(-1)
                            con_win.move(con_line,1)
                            con_win.clrtoeol()
                            
                        else:
                            con_line+=1

                        con_win.addstr((con_line-1), 2, line[start:end])
                        start = end
                        con_win.move(con_line,2)
                con_win.refresh()
        except Exception as e:
            print e
            exit()


    def __init__(self,ui_print_queue):
        try:
            curses.wrapper(self.main,ui_print_queue)
        except KeyboardInterrupt:
            print "Closing"
            exit()