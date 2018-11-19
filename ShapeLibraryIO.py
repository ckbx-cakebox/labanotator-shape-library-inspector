#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ShapeLibrary import *
from MicrosoftLocale import Locale, I18nText
import struct
import math
import io
import os
import os.path

class ShapeLibraryStreamReader(io.BufferedReader):
    def read_int8(self):
        return struct.unpack('b', self.read(1))[0]
    
    def read_int32(self):
        return struct.unpack('<l', self.read(4))[0]
    
    def read_float32(self):
        return struct.unpack('<f', self.read(4))[0]
    
    def read_pascal8(self):
        length = struct.unpack('b', self.read(1))[0]
        return self.read(length)
    
    def read_pascal32(self):
        length = struct.unpack('<l', self.read(4))[0]
        return self.read(length)
    
    def read_pascal64(self):
        length = struct.unpack('<q', self.read(8))[0]
        return self.read(length)
    
    def read_color_rgb(self):
        return Color(struct.unpack('BBB', self.read(3)))
    
    def read_boolean8(self):
        return struct.unpack('b', self.read(1))[0] != 0
    
    def is_eos(self):
        return self.peek(1) == b''
    
    def read_i18n_text(self):
        i18n_text = I18nText()
        localizationCount = self.read_int32()
        for i in range(localizationCount):
            lcid = int(self.read_pascal32()[7:])
            locale = Locale.fromLCID(lcid)
            localizedText = self.read_pascal32().decode(locale.encoding)
            i18n_text[locale] = localizedText
        return i18n_text

class ShapeLibraryStreamWriter(io.BufferedWriter):
    def write_int8(self, value):
        return self.write(struct.pack('b', value))
    
    def write_int32(self, value):
        return self.write(struct.pack('<l', value))
    
    def write_float32(self, value):
        return self.write(struct.pack('<f', value))
    
    def write_pascal8(self, value):
        self.write(struct.pack('<b', len(value)))
        self.write(value)
    
    def write_pascal32(self, value):
        self.write(struct.pack('<l', len(value)))
        self.write(value)
    
    def write_pascal64(self, value):
        self.write(struct.pack('<q', len(value)))
        self.write(value)
    
    def write_color_rgb(self, value):
        return self.write(struct.pack('BBB', *value.components()))
    
    def write_boolean8(self, value):
        return self.write(struct.pack('b', value != 0))
    
    def write_i18n_text(self, i18n_text):
        locales = [locale for locale in Locale.all() if i18n_text[locale] != '']
        self.write(struct.pack('<l', len(locales)))
        for locale in locales:
            self.write_pascal32(('Caption%04d' % locale.lcid).encode('iso-8859-1'))
            self.write_pascal32(i18n_text[locale].encode(locale.encoding))
        return True  # todo


