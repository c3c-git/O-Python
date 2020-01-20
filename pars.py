# module pars
"""Синтаксический анализатор"""

from enum import Enum, auto

from text import ch, nextCh
import table
import scan
from scan import Lex, lex, nextLex, lexName
import gen
from gen import Cmd as Gen
import ovm
import ovm as cm
import cat
from error import *


class Types(Enum):
    Int = auto()
    Bool = auto()


def skip(L):
    if lex() == L:
        nextLex()
    else:
        Expected(lexName(L))


def check(L):
    if lex() != L:
        Expected(lexName(L))


def fixup(A, PC: int):
    """Адресная привязка"""
    while A > 0:
        tmp = ovm.M[A - 2]
        ovm.M[A - 2] = PC
        A = tmp


def ImportName():
    check(Lex.NAME)
    if scan.name() not in {"In", "Out"}:
        cntError("Неизвестный модуль")
    table.new(cat.Module(scan.name()))
    nextLex()


def Import():
    skip(Lex.IMPORT)
    ImportName()
    while lex() == Lex.COMMA:
        nextLex()
        ImportName()
    skip(Lex.SEMI)


def ConstExpr():
    sign = -1 if lex() == Lex.MINUS else +1
    if lex() in {Lex.PLUS, Lex.MINUS}:
        nextLex()
    if lex() == Lex.NUM:
        val = sign * scan.num()
        nextLex()
    elif lex() == Lex.NAME:
        const = table.find(scan.name())
        if type(const) != cat.Const:
            Expected("константа")
        val = sign * const.val
        nextLex()
    else:
        Expected("константа")
    return val


def ConstDecl():
    while lex() == Lex.NAME:
        ident = scan.name()
        nextLex()
        skip(Lex.EQ)
        val = ConstExpr()
        table.new(cat.Const(ident, val, Types.Int))
        skip(Lex.SEMI)


def Type():
    check(Lex.NAME)
    x = table.find(scan.name())
    if type(x) != cat.Type:
        Expected("имя типа")
    nextLex()


def varDecl():
    while lex() == Lex.NAME:
        table.new(cat.Var(scan.name(), Types.Int, 0))
        nextLex()
        while lex() == Lex.COMMA:
            nextLex()
            check(Lex.NAME)
            table.new(cat.Var(scan.name(), Types.Int, 0))
            nextLex()
        skip(Lex.COLON)
        Type()
        skip(Lex.SEMI)


def DeclSeq():
    while lex() in {Lex.CONST, Lex.VAR}:
        if lex() == Lex.CONST:
            nextLex()
            ConstDecl()
        else:
            nextLex()
            varDecl()


def intExpr():
    p = loc.lexPos
    T = Expression()
    testInt(T, p)


def boolExpr():
    p = loc.lexPos
    T = Expression()
    testBool(T, p)


def Function(x: cat.Func):
    if x.name == "ABS":
        intExpr()
        Gen(cm.DUP)
        gen.Const(0)
        Gen(gen.PC + 3)
        Gen(cm.IFGE)
        Gen(cm.NEG)
    elif x.name == "MIN":
        check(Lex.NAME)
        x = table.find(scan.name())
        if type(x) != cat.Type:
            Expected("имя типа")
        nextLex()
        Gen(scan.MAXINT)
        Gen(cm.NEG)
        Gen(1)
        Gen(cm.SUB)
    elif x.name == "MAX":
        check(Lex.NAME)
        x = table.find(scan.name())
        if type(x) != cat.Type:
            Expected("имя типа")
        nextLex()
        gen.Const(scan.MAXINT)
    elif x.name == "ODD":
        intExpr()
        Gen(1)
        Gen(cm.MOD)
        Gen(0)
        Gen(cm.IFNE)
    else:
        assert False


