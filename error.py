# module error
"""Сообщения об ошибках"""

import loc
import text


def _error(pos, msg):
    while text.ch() != text.chEOL and text.ch() != text.chEOT:
        text.nextCh()
    print(' ' * (pos - 1), '^', sep='')
    print(msg)
    exit(1)


def lexError(msg):
    _error(loc.pos, msg)


def Expected(msg):
    _error(loc.lexPos, "Ожидается " + str(msg))


def posExpected(msg, p):
    _error(p, "Ожидается " + str(msg))


def posError(msg, p):
    _error(p, str(msg))


def Error(msg):
    print()
    print(msg)
    exit(1)


def cntError(msg):
    _error(loc.lexPos, str(msg))
