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
import shlex

BLACK=0
WHITE=1
UNOCCUPIED=-1
COLOUR=("black", "white")

mc = 0

class Othello(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid(sticky=N + S + E + W)
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        master.minsize(width=200, height=200)
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
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        line_width = 2
        self.line_width = line_width
        square_width = int((min(screen_width, screen_height) * 0.6) / 8) 
        square_height = square_width
        self.square_height = square_height
        board_width = (square_width * 8)
        board_height = board_width

        pad_frame = Frame(borderwidth=0, background="light blue", width=board_width, height=board_height)
        #pad_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)
        pad_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = Canvas(root, width=board_width, height=board_height, bg="darkgreen")
        set_aspect(self.canvas, pad_frame, aspect_ratio=1.0/1.0)

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.canvas.bind("<Button-1>", self.clicked)
        self.canvas.bind("<Button-3>", self.rclicked)

    def on_resize(self,event):
        self.draw_board()

    def draw_board(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # if window size not divisible by 8 we will have extra space
        # at the edges
        x_extra = (width % 8)
        y_extra = (height % 8)

        x_offset = x_extra / 2
        y_offset = y_extra / 2

        width = width - x_extra
        height = height - y_extra

        square_width = width / 8
        square_height = height / 8
        self.canvas.delete(ALL)
        line_width = self.line_width
        # horizontal board lines
        x = 0
        y = 0
        for i in range(0, 9):
            self.canvas.create_line(x + x_offset, y + y_offset, width + x_offset, y + y_offset, fill="black", width=line_width)
            y += square_height

        # vertical board lines
        x = 0
        y = 0
        for i in range(0, 9):
            self.canvas.create_line(x + x_offset, y + y_offset, x + x_offset, height + y_offset, fill="black", width=line_width)
            x += square_width

        self.piece_ids = []
        # draw the 4 pieces at start position
        for y in range(0, 8):
            for x in range(0, 8):
                self.draw_piece(x, y)

    # human passes on move (only allowed if no legal moves)
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

    # process humans move (black)
    def clicked(self, event):
        global mc
        if self.stm != BLACK or self.gameover:
            return

        # get x, y square co-ordinates (in range 0 - 7)
        x = event.x / (self.canvas.winfo_width() / 8)
        y = event.y / (self.canvas.winfo_height() / 8)
 
        # ignore index out of range (user clicked near edge of board)
        if x > 7 or y > 7:
            return

        if self.board[x][y] != UNOCCUPIED:
            return

        # No legal moves
        if self.legal_moves == []:
            return

        # not a legal move
        if (x, y) not in self.legal_moves:
            return

        # legal move so place piece and flip opponents pieces
        for incx, incy in [(-1, 0), (-1, -1), (0, -1), (1, -1), (1,0), (1, 1), (0, 1), (-1, 1)]:
            self.flip(x, y, incx, incy, self.stm)

        # convert move from board co-ordinates to othello format (e.g. 3, 5 goes to 'd6')
        l = "abcdefgh"[x]
        n = y + 1
        move = l + str(n)
        print "move:", move
        str1 = "usermove " + move + "\n"
        # send human move to engine
        self.command(str1)
        if mc == 0:
            self.command('go\n')
            mc = 1

        self.stm = abs(self.stm - 1)
        self.print_board()
        self.canvas.update_idletasks()
        self.mv = ""
        self.gameover = self.check_for_gameover()
        if self.gameover:
            return
        self.ct= thread.start_new_thread( self.computer_move, () ) 
        self.after_idle(self.get_move)
        return

    # Game is over when neither side can move
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

    # count the discs on the board for side
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
                    count += self.count_flipped(x, y, incx, incy, stm)
                if count > 0:
                    legal_moves.append((x, y))
        return legal_moves

    def count_flipped(self, x, y, incx, incy, stm):
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
        # if no move wait a second and try again
        if self.mv == "":
            time.sleep(1.0)
            self.after_idle(self.get_move)
            return
        print "move:",self.mv
        mv = self.mv
        # pass
        if mv == "@@@@":
            self.stm = abs(self.stm - 1)
            return
        # convert move to board coordinates (e.g. "d6" goes to 3, 5)
        letter = mv[0]
        num = mv[1]
        x = "abcdefgh".index(letter)
        y = int(num) - 1

        for incx, incy in [(-1, 0), (-1, -1), (0, -1), (1, -1), (1,0), (1, 1), (0, 1), (-1, 1)]:                        
            self.flip(x, y, incx, incy, self.stm)              
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

        # Engine should respond to "protover 2" with "feature" command
        response_ok = False
        i = 0
        while True:            
            for l in self.op:
                l = l.strip()
                if l.startswith("feature "):
                    response_ok = True
                    f = shlex.split(l)
                    features = f[1:]
                    for f in features:
                        print f
            self.op = []
            if response_ok:
                break            
            i += 1
            if i > 12:                
                print "Error - no response from engine"
                sys.exit(1)
            time.sleep(0.25)

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
            self.op = []

    def draw_piece(self, i, j):
        # remove piece (if any) before redrawing it
        for t in self.piece_ids:
            x,y,piece_id = t
            if (x,y) == (i,j):
                self.canvas.delete(piece_id)
                self.piece_ids.remove((x,y,piece_id))
        square_width = (self.canvas.winfo_width() / 8)
        square_height = (self.canvas.winfo_height() / 8)
        adj =  square_width * 0.1
        x0 = i * square_width + adj
        y0 = j * square_height + adj
        x1 = (i + 1) * square_width - adj
        y1 = (j + 1) * square_height - adj

        if self.board[i][j] == BLACK:
            fill_colour = COLOUR[BLACK]
        elif self.board[i][j] == WHITE:
            fill_colour = COLOUR[WHITE]
        else:
            return
        piece_id = self.canvas.create_oval(x0, y0, x1, y1, fill=fill_colour)
        oval_tup = (i,j,piece_id)
        self.piece_ids.append(oval_tup)

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
                #print line
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
                        self.board[i][j] = stm
                        self.draw_piece(i,j)
                return count                
            else:
                return 0
            xx = xx + incx
            yy = yy + incy

def set_aspect(content_frame, pad_frame, aspect_ratio):
    # a function which places a frame within a containing frame, and
    # then forces the inner frame to keep a specific aspect ratio

    def enforce_aspect_ratio(event):
        # when the pad window resizes, fit the content into it,
        # either by fixing the width or the height and then
        # adjusting the height or width based on the aspect ratio.

        # start by using the width as the controlling dimension
        desired_width = event.width
        desired_height = int(event.width / aspect_ratio)

        # if the window is too tall to fit, use the height as
        # the controlling dimension
        if desired_height > event.height:
            desired_height = event.height
            desired_width = int(event.height * aspect_ratio)

        # place the window, giving it an explicit size
        content_frame.place(in_=pad_frame, x=0, y=0, 
            width=desired_width, height=desired_height)

    pad_frame.bind("<Configure>", enforce_aspect_ratio)

root = Tk()
#root.resizable(width=FALSE, height=FALSE)
#root.geometry('{}x{}'.format(900, 900))
root.aspect(1,1,1,1)
app = Othello(root)
app.master.title('OthelloTK')
app.mainloop()

