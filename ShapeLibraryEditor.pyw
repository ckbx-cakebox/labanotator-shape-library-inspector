#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as Tk
from tkinter import filedialog
from ShapeLibrary import *
from ShapeLibraryIO import *
import os.path

class ScrollableListbox(Tk.Frame):
    def __init__(self, master, **keys):
        Tk.Frame.__init__(self, master, **keys)
        self.listbox = Tk.Listbox(self)
        self.listbox.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.scrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y, expand=False)
        self.scrollbar.configure(command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

class ShapeLibraryEntryList(Tk.Frame):
    def __init__(self, master=None, **keys):
        Tk.Frame.__init__(self, master, **keys)
        
        self.__shape_library = ShapeLibrary()
        self.__path = None
        
        self.__name_label = Tk.Label(self, font=('MS UI Gothic', '8'))
        self.__name_label.pack()
        self.__scrollable_listbox = ScrollableListbox(self)
        self.__scrollable_listbox.listbox.configure(activestyle=Tk.NONE)
        self.__scrollable_listbox.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
        
        self.__open_button = Tk.Button(self, text='Open...')
        self.__open_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__open_button.bind("<ButtonRelease-1>", self.__open_file)
        
        self.__save_button = Tk.Button(self, text='Save')
        self.__save_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__save_button.bind("<ButtonRelease-1>", self.__save_file)
        
        self.__save_as_button = Tk.Button(self, text='Save As...')
        self.__save_as_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__save_as_button.bind("<ButtonRelease-1>", self.__save_file_as)
        
        self.__up_button = Tk.Button(self, text='  ↑  ')
        self.__up_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__up_button.bind("<Button-1>", self.__move_up)
        
        self.__down_button = Tk.Button(self, text='  ↓  ')
        self.__down_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__down_button.bind("<Button-1>", self.__move_down)
    
    def get_selected_index(self):
        selections = self.__scrollable_listbox.listbox.curselection()
        if len(selections) != 1:
            return None
        return selections[0]
    
    def set_selected_index(self, index):
        self.__scrollable_listbox.listbox.select_set(index)
    
    def number_of_entries(self):
        return len(self.__shape_library.entries)
    
    def get_entry(self, index):
        return self.__shape_library.entries[index]
    
    def add_entry(self, entry):
        self.__shape_library.add(entry)
        self.__scrollable_listbox.listbox.insert(Tk.END, entry.name)
    
    def insert_entry(self, index, entry):
        self.__shape_library.insert(index, entry)
        self.__scrollable_listbox.listbox.insert(index, entry.name)
    
    def remove_entry(self, index):
        self.__shape_library.remove(index)
        self.__scrollable_listbox.listbox.delete(index)
    
    def __open_file(self, event):
        path = filedialog.askopenfilename(title = "Select file", filetypes = (("LabaNotator library files","*.lib"),))
        if path == '':
            return
        self.__path = path
        reader = ShapeLibraryReader()
        self.__shape_library = reader.read(self.__path)
        self.__scrollable_listbox.listbox.delete(0, Tk.END)
        self.__scrollable_listbox.listbox.insert(Tk.END, *[entry.name for entry in self.__shape_library.entries])
        self.__name_label.configure(text=self.__path)
    
    def __save_file(self, event):
        if self.__path == None:
            self.__save_file_as(event)
        else:
            writer = ShapeLibraryWriter()
            writer.write(self.__path, self.__shape_library)
    
    def __save_file_as(self, event):
        path = filedialog.asksaveasfilename(title = "Save file as", filetypes = (("LabaNotator library files","*.lib"),))
        if path == '':
            return
        if os.path.splitext(path)[1] != '.lib':
            path += '.lib'
        self.__path = path
        self.__save_file(event)
    
    def __move_up(self, event):
        selected_index = self.get_selected_index()
        if selected_index == None or selected_index == 0:
            return
        entry = self.get_entry(selected_index)
        self.remove_entry(selected_index)
        self.insert_entry(selected_index - 1, entry)
        self.set_selected_index(selected_index - 1)
    
    def __move_down(self, event):
        selected_index = self.get_selected_index()
        if selected_index == None or selected_index == self.number_of_entries() - 1:
            return
        entry = self.get_entry(selected_index)
        self.remove_entry(selected_index)
        self.insert_entry(selected_index + 1, entry)
        self.set_selected_index(selected_index + 1)

class ShapeLibraryDouble(Tk.Frame):
    def __init__(self, master, **keys):
        Tk.Frame.__init__(self, master, **keys)
        self.__left = ShapeLibraryEntryList(self)
        self.__left.pack(side=Tk.LEFT, padx=5, pady=5, fill=Tk.BOTH, expand=True)
        
        self.__right = ShapeLibraryEntryList(self)
        self.__right.pack(side=Tk.RIGHT, padx=5, pady=5, fill=Tk.BOTH, expand=True)
        
        self.__move_to_right_button = Tk.Button(self, text='→')
        self.__move_to_right_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__move_to_right_button.bind("<Button-1>", self.__move_to_right)
        
        self.__move_to_left_button = Tk.Button(self, text='←')
        self.__move_to_left_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__move_to_left_button.bind("<Button-1>", self.__move_to_left)
    
    def __move_to_right(self, event):
        left_index = self.__left.get_selected_index()
        if left_index == None:
            return
        shape = self.__left.get_entry(left_index)
        self.__left.remove_entry(left_index)
        right_index = self.__right.get_selected_index()
        if right_index == None:
            self.__right.add_entry(shape)
        else:
            self.__right.insert_entry(right_index, shape)
        if left_index > 0:
            self.__left.set_selected_index(left_index - 1)
        else:
            self.__left.set_selected_index(0)
    
    def __move_to_left(self, event):
        right_index = self.__right.get_selected_index()
        if right_index == None:
            return
        shape = self.__right.get_entry(right_index)
        self.__right.remove_entry(right_index)
        left_index = self.__left.get_selected_index()
        if left_index == None:
            self.__left.add_entry(shape)
        else:
            self.__left.insert_entry(left_index, shape)
        if right_index > 0:
            self.__right.set_selected_index(right_index - 1)
        else:
            self.__right.set_selected_index(0)


if __name__ == '__main__':
    root = Tk.Tk()
    root.title('LabaNotator Shape Library Editor')
    root.minsize(960, 480)
    editor = ShapeLibraryDouble(root)
    editor.pack(fill=Tk.BOTH, expand=True)
    root.mainloop()
