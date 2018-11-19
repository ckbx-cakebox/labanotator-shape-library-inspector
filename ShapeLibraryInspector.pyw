#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as Tk
import tkinter.ttk as Ttk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showerror
from tkinter import filedialog
import os.path
import re

from ShapeLibrary import *
from ShapeLibraryIO import *
from Color import Color
from MicrosoftLocale import Locale
from I18nTextView import I18nTextView
from PropertyInspector import *

class I18nTextEditor(Tk.Toplevel):
    def __init__(self, master, property, **keys):
        Tk.Toplevel.__init__(self, master, **keys)
        self.__property = property
        self.entry = I18nTextView(self)
        self.entry.set_i18n_text(self.__property.value.copy())
        self.entry.pack(fill=Tk.BOTH, expand=True)
        self.footer = Tk.Frame(self)
        self.footer.pack(side=Tk.BOTTOM)
        self.ok_button = Tk.Button(self.footer, text='OK', command=self.__commit)
        self.ok_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.cancel_button = Tk.Button(self.footer, text='Cancel', command=self.__cancel)
        self.cancel_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.geometry('1024x768')
        self.grab_set()
    
    def __commit(self):
        self.__property.parse(self.entry.get_i18n_text())
        self.destroy()
    
    def __cancel(self):
        self.destroy()

class I18nTextPropertyType(PropertyType):
    def name(self):
        return 'I18nText'
    
    def parse(self, value):
        return value
    
    def format(self, value):
        s = value[Locale.current()]
        if s != '':
            return s
        for locale in Locale.all():
            if value[locale] != '':
                return value[locale]
        return ''
    
    def editor(self, master, property):
        I18nTextEditor(master, property)

class ColorPropertyType(PropertyType):
    def name(self):
        return 'Color'
    
    def parse(self, value):
        value = value.lower()
        match = re.match(r'#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})', value)
        if match is None:
            raise ValueError("'%s' is not a valid color hexcode." % value)
        r = int(match.group(1), 16)
        g = int(match.group(2), 16)
        b = int(match.group(3), 16)
        return Color((r, g, b))
    
    def format(self, value):
        return value.hex()
    
    def editor(self, master, property):
        color = askcolor(initialcolor=property.format(), parent=master, title=property.name)
        property.parse(color[1])

