# module ovm
"""Виртуальная машина"""

# import numpy as np

import time

import error

STOP = -1
ADD = -2
SUB = -3
MULT = -4
DIV = -5
MOD = -6
NEG = -7
LOAD = -8
SAVE = -9
DUP = -10
DROP = -11
SWAP = -12
OVER = -13
GOTO = -14
IFLT = -15
IFLE = -16
IFGT = -17
IFGE = -18
IFEQ = -19
IFNE = -20
IN = -21
OUT = -22
LN = -23

mnemo = [
    "",
    "STOP",
    "ADD",
    "SUB",
    "MULT",
    "DIV",
    "MOD",
    "NEG",
    "LOAD",
    "SAVE",
    "DUP",
    "DROP",
    "SWAP",
    "OVER",
    "GOTO",
    "IFLT",
    "IFLE",
    "IFGT",
    "IFGE",
    "IFEQ",
    "IFNE",
    "IN",
    "OUT",
    "LN"
]

MEM_SIZE = 8 * 1024
M = [STOP] * MEM_SIZE


def printCode(PC):
    for pc in range(PC):
        if M[pc] >= 0:
            print(f"{pc}) {M[pc]}")
        else:
            print(f"{pc}) {mnemo[-M[pc]]}")


def Run():
    PC = 0
    SP = MEM_SIZE

    t1 = time.time()

    while True:
        cmd = M[PC]
        PC += 1
        if cmd >= 0:
            SP -= 1
            M[SP] = cmd
        elif cmd == ADD:
            SP += 1
            M[SP] += M[SP - 1]
        elif cmd == SUB:
            SP += 1
            M[SP] -= M[SP - 1]
        elif cmd == MULT:
            SP += 1
            M[SP] *= M[SP - 1]
        elif cmd == DIV:
            SP += 1
            M[SP] /= M[SP - 1]
        elif cmd == MOD:
            SP += 1
            M[SP] %= M[SP - 1]
        elif cmd == NEG:
            M[SP] = -M[SP]
        elif cmd == LOAD:
            M[SP] = M[M[SP]]
        elif cmd == SAVE:
            M[M[SP + 1]] = M[SP]
            SP += 2
        elif cmd == DUP:
            SP -= 1
            M[SP] = M[SP + 1]
        elif cmd == DROP:
            SP += 1
        elif cmd == SWAP:
            M[SP], M[SP + 1] = M[SP + 1], M[SP]
        elif cmd == OVER:
            SP -= 1
            M[SP] = M[SP + 2]
        elif cmd == GOTO:
            PC = M[SP]
            SP += 1
        elif cmd == IFEQ:
            if (M[SP + 2] == M[SP + 1]):
                PC = M[SP]
            SP += 3
        elif cmd == IFNE:
            if (M[SP + 2] != M[SP + 1]):
                PC = M[SP]
            SP += 3
        elif cmd == IFLE:
            if (M[SP + 2] <= M[SP + 1]):
                PC = M[SP]
            SP += 3
        elif cmd == IFLT:
            if (M[SP + 2] < M[SP + 1]):
                PC = M[SP]
            SP += 3
        elif cmd == IFGE:
            if (M[SP + 2] >= M[SP + 1]):
                PC = M[SP]
            SP += 3
        elif cmd == IFGT:
            if (M[SP + 2] > M[SP + 1]):
                PC = M[SP]
            SP += 3
        elif cmd == IN:
            SP -= 1
            try:
                M[SP] = int(input('?'))
            except:
                error.Error("Неправильный ввод")
        elif cmd == OUT:
            print(f"{M[SP + 1]:{M[SP]}}", end="")
            SP += 2
        elif cmd == LN:
            print()
        elif cmd == STOP:
            break
        else:
            error.Error("OVM: Недопустимый код операции")

    t2 = time.time()

    print(f"\nСтоп PC = {PC - 1} ({(t2 - t1):0.3} c)")
    if SP < MEM_SIZE:
        print("Код возврата", M[SP])
