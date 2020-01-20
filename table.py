# module table
"""Таблица имен"""

import builtins

import error
import cat

_table = []


def openScope():
    _table.append({})


def closeScope():
    _table.pop()


def add(item):
    top = _table[-1]
    top[item.name] = item


def print():
    pr = builtins.print
    pr()
    for scope in _table:
        pr("---------------")
        for key, value in scope.items():
            pr(value)


def _exist(name):
    top = _table[-1]
    return name in top


def new(item):
    if _exist(item.name):
        error.cntError("Повторное объявление имени")
    else:
        add(item)
    return item


def find(name):
    for scope in _table:
        if name in scope:
            return scope[name]
    error.cntError("Неизвестное имя")


def getVars():
    vars = []
    for scope in _table:
        for item in scope.values():
            if type(item) == cat.Var:
                vars.append(item)
    return vars
