#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import ctypes.wintypes
import functools

class I18nText(object):
    def __init__(self, strings = None):
        self.__strings = {}
        if strings != None:
            self.__strings = strings
    
    def __setitem__(self, locale, string):
        if string == '':
            del self.__strings[locale]
        else:
            self.__strings[locale] = string
    
    def __getitem__(self, locale):
        if locale in self.__strings:
            return self.__strings[locale]
        else:
            return ''
    
    def __delitem__(self, locale):
        del self.__strings[locale]
    
    def __iter__(self):
        return iter(self.__strings.keys())
    
    def __repr__(self):
        return 'I18nText(%s)' % self.__strings
    
    def copy(self):
        return I18nText(self.__strings.copy())

class Locale(object):
    LOCALE_NOUSEROVERRIDE = 0x80000000
    LOCALE_USE_CP_ACP = 0x40000000
    LOCALE_ILANGUAGE = 1
    LOCALE_SLANGUAGE = 2
    LOCALE_SENGLANGUAGE = 0x1001
    LOCALE_SABBREVLANGNAME = 3
    LOCALE_SNATIVELANGNAME = 4
    LOCALE_ICOUNTRY = 5
    LOCALE_SCOUNTRY = 6
    LOCALE_SENGCOUNTRY = 0x1002
    LOCALE_SABBREVCTRYNAME = 7
    LOCALE_SNATIVECTRYNAME = 8
    LOCALE_IDEFAULTLANGUAGE = 9
    LOCALE_IDEFAULTCOUNTRY = 10
    LOCALE_IDEFAULTCODEPAGE = 11
    LOCALE_IDEFAULTANSICODEPAGE = 0x1004
    LOCALE_SLIST = 12
    LOCALE_IMEASURE = 13
    LOCALE_SDECIMAL = 14
    LOCALE_STHOUSAND = 15
    LOCALE_SGROUPING = 16
    LOCALE_IDIGITS = 17
    LOCALE_ILZERO = 18
    LOCALE_INEGNUMBER = 0x1010
    LOCALE_SNATIVEDIGITS = 19
    LOCALE_SCURRENCY = 20
    LOCALE_SINTLSYMBOL = 21
    LOCALE_SMONDECIMALSEP = 22
    LOCALE_SMONTHOUSANDSEP = 23
    LOCALE_SMONGROUPING = 24
    LOCALE_ICURRDIGITS = 25
    LOCALE_IINTLCURRDIGITS = 26
    LOCALE_ICURRENCY = 27
    LOCALE_INEGCURR = 28
    LOCALE_SDATE = 29
    LOCALE_STIME = 30
    LOCALE_SSHORTDATE = 31
    LOCALE_SLONGDATE = 32
    LOCALE_STIMEFORMAT = 0x1003
    LOCALE_IDATE = 33
    LOCALE_ILDATE = 34
    LOCALE_ITIME = 35
    LOCALE_ITIMEMARKPOSN = 0x1005
    LOCALE_ICENTURY = 36
    LOCALE_ITLZERO = 37
    LOCALE_IDAYLZERO = 38
    LOCALE_IMONLZERO = 39
    LOCALE_S1159 = 40
    LOCALE_S2359 = 41
    LOCALE_ICALENDARTYPE = 0x1009
    LOCALE_IOPTIONALCALENDAR = 0x100B
    LOCALE_IFIRSTDAYOFWEEK = 0x100C
    LOCALE_IFIRSTWEEKOFYEAR = 0x100D
    LOCALE_SDAYNAME1 = 42
    LOCALE_SDAYNAME2 = 43
    LOCALE_SDAYNAME3 = 44
    LOCALE_SDAYNAME4 = 45
    LOCALE_SDAYNAME5 = 46
    LOCALE_SDAYNAME6 = 47
    LOCALE_SDAYNAME7 = 48
    LOCALE_SABBREVDAYNAME1 = 49
    LOCALE_SABBREVDAYNAME2 = 50
    LOCALE_SABBREVDAYNAME3 = 51
    LOCALE_SABBREVDAYNAME4 = 52
    LOCALE_SABBREVDAYNAME5 = 53
    LOCALE_SABBREVDAYNAME6 = 54
    LOCALE_SABBREVDAYNAME7 = 55
    LOCALE_SMONTHNAME1 = 56
    LOCALE_SMONTHNAME2 = 57
    LOCALE_SMONTHNAME3 = 58
    LOCALE_SMONTHNAME4 = 59
    LOCALE_SMONTHNAME5 = 60
    LOCALE_SMONTHNAME6 = 61
    LOCALE_SMONTHNAME7 = 62
    LOCALE_SMONTHNAME8 = 63
    LOCALE_SMONTHNAME9 = 64
    LOCALE_SMONTHNAME10 = 65
    LOCALE_SMONTHNAME11 = 66
    LOCALE_SMONTHNAME12 = 67
    LOCALE_SMONTHNAME13 = 0x100E
    LOCALE_SABBREVMONTHNAME1 = 68
    LOCALE_SABBREVMONTHNAME2 = 69
    LOCALE_SABBREVMONTHNAME3 = 70
    LOCALE_SABBREVMONTHNAME4 = 71
    LOCALE_SABBREVMONTHNAME5 = 72
    LOCALE_SABBREVMONTHNAME6 = 73
    LOCALE_SABBREVMONTHNAME7 = 74
    LOCALE_SABBREVMONTHNAME8 = 75
    LOCALE_SABBREVMONTHNAME9 = 76
    LOCALE_SABBREVMONTHNAME10 = 77
    LOCALE_SABBREVMONTHNAME11 = 78
    LOCALE_SABBREVMONTHNAME12 = 79
    LOCALE_SABBREVMONTHNAME13 = 0x100F
    LOCALE_SPOSITIVESIGN = 80
    LOCALE_SNEGATIVESIGN = 81
    LOCALE_IPOSSIGNPOSN = 82
    LOCALE_INEGSIGNPOSN = 83
    LOCALE_IPOSSYMPRECEDES = 84
    LOCALE_IPOSSEPBYSPACE = 85
    LOCALE_INEGSYMPRECEDES = 86
    LOCALE_INEGSEPBYSPACE = 87
    LOCALE_FONTSIGNATURE = 88
    LOCALE_SISO639LANGNAME = 89
    LOCALE_SISO3166CTRYNAME = 90
    LOCALE_SYSTEM_DEFAULT = 0x800
    LOCALE_USER_DEFAULT = 0x400
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __GetLocaleInfoEx(name, type):
        buffer = ctypes.create_unicode_buffer(256)
        ctypes.windll.kernel32.GetLocaleInfoEx(name, type, buffer, ctypes.sizeof(buffer))
        return buffer.value
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __LCIDToLocalName(lcid):
        LOCALE_NAME_MAX_LENGTH = 85
        buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
        ctypes.windll.kernel32.LCIDToLocalName(lcid, buffer, ctypes.sizeof(buffer), 0)
        return buffer.value
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __LocaleNameToLCID(name):
        return ctypes.windll.kernel32.LocaleNameToLCID(name, 0)
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __EnumSystemLocalesEx():
        return _LocaleEnum().EnumSystemLocalesEx(_LocaleEnum.LOCALE_ALL, None, None)
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __GetUserDefaultLocaleName():
        LOCALE_NAME_MAX_LENGTH = 85
        buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
        ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, ctypes.sizeof(buffer))
        return buffer.value
    
    @classmethod
    def all(cls):
        return cls.__EnumSystemLocalesEx()
    
    @classmethod
    def current(cls):
        name = cls.__GetUserDefaultLocaleName()
        for locale in cls.all():
            if locale.name == name:
                return locale
        return None
    
    @classmethod
    def fromLCID(cls, lcid):
        for locale in cls.all():
            if locale.lcid == lcid:
                return locale
        return None
    
    def __init__(self, name):
        self.__name = name
    
    def __eq__(self, other):
        if not isinstance(other, Locale):
            return False
        return self.__name == other.name
    
    def __hash__(self):
        return hash(self.__name)
    
    def info(self, type):
        return self.__GetLocaleInfoEx(self.__name, type)
    
    @property
    def name(self):
        return self.__name
    
    @property
    def lcid(self):
        return self.__LocaleNameToLCID(self.__name)
    
    @property
    def codepage(self):
        return int(self.info(self.LOCALE_IDEFAULTCODEPAGE))
    
    @property
    def native_language_name(self):
        return self.info(self.LOCALE_SNATIVELANGNAME)
    
    @property
    def native_country_name(self):
        return self.info(self.LOCALE_SNATIVECTRYNAME)
    
    @property
    def localized_language_name(self):
        return self.info(self.LOCALE_SLANGUAGE)
    
    @property
    def localized_country_name(self):
        return self.info(self.LOCALE_SCOUNTRY)
    
    @property
    def english_language_name(self):
        return self.info(self.LOCALE_SENGLANGUAGE)
    
    @property
    def english_country_name(self):
        return self.info(self.LOCALE_SENGCOUNTRY)
    
    @property
    def encoding(self):
        if self.codepage == 1:
            return 'utf-16'
        return 'cp%d' % self.codepage
    
    def __repr__(self):
        return 'Locale("%s")' % self.__name


