#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as Tk
import tkinter.ttk as Ttk
from MicrosoftLocale import Locale, I18nText

class I18nTextView(Tk.Frame):
    def __init__(self, master=None, **keys):
        Tk.Frame.__init__(self, master, **keys)
        self.__i18n_text = None
        self.__rowids = {}
        self.__editor = None
        self.__locale = None
        
        self.treeview = Ttk.Treeview(self)
        self.treeview.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.scrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y, expand=False)
        self.scrollbar.configure(command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        
        self.treeview.bind("<Double-1>", self.__begin_edit)
        self.treeview['columns'] = (1, 2)
        self.treeview['show'] = 'headings'
        self.treeview.column(1)
        self.treeview.column(2)
        self.treeview.heading(1, text='Locale')
        self.treeview.heading(2, text='Text')
        
        self.set_i18n_text(I18nText())
    
    def __locale_for_rowid(self, rowid):
        for locale in Locale.all():
            if self.__rowids[locale] == rowid:
                return locale
        return None
    
    def __begin_edit(self, event):
        self.__cancel_edit(event)
        
        rowid = self.treeview.identify_row(event.y)
        column = self.treeview.identify_column(event.x)
        if column == '#1':
            return
        locale = self.__locale_for_rowid(rowid)
        if locale is None:
            return
        x, y, width, height = self.treeview.bbox(rowid, column)
        pady = height // 2
        
        self.__locale = locale
        self.__editor = Tk.Entry(self.treeview)
        self.__editor.insert(Tk.END, self.__i18n_text[self.__locale])
        self.__editor.place(x=x, y=y+pady, anchor=Tk.W, width=width)
        self.__editor.focus_force()
        self.__editor.bind("<Escape>", self.__cancel_edit)
        self.__editor.bind("<Return>", self.__commit_edit)
    
    def __cancel_edit(self, event):
        if self.__editor != None:
            self.__editor.destroy()
            self.__editor = None
            self.__locale = None
    
    def __commit_edit(self, event):
        self.__i18n_text[self.__locale] = self.__editor.get()
        self.treeview.item(self.__rowids[self.__locale], values=(self.__locale.localized_language_name, self.__i18n_text[self.__locale]))
        self.__cancel_edit(event)
    
    def set_i18n_text(self, i18n_text):
        self.__i18n_text = i18n_text
        self.treeview.delete(*self.treeview.get_children())
        for locale in Locale.all():
            self.__rowids[locale] = self.treeview.insert('', 'end', values=(locale.localized_language_name, self.__i18n_text[locale]))
    
    def get_i18n_text(self):
        return self.__i18n_text