class ShapeLibraryReader(object):
    def read(self, path):
        sl = ShapeLibrary()
        with open(path, 'rb') as f:
            reader = ShapeLibraryStreamReader(f)
            if reader.read(10) != b'TCADLIBX.k':
                raise IOError('bad magic')
            sl.readonly = reader.read_int8()
            sl.name = reader.read_i18n_text()
            while True:
                if reader.is_eos():
                    break
                entry = self.__read_shape_library_entry(reader)
                sl.add(entry)
        return sl
    
    def __read_shape_library_entry(self, reader):
        name = reader.read_pascal8().decode('iso-8859-1')
        contents = reader.read_pascal32()
        reader = ShapeLibraryStreamReader(io.BytesIO(contents))
        width = reader.read_int32()
        height = reader.read_int32()
        localizedName = reader.read_i18n_text()
        shapeCount = reader.read_int32()
        shape = self.__read_shape(reader)
        return ShapeLibraryEntry(name, width, height, localizedName, shape)
    
    def __read_shape(self, reader):
        shape = Shape()
        shapeType = reader.read(16).decode('iso-8859-1').rstrip()
        shape['ShapeType'] = shapeType
        shape['_Reserved01'] = reader.read(4)  #  00 00 00 00
        shape['ShapeAutoNumber'] = reader.read_int32()
        shape['ShapeRef'] = reader.read_int32()
        shape['_Reserved02'] = reader.read(4) #  00 00 00 00
        shape['ParentShapeRef'] = reader.read_int32()  # root = -1, child = parent shape ref
        childShapeCount = reader.read_int32()
        shape['ChildShapeRefs'] = [reader.read_int32() for i in range(0, childShapeCount)]
        shape['_Reserved03'] = reader.read(4) #  00 00 00 00 
        pointsCount = reader.read_int32()
        shape['Points'] = [(reader.read_float32(), reader.read_float32()) for i in range(0, pointsCount)]
        shape['_Reserved04'] = reader.read(4)  # 00 00 00 00
        shape['_Reserved05'] = reader.read_float32()  # vary for rotation
        shape['_Reserved06'] = reader.read_float32()  # vary for rotation
        shape['_Reserved07'] = reader.read(4)  # 00 00 00 00
        shape['Rotation'] = reader.read_float32()
        shape['_Reserved08'] = reader.read(8)  # 00 00 00 00 00 00 00 00
        shape['FillColor'] = reader.read_color_rgb()
        shape['_Reserved10'] = reader.read(2)  # 00 01
        shape['ShapeName'] = reader.read_pascal32().decode('iso-8859-1')
        shape['_Reserved12'] = reader.read(8)  #  FF FF FF 00  00 00 00 00
        shape['FontName'] = reader.read_pascal32().decode('iso-8859-1')
        shape['_Reserved13'] = reader.read(1)  # 01
        shape['FontColor'] = reader.read_color_rgb()
        shape['_Reserved14'] = reader.read(5)  # FF F0 FF FF FF (g) or 00 E3 FF FF FF
        shape['FontSize'] = reader.read_int32()
        shape['_Reserved15'] = reader.read(5)  # 00 60 00 00 00
        textStyle = reader.read_int8()
        shape['TextBold'] = (textStyle & 1) != 0
        shape['TextItalic'] = (textStyle & 2) != 0
        shape['TextUnderline'] = (textStyle & 4) != 0
        shape['TextStrikethrough'] = (textStyle & 8) != 0
        shape['_Reserved17'] = reader.read(13)  # 00 00 00 00 00 00 00 00 17 00 00 00 00
        shape['StrokeColor'] = reader.read_color_rgb()
        shape['_Reserved21'] = reader.read(2)  # 00 04
        shape['StrokeType'] = reader.read_int8()
        shape['StrokeWidth'] = reader.read_int32()
        shape['_Reserved23'] = reader.read_i18n_text()
        shape['FlipHorizontal'] = reader.read_boolean8()
        shape['FlipVertical'] = reader.read_boolean8()
        shape['_Reserved24'] = reader.read(1)  #  01
        commentCount = reader.read_int32()
        shape['Comments'] = [reader.read_pascal32().decode('iso-8859-1') for _ in range(0, commentCount)]
        shape['_Reserved25'] = reader.read(10)  # 00 0A 00 00 00 00 0A 00 00 00
        shape['Locked'] = reader.read_boolean8()
        shape['_Reserved29'] = reader.read(3)  # 00 00 01
        shape['Rotatable'] = reader.read_boolean8()
        shape['Resizable'] = reader.read_boolean8()
        shape['ParentCenter'] = reader.read_boolean8()
        
        #  Text Additional
        if shapeType == 'TMyText':
            shape['_Reserved36(TMyText)'] = reader.read(6)  # 00 01 01 00 00 00
            shape['Text'] = reader.read_pascal32().decode('iso-8859-1')
            shape['_Reserved42(TMyText)'] = reader.read(1)  # 00
            shape['TextAlign'] = reader.read_int8()
            shape['TextWrap'] = reader.read_int8()
        
        if shapeType == 'TMyLine' or shapeType == 'TMyPolygon' or shapeType == 'TMyPolyLine' or shapeType == 'TMyFreeLine':
            shape['ArrowDegree'] = reader.read_int32()
            shape['ArrowLength'] = reader.read_int8()
            shape['ArrowOffset'] = reader.read_int8()
            shape['ArrowStyle'] = reader.read_int8()
        
        if shapeType == 'TMyImage':
            shape['Bitmap'] = reader.read_pascal64()
        
        if shapeType == 'TMyGroup':
            shape['_Reserved36(TMyGroup)'] = reader.read(16)
            shape['ChildShapes'] = [self.__read_shape(reader) for i in range(0, childShapeCount)]
        
        if shapeType == 'TMyCombine':
            shape['_Reserved36(TMyCombine)'] = reader.read(16)
            shape['ChildShapes'] = [self.__read_shape(reader) for i in range(0, childShapeCount)]
        
        if shapeType == 'TMyElliArc':
            shape['_Reserved36(TMyElliArc)'] = reader.read(2)  # 00 00
        
        if shapeType == 'TMySpiral':
            shape['_Reserved36(TMySpiral)'] = reader.read(4)  # 00 00 00 00
            shape['Distance'] = reader.read_float32()
        
        if shapeType == 'TMySinusLine':
            shape['Period'] = reader.read_int32()
        
        return shape


