#!/usr/bin/env python
# -*- coding: shift-jis -*-

import MicrosoftLocale
from Color import Color

class ShapeLibrary(object):
    def __init__(self):
        self.__name = MicrosoftLocale.I18nText()
        self.__readOnly = False
        self.__entries = []
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name
    
    @property
    def readonly(self):
        return self.__readOnly
    
    @readonly.setter
    def readonly(self, value):
        if value:
            self.__readOnly = True
        else:
            self.__readOnly = False
    
    @property
    def entries(self):
        return self.__entries
    
    def add(self, entry):
        self.__entries.append(entry)
    
    def insert(self, index, entry):
        self.__entries.insert(index, entry)
    
    def remove(self, index):
        del self.__entries[index]
    
    def __str__(self):
        return "\n\n".join("%s" % entry for entry in self.__entries)

class ShapeLibraryEntry(object):
    def __init__(self, name, width, height, i18n_name, shape):
        self.__name = name
        self.__width = width
        self.__height = height
        self.__i18n_name = i18n_name
        self.__shape = shape
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value):
        self.__name = name
    
    @property
    def width(self):
        return self.__width
    
    @width.setter
    def width(self, value):
        self.__width = value
    
    @property
    def height(self):
        return self.__height
    
    @height.setter
    def height(self, value):
        self.__height = value
    
    @property
    def i18n_name(self):
        return self.__i18n_name
    
    @i18n_name.setter
    def i18n_name(self, value):
        self.__i18n_name = value
    
    @property
    def shape(self):
        return self.__shape
    
    @property
    def number_of_descendants(self):
        return self.__number_of_descendants(self.__shape)
    
    def __number_of_descendants(self, shape):
        return 1 + sum(self.__number_of_descendants(subshape) for subshape in shape.children)
    
    def __str__(self):
        return '"%s" (%dx%d %s) %s' % (self.__name, self.__width, self.__height, self.__i18n_name, self.__shape)

class Shape(object):
    def __init__(self):
        self.__properties = {}
    
    def __iter__(self):
        return iter(sorted(self.__properties.keys()))
    
    def __getitem__(self, name):
        if name in self.__properties:
            return self.__properties[name]
        return None
    
    def __setitem__(self, name, value):
        self.__properties[name] = value
    
    
    @property
    def type(self):
        return '' if self['ShapeType'] is None else self['ShapeType']
    
    @property
    def name(self):
        return '' if self['ShapeName'] is None else self['ShapeName']
    
    @property
    def points(self):
        return [] if self['Points'] is None else self['Points']
    
    @property
    def children(self):
        return [] if self['ChildShapes'] is None else self['ChildShapes']
    
    def __str__(self):
        return '%s' % self.__properties