class PointsPropertyType(PropertyType):
    def name(self):
        return '[(Float, Float)]'
    
    def parse(self, value):
        values = [float(elem) for elem in value.split()]
        if len(values) % 2 == 1:
            raise ValueError('number of elements should be even, but %d' % len(values))
        return [(values[i*2], values[i*2+1]) for i in range(0, len(values)//2)]
    
    def format(self, points):
        return ' '.join([str(elem) for point in points for elem in point])
    
    def editor(self, master, property):
        return InlineEntryEditor(master, property)

class IntegerListPropertyType(PropertyType):
    def name(self):
        return '[Integer]'
    
    def parse(self, value):
        return [int(elem) for elem in value.split()]
    
    def format(self, value):
        return ' '.join([str(elem) for elem in value])
    
    def editor(self, master, property):
        return InlineEntryEditor(master, property)

class StringListPropertyType(PropertyType):
    def name(self):
        return '[String]'
    
    def parse(self, value):
        if value == '':
            return []
        return [value]
    
    def format(self, value):
        if len(value) == 0:
            return ''
        return value[0]
    
    def editor(self, master, property):
        return InlineEntryEditor(master, property)

class ShapeLibraryInspector(PropertyInspector):
    def __init__(self, master=None, **keys):
        PropertyInspector.__init__(self, master, **keys)
        self.__shape_library = ShapeLibrary()
    
    def set_shape_library(self, shapeLibrary):
        self.__shape_library = shapeLibrary
        self.delete_all()
        self.__add_shape_library_node('', 'Shape Library', self.__shape_library)
    
    def __create_property_type(self, name, value):
        if name == 'Comments':
            return StringListPropertyType()
        elif name == 'ChildShapeRefs':
            return IntegerListPropertyType()
        elif name == 'Points':
            return PointsPropertyType()
        elif name == 'StrokeType':
            return EnumPropertyType('StrokeStyle', { 0: 'Solid', 1: 'Dash', 2: 'Dot', 3: 'Dash Dot', 4: 'Dash Dot Dot', 5: 'Clear' })
        elif name == 'ShapeType':
            return ShapeTypePropertyType('ShapeType', {
                'TMyText': 'TMyText',
                'TMyLine': 'TMyLine',
                'TMyPolygon': 'TMyPolygon',
                'TMyPolyLine': 'TMyPolyLine',
                'TMyFreeLine': 'TMyFreeLine',
                'TMyImage': 'TMyImage',
                'TMyGroup': 'TMyGroup',
                'TMyCombine': 'TMyCombine',
                'TMyElliArc': 'TMyElliArc',
                'TMySpiral': 'TMySpiral',
                'TMySinusLine': 'TMySinusLine',
            })
        elif isinstance(value, bool):
            return BooleanPropertyType()
        elif isinstance(value, int):
            return IntegerPropertyType()
        elif isinstance(value, float):
            return FloatPropertyType()
        elif isinstance(value, str):
            return StringPropertyType()
        elif isinstance(value, I18nText):
            return I18nTextPropertyType()
        elif isinstance(value, Color):
            return ColorPropertyType()
        elif isinstance(value, bytes):
            return BytesPropertyType()
        else:
            return PropertyType()
    
    def __create_property(self, type, target, name, value):
        property = Property(type, target, name, value)
        property.bind(self.__property_changed)
        return property
    
    def __property_changed(self, property, command):
        name = property.name
        value = property.value
        if isinstance(property.target, ShapeLibrary):
            sl = property.target
            if name == 'ReadOnly':
                sl.readonly = value
            elif name == 'Name':
                sl.name = value
        elif isinstance(property.target, ShapeLibraryEntry):
            entry = property.target
            if name == 'Name':
                entry.name = value
            elif name == 'Width':
                entry.width = value
            elif name == 'Height':
                entry.height = value
            elif name == 'I18nName':
                entry.i18n_name = value
        elif isinstance(property.target, Shape):
            property.target[name] = value
    
    def __add_shape_library_node(self, parentNode, name, value):
        sl = self.__shape_library
        node = self.treeview.insert(parentNode, Tk.END, text='<root>', values=('ShapeLibrary', ''), open=True)
        self.insert(node, Tk.END, self.__create_property(I18nTextPropertyType(), sl, 'Name', sl.name))
        self.insert(node, Tk.END, self.__create_property(BooleanPropertyType(), sl, 'ReadOnly', sl.readonly))
        subnode = self.treeview.insert(node, Tk.END, text='ShapeLibraryEntries', values=('[ShapeLibraryEntry]', ''), open=True)
        for entry in self.__shape_library.entries:
            self.__add_shape_library_entry_node(subnode, entry)
    
    def __add_shape_library_entry_node(self, parentNode, entry):
        node = self.treeview.insert(parentNode, Tk.END, text=entry.name, values=('ShapeLibraryEntry', ''))
        self.insert(node, Tk.END, self.__create_property(StringPropertyType(), entry, 'Name', entry.name))
        self.insert(node, Tk.END, self.__create_property(IntegerPropertyType(), entry, 'Width', entry.width))
        self.insert(node, Tk.END, self.__create_property(IntegerPropertyType(), entry, 'Height', entry.height))
        self.insert(node, Tk.END, self.__create_property(I18nTextPropertyType(), entry, 'I18nName', entry.i18n_name))
        subnode = self.__add_shape_node(node, entry.shape)
        self.treeview.item(subnode, open=True)
    
    def __add_shape_node(self, parentNode, shape):
        node = self.treeview.insert(parentNode, Tk.END, text=shape.name, values=('Shape<%s>' % shape.type, ''))
        for key in sorted(shape.getProperties().keys()):
            if key == 'ChildShapes':
                if len(shape.children) > 0:
                    subnode = self.treeview.insert(node, Tk.END, text='ChildShapes', values=('[Shape]', ''))
                    for childShape in shape.children:
                        self.__add_shape_node(subnode, childShape)
            else:
                property = self.__create_property(self.__create_property_type(key, shape[key]), shape, key, shape[key])
                self.insert(node, Tk.END, property)
        return node

class ShapeTypePropertyType(EnumPropertyType):
    def name(self):
        return 'ShapeType'
    
    def parse(self, value):
        raise ValueError('Unsupported operation')
    
    def format(self, value):
        return value

class ShapeLibraryInspectorFrame(Tk.Frame):
    def __init__(self, master=None, **keys):
        Tk.Frame.__init__(self, master, **keys)
        
        self.__shape_library = ShapeLibrary()
        self.__path = None
        
        self.__filename_label = Tk.Label(self, font=('MS UI Gothic', '8'))
        self.__filename_label.pack()
        self.__shape_library_inspector = ShapeLibraryInspector(self)
        self.__shape_library_inspector.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
        
        self.__open_button = Tk.Button(self, text='Open...')
        self.__open_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__open_button.bind("<ButtonRelease-1>", self.__open_file)
        
        self.__save_button = Tk.Button(self, text='Save')
        self.__save_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__save_button.bind("<ButtonRelease-1>", self.__save_file)
        
        self.__save_as_button = Tk.Button(self, text='Save As...')
        self.__save_as_button.pack(side=Tk.LEFT, padx=5, pady=5)
        self.__save_as_button.bind("<ButtonRelease-1>", self.__save_file_as)
    
    def __open_file(self, event):
        path = filedialog.askopenfilename(title = "Select file", filetypes = (("LabaNotator library files","*.lib"),))
        if path == '':
            return
        self.__path = path
        reader = ShapeLibraryReader()
        self.__shape_library = reader.read(self.__path)
        self.__reload_shape_library()
    
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
    
    def __reload_shape_library(self):
        self.__shape_library_inspector.set_shape_library(self.__shape_library)
        self.__filename_label.configure(text=self.__path)


if __name__ == '__main__':
    root = Tk.Tk()
    root.title('LabaNotator Shape Library Inspector')
    root.minsize(1024, 768)
    editor = ShapeLibraryInspectorFrame(root)
    editor.pack(fill=Tk.BOTH, expand=True)
    root.mainloop()