class ShapeLibraryWriter(object):
    def write(self, path, sl):
        if os.path.exists(path):
            if os.path.exists(path + '.bak'):
                os.unlink(path + '.bak')
            os.rename(path, path + '.bak')
        with open(path, 'wb') as f:
            writer = ShapeLibraryStreamWriter(f)
            writer.write(b'TCADLIBX.k')
            writer.write_boolean8(sl.readonly)
            writer.write_i18n_text(sl.name)
            for entry in sl.entries:
                self.__write_shape_library_entry(writer, entry)
            writer.flush()
    
    def __write_shape_library_entry(self, writer, entry):
        writer.write_pascal8(entry.name.encode('iso-8859-1'))
        g = io.BytesIO()
        subwriter = ShapeLibraryStreamWriter(g)
        subwriter.write_int32(entry.width)
        subwriter.write_int32(entry.height)
        subwriter.write_i18n_text(entry.i18n_name)
        subwriter.write_int32(entry.number_of_descendants)
        self.__write_shape(subwriter, entry.shape)
        subwriter.flush()
        contents = g.getvalue()
        writer.write_int32(len(contents))
        writer.write(contents)
    
    def __write_shape(self, writer, shape):
        writer.write(shape.type.ljust(16).encode('iso-8859-1'))
        writer.write(shape['_Reserved01'])
        writer.write_int32(shape['ShapeAutoNumber'])
        writer.write_int32(shape['ShapeRef'])
        writer.write(shape['_Reserved02'])
        writer.write_int32(shape['ParentShapeRef'])
        writer.write_int32(len(shape.children))
        for ref in shape['ChildShapeRefs']:
            writer.write_int32(ref)
        writer.write(shape['_Reserved03'])
        writer.write_int32(len(shape.points))
        for point in shape.points:
            writer.write_float32(point[0])
            writer.write_float32(point[1])
        writer.write(shape['_Reserved04'])
        writer.write_float32(shape['_Reserved05'])
        writer.write_float32(shape['_Reserved06'])
        writer.write(shape['_Reserved07'])
        writer.write_float32(shape['Rotation'])
        writer.write(shape['_Reserved08'])
        writer.write_color_rgb(shape['FillColor'])
        writer.write(shape['_Reserved10'])
        writer.write_pascal32(shape.name.encode('iso-8859-1'))
        writer.write(shape['_Reserved12'])
        writer.write_pascal32(shape['FontName'].encode('iso-8859-1'))
        writer.write(shape['_Reserved13'])
        writer.write_color_rgb(shape['FontColor'])
        writer.write(shape['_Reserved14'])
        writer.write_int32(shape['FontSize'])
        writer.write(shape['_Reserved15'])
        writer.write_int8((shape['TextBold']) | (shape['TextItalic'] << 1) | (shape['TextUnderline'] << 2) | (shape['TextStrikethrough'] << 3))
        writer.write(shape['_Reserved17'])
        writer.write_color_rgb(shape['StrokeColor'])
        writer.write(shape['_Reserved21'])
        writer.write_int8(shape['StrokeType'])
        writer.write_int32(shape['StrokeWidth'])
        writer.write_i18n_text(shape['_Reserved23'])
        writer.write_boolean8(shape['FlipHorizontal'])
        writer.write_boolean8(shape['FlipVertical'])
        writer.write(shape['_Reserved24'])
        writer.write_int32(len(shape['Comments']))
        for comment in shape['Comments']:
            writer.write_pascal32(comment.encode('iso-8859-1'))
        writer.write(shape['_Reserved25'])
        writer.write_boolean8(shape['Locked'])
        writer.write(shape['_Reserved29'])
        writer.write_boolean8(shape['Rotatable'])
        writer.write_boolean8(shape['Resizable'])
        writer.write_boolean8(shape['ParentCenter'])
        
        if shape.type == 'TMyText':
            writer.write(shape['_Reserved36(TMyText)'])
            writer.write_pascal32(shape['text'].encode('iso-8859-1'))
            writer.write(shape['_Reserved42(TMyText)'])
            writer.write_int8(shape['TextAlign'])
            writer.write_int8(shape['TextWrap'])
        
        if shape.type in ['TMyLine', 'TMyPolygon', 'TMyPolyLine', 'TMyFreeLine']:
            writer.write_int32(shape['ArrowDegree'])
            writer.write_int8(shape['ArrowLength'])
            writer.write_int8(shape['ArrowOffset'])
            writer.write_int8(shape['ArrowStyle'])
        
        if shape.type == 'TMyImage':
            writer.write_pascal64(shape['Bitmap'])
        
        if shape.type == 'TMyGroup':
            writer.write(shape['_Reserved36(TMyGroup)'])
            for subshape in shape.children:
                self.__write_shape(writer, subshape)
        
        if shape.type == 'TMyCombine':
            writer.write(shape['_Reserved36(TMyCombine)'])
            for subshape in shape.children:
                self.__write_shape(writer, subshape)
        
        if shape.type == 'TMyElliArc':
            writer.write(shape['_Reserved36(TMyElliArc)'])
        
        if shape.type == 'TMySpiral':
            writer.write(shape['_Reserved36(TMySpiral)'])
            writer.write_float32(shape['Distance'])
        
        if shape.type == 'TMySinusLine':
            writer.write_int32(shape['Period'])
    
    
