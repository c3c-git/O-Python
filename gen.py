# module gen
"""Генератор кода"""

import ovm as cm
from ovm import M
from scan import Lex
import cat

PC = 0


def Cmd(cmd):
    global PC
    M[PC] = cmd
    PC += 1


def Const(c):
    Cmd(abs(c))
    if c < 0:
        Cmd(cm.NEG)


def Addr(v: cat.Var):
    Cmd(v.addr)
    v.addr = PC + 1


def Comp(op):
    Cmd(0)
    if op == Lex.EQ:
        Cmd(cm.IFNE)
    elif op == Lex.NE:
        Cmd(cm.IFEQ)
    elif op == Lex.LT:
        Cmd(cm.IFGE)
    elif op == Lex.LE:
        Cmd(cm.IFGT)
    elif op == Lex.GT:
        Cmd(cm.IFLE)
    elif op == Lex.GE:
        Cmd(cm.IFLT)
    else:
        assert False
