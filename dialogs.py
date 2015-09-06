#
#   dialogs.py
#
#   This file is part of othelloTk   
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

import Tkinter as tk
import os
import tkSimpleDialog
import tkFileDialog

class PreferencesDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, master):
        self.mainapp = parent
        tkSimpleDialog.Dialog.__init__(self, master)

    def body(self, master):
        #self.rb = tk.IntVar()
        #self.rb.set(self.mainapp.settings["opponent"])
        #tk.Label(master, text="Opponent:").grid(row=0, sticky=tk.W)
        #tk.Radiobutton(master, text="Human", variable=self.rb, value=HUMAN, state=tk.NORMAL).grid(row=0, column=1, sticky=tk.W)

        enginepath = self.mainapp.settings["enginepath"]
        #if os.path.exists(enginepath):
        #    state = tk.NORMAL
        #else:
        #    state = tk.DISABLED
        #self.comprb = tk.Radiobutton(master, text="Engine", variable=self.rb, value=COMPUTER, state=state)
        #self.comprb.grid(row=1, column=1, sticky=tk.W)
        #self.comprb.config(state=NORMAL)
        tk.Label(master, text="Engine Path:").grid(row=2, sticky=tk.W)
        tk.Button(master, text="Browse", command=self.get_engine_path).grid(row=2, column=2)

        self.v = tk.StringVar()
        self.v.set(enginepath)
        self.e1 = tk.Entry(master, textvariable=self.v, width=30)

        self.e1.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)

        #Label(master, text="Search Depth:").grid(row=2)

        return self.e1 # initial focus

    def apply(self):
        #self.mainapp.settings["opponent"] = self.rb.get()
        self.mainapp.settings["enginepath"] = self.e1.get()
        self.result = 1
        return

    def get_engine_path(self):
        filename = tkFileDialog.askopenfilename()
        self.v.set(filename)
        #if os.path.exists(filename):
        #    self.comprb.configure(state=tk.NORMAL)
        #else:
        #    self.comprb.configure(state=tk.DISABLED)

class EnginePathDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, master):
        self.mainapp = parent
        tkSimpleDialog.Dialog.__init__(self, master)

    def body(self, master):
        self.enginepath = ""
        enginepath = self.mainapp.settings["enginepath"] 
        tk.Label(master, text="Engine Path:").grid(row=2, sticky=tk.W)
        tk.Button(master, text="Browse", command=self.get_engine_path).grid(row=2, column=2)

        # engine path
        self.ep = tk.StringVar()
        self.ep.set(enginepath)
        self.e1 = tk.Entry(master, textvariable=self.ep, width=30)

        self.e1.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        self.msg = tk.StringVar()
        self.msg.set("Please set a valid path to the Edax engine")
        msglbl = tk.Label(master, textvariable=self.msg, justify=tk.LEFT).grid(row=3, column=1, sticky=tk.W)

        return self.e1 # initial focus

    def validate(self):
        enginepath = self.ep.get()
        if os.path.exists(enginepath): 
            return True
        else:
            self.msg.set("Not a valid path")
            return False

    def apply(self):
        #self.mainapp.settings["enginepath"] = self.e1.get()
        self.enginepath = self.e1.get()
        #self.result = 1
        return

    def get_engine_path(self):
        filename = tkFileDialog.askopenfilename()
        self.ep.set(filename)

