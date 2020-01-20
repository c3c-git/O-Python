# module cat
"""Категории в таблице имен"""

class Func:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return f"Функция {self.name}  {(self.type)}"


class Proc:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Процедура {self.name}"


class Module:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Модуль {self.name}"


class Var:
    def __init__(self, name, type, addr):
        self.name = name
        self.type = type
        self.addr = addr

    def __str__(self):
        return f"Переменная {self.name}  {self.type} {self.addr}"


class Const:
    def __init__(self, name, val, type):
        self.name = name
        self.type = type
        self.val = val

    def __str__(self):
        return f"Константа {self.name}  {self.type} {self.val}"


class Type:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return f"Тип {self.name}  {self.type}"