def Factor():
    T = None
    if lex() == Lex.NUM:
        Gen(scan.num())
        nextLex()
        T = Types.Int
    elif lex() == Lex.NAME:
        x = table.find(scan.name())
        if type(x) == cat.Var:
            gen.Addr(x)
            Gen(cm.LOAD)
            nextLex()
            T = x.type
        elif type(x) == cat.Const:
            gen.Const(x.val)
            T = x.type
            nextLex()
        elif type(x) == cat.Func:
            nextLex()
            skip(Lex.LPAR)
            Function(x)
            T = x.type
            skip(Lex.RPAR)
        else:
            Expected("функция, константа или переменная")
    elif lex() == Lex.LPAR:
        nextLex()
        T = Expression()
        skip(Lex.RPAR)
    else:
        Expected("имя число или выражение в скобках")
    return T


def testInt(T, pos: int):
    if T != Types.Int:
        posExpected("выражение целого типа", pos)


def testBool(T, pos: int):
    if T != Types.Bool:
        posExpected("выражение логического типа", pos)


def Term():
    p = loc.lexPos
    T = Factor()
    while lex() in {Lex.MULT, Lex.MOD, Lex.DIV}:
        op = lex()
        testInt(T, p)
        nextLex()
        p = loc.lexPos
        Factor()
        testInt(T, p)
        if op == Lex.MULT:
            Gen(cm.MULT)
        elif op == Lex.DIV:
            Gen(cm.DIV)
        else:
            Gen(cm.MOD)

    return T


def SimpleExpression():
    if lex() in {Lex.PLUS, Lex.MINUS}:
        op = lex()
        nextLex()
        p = loc.lexPos
        T = Term()
        testInt(T, p)
        if op == Lex.MINUS:
            Gen(cm.NEG)
    else:
        p = loc.lexPos
        T = Term()

    while lex() in {Lex.PLUS, Lex.MINUS}:
        op = lex()
        testInt(T, p)
        nextLex()
        p = loc.lexPos
        T = Term()
        testInt(T, p)
        if op == Lex.PLUS:
            Gen(cm.ADD)
        else:
            Gen(cm.SUB)

    return T


def Expression():
    p = loc.lexPos
    T = SimpleExpression()
    if lex() in {Lex.EQ, Lex.NE, Lex.GE, Lex.GT, Lex.LE, Lex.LT}:
        op = lex()
        testInt(T, p)
        nextLex()
        p = loc.lexPos
        T = SimpleExpression()
        testInt(T, p)
        T = Types.Bool
        gen.Comp(op)
    return T


def Variable():
    check(Lex.NAME)
    x = table.find(scan.name())
    if type(x) == cat.Var:
        gen.Addr(x)
    else:
        Expected("переменная")
    nextLex()


def Procedure(x):
    if x.name == "HALT":
        gen.Const(ConstExpr())
        Gen(cm.STOP)
    elif x.name == "INC":
        Variable()
        Gen(cm.DUP)
        Gen(cm.LOAD)
        if lex() == Lex.COMMA:
            nextLex()
            intExpr()
        else:
            gen.Const(1)
        Gen(cm.ADD)
        Gen(cm.SAVE)
    elif x.name == "DEC":
        Variable()
        Gen(cm.DUP)
        Gen(cm.LOAD)
        if lex() == Lex.COMMA:
            nextLex()
            intExpr()
        else:
            gen.Const(1)
        Gen(cm.SUB)
        Gen(cm.SAVE)
    elif x.name == "In.Int":
        Variable()
        Gen(cm.IN)
        Gen(cm.SAVE)
    elif x.name == "Out.Int":
        intExpr()
        skip(Lex.COMMA)
        intExpr()
        Gen(cm.OUT)
    elif x.name == "Out.Ln":
        Gen(cm.LN)
    elif x.name == "In.Open":
        pass


