import curses
import Queue

class BotUI(object):
    
    def main(self,screen,irc_print_queue):

        curses.start_color() 
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE) 
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) 


        screen.bkgd(curses.color_pair(1)) 
        screen.refresh() 

        win_size = screen.getmaxyx()
        win = curses.newwin(win_size[0], win_size[1], 0, 0) 
        win.bkgd(curses.color_pair(2)) 
        win.box() 
        
        
        #while True:            
        win.addstr(2, 2, irc_print_queue.get()) 
        win.refresh() 
        c = screen.getch() 

    
    def __init__(self,irc_print_queue):
        
        try: 
             curses.wrapper(self.main, irc_print_queue) 
        except KeyboardInterrupt: 
             print "Got KeyboardInterrupt exception. Exiting..." 
             exit()
                
if __name__ == "__main__":
    irc_print_queue = Queue.Queue(maxsize=0)
    b = BotUI(irc_print_queue)
    irc_print_queue.put('Hello World\n')