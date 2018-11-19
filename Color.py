#!/usr/bin/env python
# -*- coding: shift-jis -*-

class Color(object):
    def __init__(self, rgb):
        self.__rgb = rgb
    
    def hex(self):
        return "#%02x%02x%02x" % self.__rgb
    
    def components(self):
        return self.__rgb
    
    def __repr__(self):
        return "Color<%s>" % self.hex()
    
    def __str__(self):
        return self.hex()

