# module text
"""Драйвер исходного текста"""

import sys

from error import *
import loc

chEOT = chr(0)
chEOL = '\n'
chSPACE = ' '
chTAB = '\t'

_f = None
_src = ""
_i = 0
_ch = ''


def Reset():
    """Reset"""
    global _f, _src, _i, _ch
    if len(sys.argv) > 1:
        try:
            _f = open(sys.argv[1], encoding="utf-8")
        except:
            Error("Ошибка открытия файла " + sys.argv[1])
        _src = _f.read()
        _i = 0
        _ch = ''
        # nextCh()
    else:
        print('Запуск: python o.py <файл программы>')


def nextCh():
    global _i, _ch
    if _ch != chEOT:
        if _i < len(_src):
            _ch = _src[_i]
            _i += 1
            if _ch in {'\n', '\r'}:
                _ch = chEOL
            print(_ch, end="")
            if _ch in {'\n', '\r'}:
                _ch = chEOL
                loc.pos = 0
            else:
                loc.pos += 1
        else:
            _ch = chEOT


def ch():
    return _ch


def Close():
    _f.close()
