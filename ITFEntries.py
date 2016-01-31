# Copyright Stefan Ralser, Johannes Postler, Arntraud Bacher
# Institut für Ionenphysik und Angewandte Physik
# Universitaet Innsbruck

# Class for entries

from tkinter import ttk
import tkinter as tk

# Style konfigurieren
#ttk.Style().configure('Status.TLabel', borderwidth=1, relief='sunken')

# ----------------------------------------
# Class ITFEntries für die Eingabefelder
# ----------------------------------------
class ITFEntries:
    def __init__(self,frame,bezeichnung,ausrichtung,zeile,spalte,
        startwert='',status=tk.NORMAL, span=1):
        if bezeichnung != '':
            self.text = ttk.Label(frame, text=bezeichnung)
            if ausrichtung == 'h':
                self.text.grid(column=spalte-1, row=zeile, sticky=tk.W)
            else:
                self.text.grid(column=spalte, row=zeile-1, sticky=tk.W)
        self.wert = tk.StringVar()
        self.edit = ttk.Entry(frame, textvariable=self.wert,
                              justify=tk.RIGHT, state=status)
        self.wert.set(startwert)
        self.edit.bind('<Return>', self.changed)
        self.edit.grid(column=spalte, row=zeile, columnspan=span, sticky=tk.W)
        self.system = bezeichnung

    def changed(self,event):
        text = self.wert.get()
        text = text.replace(',','.')
        self.wert.set(text)
    
    def disable(self):
        self.edit.config(state=tk.DISABLED)
    def enable(self):
        self.edit.config(state=tk.NORMAL)
    def config(self,stil):
        self.edit.config(style=stil)

class ITFStatusBar:
    def __init__(self,frame,zeile):
        self.textbar = ttk.Label(frame, text='', borderwidth=1,
            relief=tk.SUNKEN, anchor=tk.W)
        self.textbar.grid(column=0, row=zeile, sticky=tk.S+tk.W+tk.E)
        self.progressbar = ttk.Progressbar(frame, mode='determinate',
            orient=tk.HORIZONTAL)
        self.progressbar.grid(column=1, row=zeile, sticky=tk.S+tk.W+tk.E)

    def setText(self, text):
        self.textbar.configure(text=text)

    def clearText(self):
        self.textbar.configure(text='')

    def update(self,wert):
        self.progressbar['value'] = wert
