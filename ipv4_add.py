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
        # print(f"{k} permit ipv4 host 10.10.{c}.{j} host 20.20.0.2")
        # print(
        #     f"{k} permit tcp host 11.11.{c}.{j} lt 2001 host 21.21.0.2 neq 1023 dscp af42 nexthop1 ipv4 192.168.0.2 nexthop2 ipv4 192.168.4.2 nexthop3 ipv4 192.168.3.2"
        # )


for i in range(1, 501):
    j = hex(i).split("x")[1]
    print(f"{i} permit ipv6 host 2001:10:10::{j} host 2001:20:20::2")
    # print(
    #     f"{i} permit tcp host 2001:11:11::{j} gt 1 host 2001:21:21::2 lt 9000 nexthop1 ipv6 2001:192:168::2 nexthop2 ipv6 2001:192:168:3::2 nexthop3 ipv6 2001:192:168:1::2"
    # )
# for i in range(8200, 8300):
#     print(f"{i} deny tcp host 20.0.0.2 eq {i} host 10.0.0.2 eq {i}")
