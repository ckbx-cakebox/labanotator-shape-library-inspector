#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as Tk
import tkinter.ttk as Ttk
from tkinter.messagebox import showerror

class PropertyType(object):
    def name(self):
        return None
    
    def options(self):
        return {}
    
    def parse(self, value):
        return None
    
    def format(self, value):
        return None
    
    def editor(self):
        return None

class StringPropertyType(PropertyType):
    def name(self):
        return 'String'
    
    def parse(self, value):
        return value
    
    def format(self, value):
        return value
    
    def editor(self, master, property):
        return InlineTextEditor(master, property)

class BytesPropertyType(PropertyType):
    def name(self):
        return 'Binary'
    
    def parse(self, value):
        return bytes(int(byte, 16) for byte in value.split())
    
    def format(self, value):
        return ' '.join(['%02X' % byte for byte in value])
    
    def editor(self, master, property):
        return InlineEntryEditor(master, property)

class BooleanPropertyType(PropertyType):
    def name(self):
        return 'Boolean'
    
    def parse(self, value):
        value = value.lower()
        if value == 'true':
            return True
        if value == 'false':
            return False
        if value == '1':
            return True
        if value == '0':
            return False
        raise ValueError("'%s' is not a valid boolean value." % value)
    
    def format(self, value):
        if value:
            return 'True'
        else:
            return 'False'
    
    def options(self):
        return { True: 'True', False: 'False'}
    
    def editor(self, master, property):
        return InlineComboboxEditor(master, property)

class IntegerPropertyType(PropertyType):
    def name(self):
        return 'Integer'
    
    def parse(self, value):
        return int(value)
    
    def format(self, value):
        return str(value)
    
    def editor(self, master, property):
        return InlineEntryEditor(master, property)

class FloatPropertyType(PropertyType):
    def name(self):
        return 'Float'
    
    def parse(self, value):
        return float(value)
    
    def format(self, value):
        return str(value)
    
    def editor(self, master, property):
        return InlineEntryEditor(master, property)

class EnumPropertyType(PropertyType):
    def __init__(self, name, options):
        self.__name = name
        self.__options = options
    
    def name(self):
        return self.__name
    
    def parse(self, value):
        for key in self.__options:
            if self.__options[key] == value:
                return key
        raise ValueError("'%s' is not a valid value." % value)
    
    def format(self, value):
        return self.__options[value]
    
    def options(self):
        return self.__options
    
    def editor(self, master, property):
        return InlineComboboxEditor(master, property)

class Property(object):
    def __init__(self, type, target, name, value):
        self.__type = type
        self.__target = target
        self.__name = name
        self.__value = value
        self.__commands = []
    
    def bind(self, command):
        self.__commands.append(command)
    
    def unbind(self, command):
        self.__commands.remove(command)
    
    @property
    def type(self):
        return self.__type
    
    @property
    def name(self):
        return self.__name
    
    @property
    def value(self):
        return self.__value
    
    @property
    def target(self):
        return self.__target
    
    def format(self):
        return self.__type.format(self.__value)
    
    def parse(self, value):
        self.__value = self.__type.parse(value)
        for command in list(self.__commands):  # enable unproperty in bound functions
            command(self, command)

class InlineEntryEditor(Tk.Entry):
    def __init__(self, master, property, **keys):
        Tk.Entry.__init__(self, master, **keys)
        self.__property = property
        self.bind("<Escape>", self.__cancel)
        self.bind("<FocusOut>", self.__commit)
        self.bind("<Return>", self.__commit)
        self.insert(Tk.END, self.__property.format())
    
    def __cancel(self, event):
        self.destroy()
    
    def __commit(self, event):
        try:
            self.__property.parse(self.get())
            self.destroy()
        except ValueError as e:
            showerror(title='Value Error', message=str(e))

class InlineTextEditor(Tk.Text):
    def __init__(self, master, property, **keys):
        Tk.Text.__init__(self, master, **keys)
        self.__property = property
        self.bind("<Escape>", self.__cancel)
        self.bind("<FocusOut>", self.__commit)
        self.insert(Tk.END, self.__property.format())
    
    def __cancel(self, event):
        self.destroy()
    
    def __commit(self, event):
        try:
            self.__property.parse(self.get('1.0', Tk.END))
        except ValueError as e:
            showerror(title='Value Error', message=str(e))
        self.destroy()

class InlineComboboxEditor(Ttk.Combobox):
    def __init__(self, master, property, **keys):
        Ttk.Combobox.__init__(self, master, **keys)
        self.__property = property
        self.bind("<Escape>", self.__cancel)
        #self.bind("<FocusOut>", self.__commit)
        self.bind("<Return>", self.__commit)
        self.bind("<<ComboboxSelected>>", self.__commit)
        self['values'] = list(self.__property.type.options().values())
        self.insert(Tk.END, self.__property.format())
    
    def __cancel(self, event):
        self.destroy()
    
    def __commit(self, event):
        try:
            self.__property.parse(self.get())
        except ValueError as e:
            showerror(title='Value Error', message=str(e))
        self.destroy()

class PropertyInspector(Tk.Frame):
    def __init__(self, master=None, **keys):
        Tk.Frame.__init__(self, master, **keys)
        self.__properties = {}
        
        self.treeview = Ttk.Treeview(self)
        self.treeview.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.scrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y, expand=False)
        self.scrollbar.configure(command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        
        self.treeview.bind('<Double-1>', self.__treeview_selected)
        self.treeview['show'] = 'tree'
        self.treeview['columns'] = ('type', 'value')
        self.treeview.column('#0', width=400)
        self.treeview.column('type')
        self.treeview.column('value')
        self.treeview.heading('type', text='Type')
        self.treeview.heading('value', text='Value')
    
    def insert(self, rowid, index, property):
        rowid = self.treeview.insert(rowid, index, text=property.name, values=(property.type.name(), property.format()))
        self.__properties[rowid] = property
        return rowid
    
    def delete_all(self):
        self.treeview.delete(*self.treeview.get_children())
        self.__properties = {}
    
    def __treeview_selected(self, event):
        rowid = self.treeview.identify_row(event.y)
        column = self.treeview.identify_column(event.x)
        if column == '#1':
            return
        if not rowid in self.__properties:
            return
        x, y, width, height = self.treeview.bbox(rowid, column=column)
        property = self.__properties[rowid]
        property.bind(self.__property_updated)
        editor = property.type.editor(self.treeview, property)
        if editor != None:
            editor.place(x=x, y=y+height//2, anchor=Tk.W, width=width)
            editor.focus_force()
    
    def __property_updated(self, property, command):
        for rowid in self.__properties:
            if self.__properties[rowid] == property:
                self.treeview.item(rowid, values=(property.type.name(), property.format()))
        property.unbind(command)