def AssOrCall():
    check(Lex.NAME)
    x = table.find(scan.name())
    nextLex()
    if type(x) == cat.Module:
        module = x.name
        skip(Lex.DOT)
        check(Lex.NAME)
        pname = module + "." + scan.name()
        x = table.find(pname)
        if type(x) == cat.Proc:
            nextLex()
            if lex() == Lex.LPAR:
                nextLex()
                Procedure(x)
                skip(Lex.RPAR)
            else:
                Procedure(x)
        else:
            Expected("процедура")
    elif type(x) == cat.Proc:
        if lex() == Lex.LPAR:
            nextLex()
            Procedure(x)
            skip(Lex.RPAR)
        else:
            Procedure(x)
    elif type(x) == cat.Var:
        gen.Addr(x)
        skip(Lex.ASS)
        p = loc.lexPos
        T = Expression()
        if T != x.type:
            posError("Несоответствие типа", p)
        Gen(cm.SAVE)
    else:
        Expected("вызов процедуры или присваивание")


def IfStatement():
    skip(Lex.IF)
    p = loc.lexPos
    boolExpr()
    lastGOTO = 0
    condPC = gen.PC
    skip(Lex.THEN)
    StatSeq()
    while lex() == Lex.ELSIF:
        Gen(lastGOTO)
        Gen(cm.GOTO)
        lastGOTO = gen.PC
        fixup(condPC, gen.PC)
        nextLex()
        p = loc.lexPos
        boolExpr()
        skip(Lex.THEN)
        StatSeq()
    if lex() == Lex.ELSE:
        nextLex()
        Gen(lastGOTO)
        Gen(cm.GOTO)
        lastGOTO = gen.PC
        fixup(condPC, gen.PC)
        StatSeq()
    else:
        fixup(condPC, gen.PC)

    skip(Lex.END)
    fixup(lastGOTO, gen.PC)


def WhileStatement():
    whilePC = gen.PC
    skip(Lex.WHILE)
    p = loc.lexPos
    boolExpr()
    condPC = gen.PC

    skip(Lex.DO)
    StatSeq()
    skip(Lex.END)
    Gen(whilePC)
    Gen(cm.GOTO)
    fixup(condPC, gen.PC)


def Statement():
    if lex() == Lex.NAME:
        AssOrCall()
    elif lex() == Lex.IF:
        IfStatement()
    elif lex() == Lex.WHILE:
        WhileStatement()


def StatSeq():
    Statement()
    while lex() == Lex.SEMI:
        nextLex()
        Statement()


def AllocVars():
    vars = table.getVars()
    for var in vars:
        fixup(var.addr, gen.PC)
        var.addr = gen.PC
        Gen(0)


def Module():
    skip(Lex.MODULE)
    if lex() == Lex.NAME:
        modRef = table.new(cat.Module(scan.name()))
        nextLex()
    else:
        Expected("имя")
    skip(Lex.SEMI)
    L = lex()
    if lex() == Lex.IMPORT:
        Import()
    DeclSeq()
    if lex() == Lex.BEGIN:
        nextLex()
        StatSeq()
    skip(Lex.END)
    check(Lex.NAME)
    x = table.find(scan.name())
    if x != modRef:
        Expected(f"имя модуля {modRef.name}")
    nextLex()
    skip(Lex.DOT)
    Gen(cm.STOP)

    AllocVars()


def Compile():
    T = Types

    table.openScope()

    table.add(cat.Func("ABS", T.Int))
    table.add(cat.Func("MAX", T.Int))
    table.add(cat.Func("MIN", T.Int))
    table.add(cat.Func("ODD", T.Bool))
    table.add(cat.Proc("HALT"))
    table.add(cat.Proc("INC"))
    table.add(cat.Proc("DEC"))
    table.add(cat.Proc("In.Open"))
    table.add(cat.Proc("In.Int"))
    table.add(cat.Proc("Out.Int"))
    table.add(cat.Proc("Out.Ln"))
    table.add(cat.Type("INTEGER", T.Int))

    text.nextCh()
    nextLex()

    table.openScope()

    Module()

    table.closeScope()
    table.closeScope()