class _LocaleEnum(object):
    LCID_INSTALLED = 1
    LCID_SUPPORTED = 2
    LCID_ALTERNATE_SORTS = 4
    
    LOCALE_ALL = 0x00
    LOCALE_WINDOWS = 0x01
    LOCALE_SUPPLEMENTAL = 0x02
    LOCALE_ALTERNATE_SORTS = 0x04
    LOCALE_REPLACEMENT = 0x08
    LOCALE_NEUTRALDATA = 0x10
    LOCALE_SPECIFICDATA = 0x20
    
    def __callback(self, lcidHexString):
        lcid = int(lcidHexString, 16)
        self.__locales.append(Locale.fromLCID(lcid))
        return True
    
    def __callbackEx(self, localeName, dwUnknownValue, lParam):
        self.__locales.append(Locale(localeName))
        return True
    
    def EnumSystemLocalesA(self, dwFlags):
        self.__locales = []
        callback = ctypes.CFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.LPSTR)(self.__callback)
        ctypes.windll.kernel32.EnumSystemLocalesA(callback, dwFlags)
        return self.__locales
    
    def EnumSystemLocalesW(self, dwFlags):
        self.__locales = []
        callback = ctypes.CFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.LPWSTR)(self.__callback)
        ctypes.windll.kernel32.EnumSystemLocalesW(callback, dwFlags)
        return self.__locales
    
    def EnumSystemLocalesEx(self, dwFlags, lParam, lpReserved):
        self.__locales = []
        callback = ctypes.CFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD, ctypes.wintypes.LPARAM)(self.__callbackEx)
        ctypes.windll.kernel32.EnumSystemLocalesEx(callback, dwFlags, lParam, lpReserved)
        return self.__locales

