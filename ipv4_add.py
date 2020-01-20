a = 0
b = 0
c = 0
# 10.a.b.c
for i in range(0, 1021):
    if i <= 255:
        c = i
    elif i > 255 and i <= 510:
        b = 1
        c = int(i) % 255
        c = i - 255
    elif i > 510 and i <= 765:
        b = 2
        c = int(i) % 510
        # c = i - 255
    elif i > 764 and i <= 1020:
        b = 3
        c = int(i) % 765
        # c = i - 255

    # print(f"10.{a}.{b}.{c}")

    # print(f"20.{b}.{c}.0/24")
j = 0
c = 0
k = 0
for i in range(1, 33):
    c = int(i % 255)
    for j in range(0, 256):
        k += 1
        # print(f"10.10.{c}.{j}")
        # print(f"{k} permit ipv4 host 10.1.{c}.{j} host 20.1.0.2")


for i in range(1, 101):
    j = hex(i).split("x")[1]
    print(f"{i} permit ipv6 host 2001:10:1::{j} host 2001:20:1::2")
# for i in range(8200, 8300):
#     print(f"{i} deny tcp host 20.0.0.2 eq {i} host 10.0.0.2 eq {i}")
