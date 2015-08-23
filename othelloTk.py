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
from tkMessageBox import *
from tkFileDialog import *
import subprocess
import thread
import time
import inspect
import os
import shlex
import json

BLACK=0
WHITE=1
UNOCCUPIED=-1
COLOUR=("black", "white")
HUMAN=0
COMPUTER=1

class Othello(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.othellopath = os.path.expanduser("~") + "/.othelloTk"

        if not os.path.exists(self.othellopath):
            try:
                os.makedirs(self.othellopath)
            except OSError, exc:                
                print "Error - unable to create .othelloTk folder"
                sys.exit(1)

        # set default values used at first run
        self.settings = {
                         "version": "0.0.1",
                         "enginepath": "",
                         "opponent": HUMAN
                        }

        self.settings_filepath = os.path.join (self.othellopath, "settings.json")
        # create settings file as ~/.othelloTk/settings.json if first run
        if not os.path.exists(self.settings_filepath):
            with open(self.settings_filepath, 'w') as outfile:
                json.dump(self.settings, outfile, indent=4)

        # read settings from file
        with open(self.settings_filepath) as settings_file:
            self.settings = json.load(settings_file)

        # make resizeable
        self.grid(sticky=N + S + E + W) 
        master.minsize(width=300, height=300)
        self.master = master
        self.master.title('OthelloTk')
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

        self.player = [HUMAN, self.settings["opponent"]]
        self.stm = BLACK # side to move
        self.soutt = None
        self.first = True
        self.createWidgets()
        self.gameover = False
        self.engine_active = False
        self.piece_ids = []
        self.after_idle(self.print_board)

    def createWidgets(self):
        # make resizeable
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=2)

        self.line_width = 2
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        board_width = min(screen_width, screen_height) * 0.6
        board_height = board_width

        #pad_frame = Frame(self, borderwidth=0, background="light blue", width=board_width, height=board_height)
        pad_frame = Frame(self, borderwidth=0, width=board_width, height=board_height)
        pad_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=15)

        self.canvas = Canvas(pad_frame, width=board_width, height=board_height, bg="darkgreen")
        set_aspect(self.canvas, pad_frame, aspect_ratio=1.0)

        self.canvas.bind("<Configure>", self.on_resize)

        self.canvas.bind("<Button-1>", self.clicked)
        self.canvas.bind("<Button-3>", self.rclicked)

        #info_frame = Frame(self, borderwidth=0, background="light blue", width=board_width / 2, height=board_height)
        #info_frame.grid(row=0, column=1, sticky="nsew")

        #l = Label(info_frame, text = "* Black", bg="light blue", font=("Helvetica", -32, "italic"))
        #l.grid(row=0, column=0, sticky="w")

        # menubar
        self.master.option_add('*tearOff', FALSE)
        menubar = Menu(self.master)

        menu_file = Menu(menubar)
        menu_edit = Menu(menubar)
        menu_play = Menu(menubar)
        #menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')
        menubar.add_cascade(menu=menu_play, label='Play')
        #menubar.add_cascade(menu=menu_help, label='Help')

        def about():
            showinfo("About OthelloTk", "OthelloTk\n\n0.0.1\n\n"
                                        "A GUI to play Othello against Edax.\n\n"
                                         "Copyright (c) 2015 John Cheetham\n\n"
                                         "http://johncheetham.com\n\n" 
                                         "This program comes with ABSOLUTELY NO WARRANTY")

        def preferences():
            d = PreferencesDialog(self, self.master)
            # save settings to file
            if d.result is not None:
                with open(self.settings_filepath, 'w') as outfile:
                    json.dump(self.settings, outfile, indent=4)
            return

        menu_file.add_command(label='New Game', command=self.new_game, underline=0, accelerator="Ctrl+N")
        menu_file.add_separator()
        menu_file.add_command(label='Quit', command=self.quit_program, underline=0, accelerator="Ctrl+Q")
        menu_edit.add_command(label='Preferences', command=preferences)
        menu_play.add_command(label='Pass', command=self.pass_on_move, underline=0, accelerator="Ctrl+P")
        #menu_help.add_command(label='About', command=about, underline=0)
        self.master.config(menu=menubar)

        # accelerator keys
        self.bind_all("<Control-q>", self.quit_program)
        self.bind_all("<Control-n>", self.new_game)
        self.bind_all("<Control-p>", self.pass_on_move)

    def quit_program(self, event=None):
        self.quit()

    def new_game(self, event=None):

        for y in range(0, 8):
            for x in range(0, 8):
                self.board[x][y] = UNOCCUPIED

        self.board[3][3] = WHITE
        self.board[4][4] = WHITE
        self.board[3][4] = BLACK
        self.board[4][3] = BLACK

        self.stm = BLACK # side to move

        self.gameover = False
        self.piece_ids = []
        self.canvas.delete("piece")
        self.canvas.delete("possible_move")
        self.draw_board()
        self.first = True
        self.after_idle(self.print_board)
        self.player = [HUMAN, self.settings["opponent"]]
        if not self.engine_active:
            return
        self.command("quit\n")
        # allow 5 seconds for engine process to end            
        i = 0
        while True:
            if self.p.poll() is not None: 
                break                
            i += 1
            if i > 20:         
                print "engine has not terminated after quit command"
                break        
            time.sleep(0.25)
        self.engine_active = False

    def on_resize(self,event):
        self.draw_board()

    def get_board_size(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        border_size_w = canvas_width / 9
        border_size_h = canvas_height / 9
        board_width = canvas_width - border_size_w
        board_height = canvas_height - border_size_h
        # Make sure width/height is divisible by 8
        board_width = board_width - (board_width % 8)
        board_height = board_height - (board_height % 8)
        x_offset = border_size_w / 2
        y_offset = border_size_h / 2
        return board_width, board_height, x_offset, y_offset, border_size_w, border_size_h

    def draw_board(self):
        board_width, board_height, x_offset, y_offset, border_size_w, border_size_h = self.get_board_size()

        square_width = board_width / 8
        square_height = board_height / 8
        self.canvas.delete(ALL)
        line_width = self.line_width
        # horizontal board lines
        x = 0
        y = 0
        for i in range(0, 9):
            self.canvas.create_line(x + x_offset, y + y_offset, board_width + x_offset, y + y_offset, fill="black", width=line_width, tags="line")
            y += square_height

        # vertical board lines
        x = 0
        y = 0
        for i in range(0, 9):
            self.canvas.create_line(x + x_offset, y + y_offset, x + x_offset, board_height + y_offset, fill="black", width=line_width, tags="line")
            x += square_width

        self.piece_ids = []
        # draw the 4 pieces at start position
        for y in range(0, 8):
            for x in range(0, 8):
                self.draw_piece(x, y)


        fontsize = (square_width / 4) * -1
        # draw x co-ordinates
        x = square_width
        let="ABCDEFGH"
        for i in range(0, 8):
            #self.canvas.create_text(x, y_offset / 2, font=("Helvetica", fontsize, "bold italic"), text=let[i], fill="light blue")
            self.canvas.create_text(x, y_offset / 2, font=("Helvetica", fontsize, "italic"), text=let[i], fill="light blue", tags="coords")
            x += square_width

        # draw y co-ordinates
        y = square_width
        num="12345678"
        for i in range(0, 8):
            self.canvas.create_text(x_offset / 2, y, font=("Helvetica", fontsize, "italic"), text=num[i], fill="light blue", tags="coords")
            y += square_height

    def draw_piece(self, i, j):
        # remove piece (if any) before redrawing it
        for t in self.piece_ids:
            x,y,piece_id = t
            if (x,y) == (i,j):
                self.canvas.delete(piece_id)
                self.piece_ids.remove((x,y,piece_id))
        board_width, board_height, x_offset, y_offset, border_size_w, border_size_h = self.get_board_size()
        square_width = board_width / 8
        square_height = board_height / 8

        # adjustment because we don't want the disc to fill the whole square
        adj =  square_width * 0.1
        tag = "piece"

        if self.board[i][j] == BLACK:
            fill_colour = COLOUR[BLACK]
        elif self.board[i][j] == WHITE:
            fill_colour = COLOUR[WHITE]
        elif (i, j) in self.legal_moves:
            fill_colour = "light blue"
            adj = square_width * 0.45
            tag = "possible_move"
        else:
            return

        x0 = i * square_width + adj + x_offset
        y0 = j * square_height + adj + y_offset
        x1 = (i + 1) * square_width - adj + x_offset
        y1 = (j + 1) * square_height - adj + y_offset
        piece_id = self.canvas.create_oval(x0, y0, x1, y1, fill=fill_colour, tags=tag)
        if tag != "possible_move":
            oval_tup = (i,j,piece_id)
            self.piece_ids.append(oval_tup)

    def pass_on_move(self, event=None):
        if self.player[self.stm] != HUMAN or self.gameover:
            return
        if self.legal_moves == []:
            print "no move available - PASS forced"
            self.stm = abs(self.stm - 1)
            self.print_board()
            if self.player[self.stm] == COMPUTER:
                str1 = "usermove @@@@\n"
                self.command(str1)

                self.mv = ""
                self.ct= thread.start_new_thread( self.computer_move, () ) 
                self.after_idle(self.get_move)
            return
        print "Can't pass - legal moves are available"

    # human passes on move (only allowed if no legal moves)
    def rclicked(self, event):
        self.pass_on_move()

    # process humans move (black)
    def clicked(self, event):

        if self.player[self.stm] != HUMAN or self.gameover:
            return

        board_width, board_height, x_offset, y_offset, border_size_w, border_size_h = self.get_board_size()

        # check the click was on the board
        if ((event.x < x_offset) or (event.x > (board_width + x_offset)) or
           (event.y < y_offset) or (event.y > (board_height + y_offset))):
           return

        # get x, y square co-ordinates (in range 0 - 7)
        x = (event.x - x_offset) / (board_width / 8)
        y = (event.y - y_offset) / (board_height / 8) 

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

        self.stm = abs(self.stm - 1)
        self.print_board()
        self.canvas.update_idletasks()

        # convert move from board co-ordinates to othello format (e.g. 3, 5 goes to 'd6')
        l = "abcdefgh"[x]
        n = y + 1
        move = l + str(n)
        print "move:", move

        # start engine if needed
        if self.player[self.stm] == COMPUTER and not self.engine_active:
            self.engine_init()
            if not self.engine_active:
                print "Error starting engine"
                # failed to init so switch opponent to human
                self.player[self.stm] = HUMAN
 
        # engine OK - send move
        if self.player[self.stm] == COMPUTER:
            str1 = "usermove " + move + "\n"
            # send human move to engine
            self.command(str1)
            # if it is the engines first move in the game then we need to send the go command
            if self.first:
                self.command('go\n')
                self.first = False

        self.gameover = self.check_for_gameover()
        if self.gameover:
            return
        if self.player[self.stm] == HUMAN:
            return

        # Computers move
        self.mv = ""
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
       #print "self.master.winfo_width()=",self.master.winfo_width()
       #print "self.master.winfo_height()=",self.master.winfo_height()
       #for item in self.pad_frame.root.grid_slaves():
       #    print "item=",item

       #tagged = self.canvas.find_withtag("possible_move")
       #for t in tagged:
       #    self.canvas.delete(t)
       self.canvas.delete("possible_move")
       self.legal_moves = self.get_legal_moves(self.stm)
       for y in range(0, 8):
           for x in range(0, 8):
               if (x,y) in self.legal_moves:
                   self.draw_piece(x, y)
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

       #ids = self.canvas.find_all()
       #for id in ids:
       #    tags = self.canvas.gettags(id)[0]
       #    if tags not in ("coords","line"):
       #        print id,self.canvas.gettags(id)
       #print "-"
       #for t in self.piece_ids:
       #    print t, self.canvas.gettags(t[2])


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
        self.engine_active = False
        #this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        #path = this_dir + os.sep + "edax.sh"  
        path = self.settings["enginepath"]
        if not os.path.exists(path):
            print "Error enginepath does not exist"
            return
        print "path=",path

        #
        # change the working directory to that of the engine before starting it
        #
        orig_cwd = os.getcwd()
        print "current working directory is", orig_cwd        
        engine_wdir = os.path.dirname(path)
        os.chdir(engine_wdir)
        print "working directory changed to" ,os.getcwd()

        p = subprocess.Popen([path,"-xboard", "-n", "1"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.p = p

        os.chdir(orig_cwd)
        print "current working directory restored back to", os.getcwd()

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
        if self.soutt is None:
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
            if i > 60:                
                print "Error - no response from engine"
                sys.exit(1)
            time.sleep(0.25)

        self.command('variant reversi\n')
        #self.command('st 6\n')
        self.command('sd 4\n')
        self.engine_active = True

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
        #content_frame.place(in_=pad_frame, x=0, y=0, 
        #    width=desired_width, height=desired_height)
        content_frame.place(in_=pad_frame, x=(event.width - desired_width) / 2, y=(event.height - desired_height) / 2, 
            width=desired_width, height=desired_height)
    pad_frame.bind("<Configure>", enforce_aspect_ratio)

import tkSimpleDialog
class PreferencesDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, master):
        PreferencesDialog.parent = parent
        tkSimpleDialog.Dialog.__init__(self, master)

    def body(self, master):
        self.rb = IntVar()
        self.rb.set(PreferencesDialog.parent.player[WHITE])
        Label(master, text="Opponent:").grid(row=0)
        Radiobutton(master, text="Human",pady = 20, variable=self.rb, value=HUMAN, state=NORMAL).grid(row=0, column=1)

        enginepath = PreferencesDialog.parent.settings["enginepath"]
        if os.path.exists(enginepath):
            state = NORMAL
        else:
            state = DISABLED
        self.comprb = Radiobutton(master, text="Engine", pady = 20, variable=self.rb, value=COMPUTER, state=state).grid(row=0, column=2)
        #self.comprb.config(state=NORMAL)
        Label(master, text="Engine Path:").grid(row=1)
        Button(master, text="Browse", command=self.get_engine_path).grid(row=1, column=2)

        self.v = StringVar()
        self.v.set(enginepath)
        self.e1 = Entry(master, textvariable=self.v)

        self.e1.grid(row=1, column=1)
        return self.e1 # initial focus

    def apply(self):
        PreferencesDialog.parent.settings["opponent"] = self.rb.get()
        PreferencesDialog.parent.settings["enginepath"] = self.e1.get()
        self.result = 1
        return

    def get_engine_path(self): 
        filename = "s"
        filename = askopenfilename()
        self.v.set(filename)

root = Tk()
app = Othello(root)
#root.aspect(809,642,809, 642)
#app.master.title('OthelloTk')
app.mainloop()

