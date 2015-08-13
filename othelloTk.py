#
#   othelloTk  August 2015
#
#   Copyright (C) 2015 John Cheetham    
#
#   othelloTk is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   othelloTk is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with othelloTk.  If not, see <http://www.gnu.org/licenses/>.
#   

from Tkinter import *
import subprocess
import thread
import time
import inspect
import os

BLACK=0
WHITE=1
UNOCCUPIED=-1
colour=("black", "white")

mc = 0

class Othello(Frame):
    def __init__(self, master):
        Frame.__init__(self, master) 
        self.grid()
        self.pack()

        row = []
        for i in range(0, 8):
            row.append(UNOCCUPIED)

        self.board = []
        for i in range(0,8):
            self.board.append(row[:])

        self.board[3][3] = WHITE
        self.board[4][4] = WHITE
        self.board[3][4] = BLACK
        self.board[4][3] = BLACK

        self.stm = BLACK # side to move
        self.createWidgets()
        self.engine_init()
        self.gameover = False
        self.after_idle(self.print_board)

    def createWidgets(self): 
        self.canvas = Canvas(self, width=806, height=806, bg="darkgreen")

        # horizontal board lines
        x = 3
        y = 3
        for i in range(0, 9):
            self.canvas.create_line(x, y, 806, y, fill="black", width="5")
            y += 100

        # vertical board lines
        x = 3
        y = 3
        for i in range(0, 9):
            self.canvas.create_line(x, y, x, 806, fill="black", width="5")
            x += 100

        self.canvas.grid()

        self.canvas.bind("<Button-1>", self.clicked)
        self.canvas.bind("<Button-3>", self.rclicked)

        # draw the 4 pieces at start position
        for i,j in [(3, 3), (4, 4), (3, 4), (4, 3)]:
            self.draw_piece(i, j)

    # pass on move (only allowed if no loegal moves)
    def rclicked(self, event):
        if self.stm != BLACK or self.gameover:
            return
        if self.legal_moves == []:
            print "no move available - PASS forced"            
            str1 = "usermove @@@@\n"
            self.command(str1)
            self.stm = abs(self.stm - 1)
            self.print_board()
            self.mv = ""
            self.ct= thread.start_new_thread( self.computer_move, () ) 
            self.after_idle(self.get_move)
            return

    def clicked(self, event):
        global mc
        if self.stm != BLACK or self.gameover:
            return
        # 0 - 8
        x = event.x / 100 
        y = event.y / 100
        if self.board[x][y] != UNOCCUPIED:
            return

        if self.legal_moves == []:
            return

        count = 0
        for incx, incy in [(-1, 0), (-1, -1), (0, -1), (1, -1), (1,0), (1, 1), (0, 1), (-1, 1)]:
            count += self.flip(x, y, incx, incy, self.stm)
       
        if count == 0:
            return

        l = "abcdefgh"[x]
        n = y + 1
        move = l + str(n)
        print "move:", move
        str1 = "usermove " + move + "\n"
        self.command(str1)
        if mc == 0:
            self.command('go\n')
            mc = 1

        self.stm = abs(self.stm - 1)
        self.print_board()
        self.canvas.update_idletasks()
        self.mv = ""
        self.ct= thread.start_new_thread( self.computer_move, () ) 
        self.after_idle(self.get_move)
        self.gameover = self.check_for_gameover()
        return

    def check_for_gameover(self):
       if self.get_legal_moves(BLACK) == [] and self.get_legal_moves(WHITE) == []:
           self.gameover = True
           print "Game Over - ",
           black_count = self.count(BLACK)
           white_count = self.count(WHITE)
           if black_count > white_count:
               print "Black wins"
           elif white_count > black_count:
               print "White Wins"
           else:
               print "Draw"
           return True
       return False

    def print_board(self):
       self.legal_moves = self.get_legal_moves(self.stm)
       print
       print "  A B C D E F G H"        
       for y in range(0, 8):
            print y+1,
            for x in range(0, 8):                
                if self.board[x][y] == BLACK:
                    print "*",
                elif self.board[x][y] == WHITE:
                    print "O",                
                else:
                    if (x, y) in self.legal_moves:
                        print ".",
                    else:
                        print "-",
            print y
       print "  0 1 2 3 4 5 6 7"
       print
       print "Black:",self.count(BLACK),"   White:",self.count(WHITE)
       if self.stm == BLACK:
           print "black to move"
       else:
           print "white to move"
       print "Legal moves:",self.get_legal_moves(self.stm)
       print

    def count(self, side):
        count = 0
        for y in range(0, 8):
            for x in range(0, 8):
                if self.board[x][y] == side:
                    count += 1
        return count

    def get_legal_moves(self, stm):
        legal_moves = []
        for y in range(0, 8):
            for x in range(0, 8):
                if self.board[x][y] != UNOCCUPIED:
                    continue
                count = 0
                for incx, incy in [(-1, 0), (-1, -1), (0, -1), (1, -1), (1,0), (1, 1), (0, 1), (-1, 1)]:
                    count += self.flip2(x, y, incx, incy, stm)
                if count > 0:
                    legal_moves.append((x, y))
        return legal_moves

    def flip2(self, x, y, incx, incy, stm):
        count = 0
        opponent = abs(stm - 1)
        xx = x + incx
        yy = y + incy
        while True:
            if xx < 0 or xx > 7 or yy < 0 or yy > 7:
                return 0
            if self.board[xx][yy] == opponent:
                count += 1
            elif self.board[xx][yy] == stm:
                return count
            else:
                return 0
            xx = xx + incx
            yy = yy + incy
        return 0

    # get computers move
    def get_move(self):
        print
        print "white to move"
        time.sleep(1.0)
        if self.mv == "":
            time.sleep(1.0)
            self.after_idle(self.get_move)
            return
        print "move:",self.mv
        mv = self.mv
        if "wins" in mv or "Draw" in mv:
            print "Game Over", mv
            return
        # pass
        if mv == "@@@@":
            return
        letter = mv[0]
        num = mv[1]
        x = "abcdefgh".index(letter)
        y = int(num) - 1

        count = 0
        for incx, incy in [(-1, 0), (-1, -1), (0, -1), (1, -1), (1,0), (1, 1), (0, 1), (-1, 1)]:                        
            count += self.flip(x, y, incx, incy, self.stm)              
        self.stm = abs(self.stm - 1)
        self.print_board()
        self.gameover = self.check_for_gameover()

    def engine_init(self):
        print "Initialising Engine"
        this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        path = this_dir + os.sep + "edax.sh"        

        p = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.p = p
        # check process is running
        i = 0
        while (p.poll() is not None):            
            i += 1
            if i > 40:        
                print "unable to start engine process"
                return False
            time.sleep(0.25)        

        # start thread to read stdout
        self.op = []       
        self.soutt = thread.start_new_thread( self.read_stdout, () )
        #self.command('xboard\n')
        self.command('protover 2\n')
        self.command('variant reversi\n')
        #self.command('st 6\n')
        self.command('sd 4\n')

    def computer_move(self):
        # Wait for move from engine
        i = 0
        bestmove = False                
        while True:
            time.sleep(0.5)
            for l in self.op:
                l = l.strip()                    
                if l.startswith('move'):
                    mv = l[7:]
                    self.mv = mv
                    self.op = []
                    return
                if "wins" in l or "Draw" in l:
                    self.mv = l
                    return
            self.op = []

    def draw_piece(self, i, j):
        x = (i+1) * 100 - 50
        y = (j+1) * 100 - 50
        if self.board[i][j] == BLACK:
            oval = self.canvas.create_oval(x - 45, y - 45, x + 51, y + 51, fill=colour[BLACK])
        elif  self.board[i][j] == WHITE:
            oval = self.canvas.create_oval(x - 45, y - 45, x + 51, y + 51, fill=colour[WHITE])        

    def command(self, cmd):
        try:
            self.p.stdin.write(cmd)
        except AttributeError:
            print "AttributeError"
        except IOError:
            print "ioerror"

    def read_stdout(self):
        while True:
            try:
                self.p.stdout.flush()
                line = self.p.stdout.readline()
                line = line.strip()
                self.op.append(line)
            except Exception, e:
                print "subprocess error in read_stdout:",e       

    def flip(self, x, y, incx, incy, stm):
        count = 0
        opponent = abs(stm - 1)
        xx = x + incx
        yy = y + incy   
        fliplist = [(x, y)]
        while True:
            if xx < 0 or xx > 7 or yy < 0 or yy > 7:
                return 0
            if self.board[xx][yy]== opponent:
                count += 1
                fliplist.append((xx, yy))               
            elif self.board[xx][yy] == stm:
                if count > 0:           
                    for i,j in fliplist:
                        xxx = i * 100 + 50
                        yyy = j * 100 + 50
                        self.canvas.create_oval(xxx - 45, yyy - 45, xxx + 51, yyy + 51, fill=colour[stm])
                        #self.draw_piece(i,j)
                        self.board[i][j] = stm
                return count                
            else:
                return 0
            xx = xx + incx
            yy = yy + incy

root = Tk()
root.resizable(width=FALSE, height=FALSE)
app = Othello(root)
app.master.title('OthelloTK')
app.mainloop()

