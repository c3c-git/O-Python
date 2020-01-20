# Компилятор языка "O"
import time

import text
import scan
import pars
import ovm
import gen

print('Компилятор языка "O"')


def Init():
    text.Reset()
    scan.Init()


def Done():
    text.Close()


t1 = time.time()
Init()
pars.Compile()
t2 = time.time()
print(f"\nКомпиляция завершена ({(t2 - t1) * 1000:0.4} мс)")
ovm.printCode(gen.PC)
print("\nСтарт")
ovm.Run()
Done()
