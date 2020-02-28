import sys
import telnetlib
import time
from threading import *

HOST = "10.105.247.50"
user = b'root'
password = b'lablab'

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password + b"\n")


class IntZero(Thread):
    def run(self):
        for i in range(2):
            tn.write(
                b"show controllers fia diagshell 0 \"phy xe18 TXFIR_MISC_CTL1r SDK_TX_DISABLE=1\" location 0/0/CPU0\n")
            time.sleep(1)
            tn.write(
                b"show controllers fia diagshell 0 \"phy xe18 TXFIR_MISC_CTL1r SDK_TX_DISABLE=0\" location 0/0/CPU0\n")
            time.sleep(1)
            print(i)


class IntOne(Thread):
    def run(self):
        for i in range(2):
            tn.write(b"conf t\n")
            #tn.write("show controllers fia diagshell 0 \"phy xe17 TXFIR_MISC_CTL1r SDK_TX_DISABLE=1\" location 0/0/CPU0\n")
            tn.write(b"int te0/0/0/1\n")
            tn.write(b"shut\n")
            tn.write(b"commit\n")
            time.sleep(1)
            tn.write(b"no shut\n")
            tn.write(b"commit\n")
            time.sleep(1)
            print(i)
            #tn.write("show controllers fia diagshell 0 \"phy xe17 TXFIR_MISC_CTL1r SDK_TX_DISABLE=0\" location 0/0/CPU0\n")

            print(i)
        tn.write(b"end\n")


t1 = IntZero()
t2 = IntOne()

t1.start()
time.sleep(0.2)
t2.start()

t1.join()
t2.join()

print("bye")

tn.write(b"exit\n")

print(tn.read_all())
